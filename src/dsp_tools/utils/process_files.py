"""This module handles processing of files referenced in the bitstream tags of an XML file."""

import hashlib
import json
import mimetypes
import os
import pickle
import shutil
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path, PurePath
from typing import Union, Any
from uuid import UUID

import docker
from docker.models.resource import Model
from lxml import etree

from dsp_tools.models.helpers import BaseError


def process_files(
    input_dir: str,
    out_dir: str,
    xml_file: str,
    sipi_image: str = "daschswiss/sipi:3.8.1"
) -> bool:
    """
    Process the files referenced in the given XML file.

    Args:
        input_dir: path to the directory where the files should be read from
        out_dir: path to the directory where the transformed / created files should be written to
        xml_file: path to xml file containing the data
        sipi_image: the sipi image that should be used
    Returns:
        success status
    """

    input_dir, out_dir, xml_file = _check_params(input_dir, out_dir, xml_file)

    print(f"{datetime.now()}: Start Sipi container...")

    _start_sipi_container_and_mount_volumes(input_dir, out_dir, sipi_image)

    all_paths: list[Path] = _get_file_paths_from_xml(xml_file=xml_file)

    print(f"{datetime.now()}: Start local file processing...")

    start_time = datetime.now()

    with ThreadPoolExecutor() as e1:
        processing_jobs = [e1.submit(
            _process_file,
            input_file,
            input_dir,
            out_dir
        ) for input_file in all_paths]

    orig_filepath_2_uuid: list[tuple[str, str]] = []

    for processed in as_completed(processing_jobs):
        orig_filepath_2_uuid.append(processed.result())

    print("Processing files took:", datetime.now() - start_time)

    try:
        _write_result_to_pkl_file(orig_filepath_2_uuid)
    except:
        print(f"An error occurred while writing the result to the pickle file. The result was: {orig_filepath_2_uuid}")

    return True


def _write_result_to_pkl_file(result: list[tuple[str, str]]):
    filename = "file_processing_result_" + datetime.now().strftime("%m%d%Y_%H%M%S") + ".pkl"
    with open(filename, 'wb') as pkl_file:
        pickle.dump(result, pkl_file)


def _check_params(input_dir: str, out_dir: str, xml_file: str) -> tuple[Path, Path, Path]:
    input_dir = Path(input_dir)
    out_dir = Path(out_dir)
    xml_file = Path(xml_file)

    _ensure_path_exists(out_dir)

    if not input_dir.is_dir():
        raise BaseError("input_dir is not a directory")
    if not out_dir.is_dir():
        raise BaseError("out_dir is not a directory")
    if not xml_file.is_file():
        raise BaseError("xml_file is not a file")

    return input_dir, out_dir, xml_file


def _start_sipi_container_and_mount_volumes(input_dir: Path,
                                            output_dir: Path,
                                            image: str
                                            ):
    container_name = "sipi"
    volumes = [f"{input_dir.absolute()}:/sipi/processing-input",
               f"{output_dir.absolute()}:/sipi/processing-output"]
    entrypoint = ["tail", "-f", "/dev/null"]
    client = docker.from_env()

    try:
        client.containers.get(container_name)
    except docker.errors.NotFound:
        print(f"{datetime.now()}: Starting Sipi container...")
        client.containers.run(image=image, name=container_name, volumes=volumes,
                              entrypoint=entrypoint, detach=True)


def _get_file_paths_from_xml(xml_file: Path) -> list[Path]:
    """
    Parse XML file to get all file paths.

    Args:
        xml_file: path to the XML file

    Returns:
        list of all paths in the <bitstream> tags
    """
    tree: etree._ElementTree = etree.parse(xml_file)
    bitstream_paths: [Path] = []
    for x in tree.iter():
        if x.text and etree.QName(x).localname.endswith("bitstream"):
            bitstream_paths.append(Path(x.text))

    return bitstream_paths


def _get_sipi_container() -> Union[Model, Any]:
    """
    Finds the locally running Sipi container (searches for container name "sipi") and returns its Model

    Returns:
        the reference to the Sipi container
    """
    docker_client = docker.from_env()
    containers = docker_client.containers.list()
    sipi_container = None
    for c in containers:
        if c.name == "sipi":
            return c
    if not sipi_container:
        raise BaseError("Couldn't find a running Sipi container.")


def _compute_sha256(file: Path):
    """
    Calculates SHA256 checksum of a file

    Args:
        file: path of the file

    Returns:
        the checksum
    """
    hash_sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def _convert_file_with_sipi(in_file, out_file_local_path) -> bool:
    """
    Converts a file by calling a locally running Sipi container.

    Args:
        in_file: path to input file, has to be relative to the Sipi executable inside the container
        out_file_local_path: path to output file, has to be relative to the Sipi executable inside the container
    """
    input_dir_sipi = Path("processing-input")
    out_dir_sipi = Path("processing-output")
    in_file_sipi_path = input_dir_sipi / in_file
    out_file_sipi_path = out_dir_sipi / os.path.basename(out_file_local_path)

    sipi_container = _get_sipi_container()
    # result = sipi_container.exec_run(f"/sipi/sipi --topleft {in_file_sipi_path} {out_file_sipi_path}")
    result = sipi_container.exec_run(f"/sipi/sipi {in_file_sipi_path} {out_file_sipi_path}")
    if result.exit_code != 0:
        print("Sipi image conversion failed:", result)
        return False
    return True


def _create_orig_file(in_file, file_name, out_dir):
    """
    Creates the .orig file expected by the API.

    Args:
        in_file: the input file from which the .orig should be crated
        file_name: the filename which should be used for the .orig file
        out_dir: the directory which the .orig file should be written to
    """
    orig_ext = PurePath(in_file).suffix
    orig_file_basename = f"{file_name}{orig_ext}.orig"
    orig_file_full_path = PurePath(out_dir, orig_file_basename)
    shutil.copyfile(in_file, orig_file_full_path)


def _get_video_metadata_with_ffprobe(file_path):
    command_array = ["ffprobe",
                     "-v",
                     "error",
                     "-select_streams", "v:0",
                     "-show_entries",
                     "stream=width,height,bit_rate,duration,nb_frames,r_frame_rate",
                     "-print_format", "json",
                     "-i",
                     file_path]
    result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    video_metadata = json.loads(result.stdout)['streams'][0]  # get first stream
    return video_metadata


def _create_sidecar_file(orig_file: Path,
                         converted_file: Path,
                         out_dir: Path,
                         file_category: str):
    if file_category not in ("IMAGE", "VIDEO", "OTHER"):
        raise BaseError(f"Unexpected file category {file_category}")

    checksum_original = _compute_sha256(orig_file)
    checksum_derivative = _compute_sha256(converted_file)

    original_filename = PurePath(orig_file).name
    internal_filename = PurePath(converted_file).name
    random_part_of_filename = PurePath(converted_file).stem
    original_extension = PurePath(orig_file).suffix
    original_internal_filename = f"{random_part_of_filename}{original_extension}.orig"
    sidecar_dict = {"originalFilename": original_filename,
                    "checksumOriginal": checksum_original,
                    "checksumDerivative": checksum_derivative,
                    "internalFilename": internal_filename,
                    "originalInternalFilename": original_internal_filename}

    # add video specific metadata to sidecar file
    if file_category == "VIDEO":
        video_metadata = _get_video_metadata_with_ffprobe(converted_file)
        sidecar_dict["width"] = video_metadata["width"]
        sidecar_dict["height"] = video_metadata["height"]
        sidecar_dict["duration"] = float(video_metadata["duration"])
        nb_frames = int(video_metadata["nb_frames"])
        duration = float(video_metadata["duration"])
        fps = nb_frames / duration
        sidecar_dict["fps"] = fps

    sidecar_file_basename = f"{random_part_of_filename}.info"
    sidecar_file = PurePath(out_dir, sidecar_file_basename)

    with open(sidecar_file, "w") as f:
        sidecar_json = json.dumps(sidecar_dict, indent=4)
        f.write(sidecar_json)


def _get_file_category_from_mimetype(file: Path):
    image_jp2 = "image/jp2"
    image_jpx = "image/jpx"
    image_tiff = "image/tiff"
    image_png = "image/png"
    image_jpg = "image/jpeg"
    application_xml = "application/xml"
    text_xml = "text/xml"
    text_plain = "text/plain"
    text_csv = "text/csv"
    audio_mp3 = "audio/mpeg"
    audio_wav = "audio/wav"
    audio_x_wav = "audio/x-wav"
    audio_vnd_wave = "audio/vnd.wave"
    application_csv = "application/csv"
    application_pdf = "application/pdf"
    application_doc = "application/msword"
    application_docx = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    application_xls = "application/vnd.ms-excel"
    application_xlsx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    application_ppt = "application/vnd.ms-powerpoint"
    application_pptx = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    application_zip = "application/zip"
    application_tar = "application/x-tar"
    application_gzip = "application/gzip"
    application_7_z = "application/x-7z-compressed"
    application_tgz = "application/x-compress"
    application_z = "application/x-compress"
    video_mp4 = "video/mp4"

    image_mimetypes = [image_jp2,
                       image_jpg,
                       image_jpx,
                       image_png,
                       image_tiff]
    video_mimetypes = [video_mp4]
    other_mimetypes = [audio_mp3,
                       audio_vnd_wave,
                       audio_wav,
                       audio_x_wav,
                       application_csv,
                       application_xml,
                       text_csv,
                       text_plain,
                       text_xml,
                       application_doc,
                       application_docx,
                       application_pdf,
                       application_ppt,
                       application_pptx,
                       application_xls,
                       application_xlsx,
                       application_7_z,
                       application_gzip,
                       application_tar,
                       application_tgz,
                       application_z,
                       application_zip]

    mimetype, _ = mimetypes.guess_type(file)

    if mimetype in video_mimetypes:
        category = "VIDEO"
    elif mimetype in image_mimetypes:
        category = "IMAGE"
    elif mimetype in other_mimetypes:
        category = "OTHER"
    else:
        category = None
    return category


def _extract_key_frames(file: Path):
    result = subprocess.call(['sh', 'export-moving-image-frames.sh', '-i', file])
    if result != 0:
        raise BaseError(f"Something happened while extracting frames from: {file}")


def _create_random_uuid() -> UUID:
    return uuid.uuid4()


def _ensure_path_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _process_file(
    in_file: Path,
    input_dir: Path,
    out_dir: Path
) -> tuple[Path, Path]:
    """
    Creates all expected derivative files and saves the output in the given output directory.

    In case of an image: creates the JP2000 derivative, the .orig file and the sidecar file.
    In case of a video: creates the keyframe images, the .orig file and the sidecar file.
    In all other cases: creates the .orig file and the sidecar file.

    Args:
        in_file: path to file
        out_dir: target location of created files

    Returns:
        tuple consisting of the original path and the internal filename
    """
    # ensure that input file exists
    if not in_file.is_file():
        print(f"{datetime.now()}: '{in_file}' does not exist. Skipping...")
        return in_file, in_file

    # get random UUID for internal file handling
    internal_filename = _create_random_uuid()

    # create .orig file
    _create_orig_file(in_file, internal_filename, out_dir)

    # convert file (create derivative) and create sidecar file based on category (image, video or other)
    file_category = _get_file_category_from_mimetype(in_file)
    if file_category == "OTHER":
        ext = PurePath(in_file).suffix
        converted_file_basename = str(internal_filename) + ext
        converted_file_full_path = out_dir / converted_file_basename
        shutil.copyfile(in_file, converted_file_full_path)
        _create_sidecar_file(in_file, converted_file_full_path, out_dir, file_category)
    elif file_category == "IMAGE":
        ext = ".jp2"
        converted_file_basename = str(internal_filename) + ext
        converted_file_full_path = out_dir / converted_file_basename
        in_file_sipi_path = os.path.relpath(in_file, input_dir)
        _convert_file_with_sipi(in_file_sipi_path, converted_file_full_path)
        _create_sidecar_file(in_file, converted_file_full_path, out_dir, file_category)
    elif file_category == "VIDEO":
        ext = PurePath(in_file).suffix
        converted_file_basename = str(internal_filename) + ext
        converted_file_full_path = out_dir / converted_file_basename
        shutil.copyfile(in_file, converted_file_full_path)
        _extract_key_frames(converted_file_full_path)
        _create_sidecar_file(in_file, converted_file_full_path, out_dir, file_category)
    else:
        raise BaseError(f"Unexpected file category: {file_category}")

    return in_file, converted_file_full_path
