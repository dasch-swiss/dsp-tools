"""This module handles processing of files referenced in the bitstream tags of an XML file."""

import hashlib
import importlib
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
from typing import Any, Optional, Union
from uuid import UUID

import docker
from docker.models.resource import Model
from lxml import etree

from dsp_tools.models.helpers import BaseError

global sipi_container


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

    param_check_result = _check_params(input_dir, out_dir, xml_file)
    if param_check_result:
        input_dir, out_dir, xml_file = param_check_result
    else:
        raise BaseError("Error reading the input parameters. Please check them.")

    global sipi_container
    sipi_container = _start_sipi_container(input_dir, out_dir, sipi_image)

    all_paths: list[Path] = _get_file_paths_from_xml(xml_file)

    print(f"{datetime.now()}: Start local file processing...")
    start_time = datetime.now()
    result: list[tuple[Path, Path]] = _process_files_in_parallel(all_paths, input_dir, out_dir)
    print(f"{datetime.now()}: Processing files took: {datetime.now() - start_time}")

    _print_files_with_errors(result)

    if not _write_result_to_pkl_file(result):
        print(f"An error occurred while writing the result to the pickle file. The result was: {result}")

    return True


def _print_files_with_errors(result: list[tuple[Path, Path]]) -> None:
    for input_file, output_file in result:
        if input_file == output_file:
            print(f"The following file could not be processed: {input_file}")


def _process_files_in_parallel(paths: list[Path], input_dir: Path, out_dir: Path) -> list[tuple[Path, Path]]:
    """
    Creates a thread pool and executes the file processing in parallel.

    Args:
        paths: a list of all paths to the files that should be processed
        input_dir: the root directory of the input files
        out_dir: the directory where the processed files should be written to

    Returns:
        a list of tuples with the original file path and the path to the processed file
    """
    with ThreadPoolExecutor() as pool:
        processing_jobs = [pool.submit(
            _process_file,
            input_file,
            input_dir,
            out_dir
        ) for input_file in paths]

    orig_filepath_2_uuid: list[tuple[Path, Path]] = []

    for processed in as_completed(processing_jobs):
        orig_filepath_2_uuid.append(processed.result())

    return orig_filepath_2_uuid


def _write_result_to_pkl_file(result: list[tuple[Path, Path]]) -> bool:
    """
    Writes the processing result to a pickle file.

    Args:
        result: the result of the file processing

    Returns:
        true if successful, false otherwise
    """
    filename = "file_processing_result_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".pkl"
    try:
        with open(filename, 'wb') as pkl_file:
            pickle.dump(result, pkl_file)
        print(f"{datetime.now()}: The result was written to: {filename}")
        return True
    except:
        return False


def _check_params(input_dir: str, out_dir: str, xml_file: str) -> Optional[tuple[Path, Path, Path]]:
    """
    Checks the input parameters provided by the user and transforms them into the expected types.

    Args:
        input_dir: the root directory of the input files
        out_dir: the output directory where the created files should be written to
        xml_file: the XML file the paths are extracted from

    Returns:
        A tuple with the Path objects of the input strings
    """
    input_dir = Path(input_dir)
    out_dir = Path(out_dir)
    xml_file = Path(xml_file)

    if not _ensure_path_exists(out_dir):
        return None

    if not input_dir.is_dir():
        print("input_dir is not a directory")
        return None
    if not out_dir.is_dir():
        print("out_dir is not a directory")
        return None
    if not xml_file.is_file():
        print("xml_file is not a file")
        return None

    return input_dir, out_dir, xml_file


def _start_sipi_container(input_dir: Path, output_dir: Path, image: str) -> Optional[Model]:
    """
    Creates and runs the Sipi container. If it exists already, it checks if it is running. It starts it if not.

    Args:
        input_dir: the root directory of the input files, mounts it into the container
        output_dir: the output directory where the processed files should be written to, mounts it into the container
        image: the image which the container should be creted from

    Returns:
        the reference to the running container
    """
    _start_sipi_container_and_mount_volumes(input_dir, output_dir, image)
    return _get_sipi_container()


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


def _start_sipi_container_and_mount_volumes(input_dir: Path,
                                            output_dir: Path,
                                            image: str) -> None:
    """
    Creates and starts a Sipi container from the provided image. Checks first if it already exists and if yes, if it is
    already running.

    Args:
        input_dir: the root directory of the images that should be processed, is mounted into the container
        output_dir: the output directory where the processed files should be written to, is mounted into the container
        image: the image which the container should be created from
    """
    container_name = "sipi"
    volumes = [f"{input_dir.absolute()}:/sipi/processing-input",
               f"{output_dir.absolute()}:/sipi/processing-output"]
    entrypoint = ["tail", "-f", "/dev/null"]
    client = docker.from_env()

    try:
        container = client.containers.get(container_name)
        if not container.attrs["State"]["Running"]:
            container.restart()
            print(f"{datetime.now()}: Started existing Sipi container '{container_name}'.")
        else:
            print(f"{datetime.now()}: Found running Sipi container '{container_name}'.")
    except docker.errors.NotFound:
        client.containers.run(image=image, name=container_name, volumes=volumes, entrypoint=entrypoint, detach=True)
        print(f"{datetime.now()}: Created and started Sipi container '{container_name}'.")


def _get_sipi_container() -> Union[Model, Any, None]:
    """
    Finds the locally running Sipi container (searches for container name "sipi")

    Returns:
        the reference to the Sipi container
    """
    docker_client = docker.from_env()
    containers = docker_client.containers.list()
    sipi_c = None
    for c in containers:
        if c.name == "sipi":
            return c
    if not sipi_c:
        print("Couldn't find a running Sipi container.")
        return None


def _compute_sha256(file: Path) -> Optional[str]:
    """
    Calculates SHA256 checksum of a file

    Args:
        file: path of the file

    Returns:
        the calculated checksum
    """
    if not file.is_file():
        print(f"Couldn't calculate checksum for {file}")
        return None
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

    if not sipi_container:
        return False
    # result = sipi_container.exec_run(f"/sipi/sipi --topleft {in_file_sipi_path} {out_file_sipi_path}")
    result = sipi_container.exec_run(f"/sipi/sipi {in_file_sipi_path} {out_file_sipi_path}")
    if result.exit_code != 0:
        print("Sipi image conversion failed:", result)
        return False
    return True


def _create_orig_file(in_file, file_name, out_dir) -> bool:
    """
    Creates the .orig file expected by the API.

    Args:
        in_file: the input file from which the .orig should be created
        file_name: the filename which should be used for the .orig file
        out_dir: the directory where the .orig file should be written to
    """
    orig_ext = PurePath(in_file).suffix
    orig_file_basename = f"{file_name}{orig_ext}.orig"
    orig_file_full_path = PurePath(out_dir, orig_file_basename)
    try:
        shutil.copyfile(in_file, orig_file_full_path)
        return True
    except:
        return False


def _get_video_metadata_with_ffprobe(file_path: Path):
    """
    Gets video metadata by running ffprobe

    Args:
        file_path: path to the file which the metadata should be extracted from

    Returns:
        the metadata object as json
    """
    command_array = ["ffprobe",
                     "-v",
                     "error",
                     "-select_streams", "v:0",
                     "-show_entries",
                     "stream=width,height,bit_rate,duration,nb_frames,r_frame_rate",
                     "-print_format", "json",
                     "-i",
                     file_path]
    try:
        result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except:
        return None
    video_metadata = json.loads(result.stdout)['streams'][0]  # get first stream
    return video_metadata


def _create_sidecar_file(orig_file: Path,
                         converted_file: Path,
                         out_dir: Path,
                         file_category: str) -> bool:
    """
    Creates the sidecar file for a given file. Depending on the file category, it adds category specific metadata.

    Args:
        orig_file: path to the original file
        converted_file: path to the converted file
        out_dir: output directory where the sidecar file should be written to
        file_category: the file category, either IMAGE, VIDEO or OTHER

    Returns:
        true if successful, false otherwise
    """
    if file_category not in ("IMAGE", "VIDEO", "OTHER"):
        print(f"Unexpected file category {file_category}")
        return False

    checksum_original = _compute_sha256(orig_file)
    if not checksum_original:
        return False

    checksum_derivative = _compute_sha256(converted_file)
    if not checksum_derivative:
        return False

    original_filename = PurePath(orig_file).name
    internal_filename = PurePath(converted_file).name
    random_part_of_filename = PurePath(converted_file).stem
    original_extension = PurePath(orig_file).suffix
    original_internal_filename = f"{random_part_of_filename}{original_extension}.orig"
    sidecar_dict: dict[str, Union[str, float]] = {"originalFilename": original_filename,
                                                  "checksumOriginal": checksum_original,
                                                  "checksumDerivative": checksum_derivative,
                                                  "internalFilename": internal_filename,
                                                  "originalInternalFilename": original_internal_filename}

    # add video specific metadata to sidecar file
    if file_category == "VIDEO":
        video_metadata = _get_video_metadata_with_ffprobe(converted_file)
        if not video_metadata:
            return False
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

    return True


def _get_file_category_from_mimetype(file: Path) -> Optional[str]:
    """
    Gets the file category of a file according to its mimetype.

    Args:
        file: file which the category should be got from

    Returns:
        the file category, either IMAGE, VIDEO or OTHER (or None)
    """
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


def _extract_key_frames(file: Path) -> bool:
    """
    Extracts the key frames of a video file and writes them to disk.

    Args:
        file: the video file which the key frames should be extracted from

    Returns:
        true if successful, false otherwise
    """
    export_moving_image_frames_script = importlib.resources.files("dsp_tools").joinpath(
        "resources/export-moving-image-frames.sh")
    result = subprocess.call(["sh", f"{export_moving_image_frames_script}", "-i", f"{file}"])
    if result != 0:
        return False
    else:
        return True


def _create_random_uuid() -> UUID:
    return uuid.uuid4()


def _ensure_path_exists(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except:
        return False


def _process_file(
    in_file: Path,
    input_dir: Path,
    out_dir: Path
) -> tuple[Path, Path]:
    """
    Creates all expected derivative files and writes the output into the provided output directory.

    In case of an image: creates the JP2000 derivative, the .orig file and the sidecar file.
    In case of a video: creates a folder with the keyframe images, the .orig file and the sidecar file.
    In all other cases: creates the .orig file and the sidecar file.

    Args:
        in_file: path to input file that should be processed
        input_dir: root directory of the input files
        out_dir: target location where the crated files are written to, if the directory doesn't exist, it is created

    Returns:
        tuple consisting of the original path and the internal filename, if there was an error, a tuple with twice the
        original path is returned
    """
    # ensure that input file exists
    if not in_file.is_file():
        print(f"{datetime.now()}: '{in_file}' does not exist. Skipping...")
        return in_file, in_file

    # get random UUID for internal file handling
    internal_filename = str(_create_random_uuid())

    # create .orig file
    if not _create_orig_file(in_file, internal_filename, out_dir):
        print(f"Couldn't create .orig file for {in_file}")
        return in_file, in_file

    # convert file (create derivative) and create sidecar file based on category (image, video or other)
    file_category = _get_file_category_from_mimetype(in_file)
    if not file_category:
        print(f"Couldn't get category for {in_file}")
        return in_file, in_file

    if file_category == "OTHER":
        result = _process_other_file(in_file, internal_filename, out_dir)
    elif file_category == "IMAGE":
        result = _process_image_file(in_file, internal_filename, out_dir, input_dir)
    elif file_category == "VIDEO":
        result = _process_video_file(in_file, internal_filename, out_dir)
    else:
        print(f"Unexpected file category: {file_category}")
        return in_file, in_file

    return result


def _get_path_for_converted_file(ext: str, internal_filename, out_dir) -> Path:
    """
    Creates the path for the converted file

    Args:
        ext: the file extension for the converted file
        internal_filename: the string that should be used for the internal filename
        out_dir: the output directory where the converted file should be written to

    Returns:
        the path to the converted file
    """
    converted_file_basename = internal_filename + ext
    return out_dir / converted_file_basename


def _process_other_file(in_file: Path, internal_filename: str, out_dir: Path) -> tuple[Path, Path]:
    """
    Processes a file of file category OTHER

    Args:
        in_file: the input file that should be processed
        internal_filename: the internal filename that should be used for the output file
        out_dir: the output directory where the processed file should be written to

    Returns:
        a tuple of the original file path and the path to the processed file
    """
    converted_file_full_path = _get_path_for_converted_file(PurePath(in_file).suffix, internal_filename, out_dir)
    try:
        shutil.copyfile(in_file, converted_file_full_path)
    except:
        print(f"Couldn't process file of category OTHER: {in_file}")
        return in_file, in_file
    if not _create_sidecar_file(in_file, converted_file_full_path, out_dir, "OTHER"):
        print(f"Couldn't create sidecar file for: {in_file}")
        return in_file, in_file
    return in_file, converted_file_full_path


def _process_image_file(in_file: Path, internal_filename: str, out_dir: Path, input_dir: Path) -> tuple[Path, Path]:
    """
    Processes a file of file category IMAGE

    Args:
        in_file: the input file that should be processed
        internal_filename: the internal filename that should be used for the output file
        out_dir: the output directory where the processed file should be written to

    Returns:
        a tuple of the original file path and the path to the processed file
    """
    converted_file_full_path = _get_path_for_converted_file(".jp2", internal_filename, out_dir)
    in_file_sipi_path = os.path.relpath(in_file, input_dir)
    sipi_result = _convert_file_with_sipi(in_file_sipi_path, converted_file_full_path)
    if not sipi_result:
        print(f"Couldn't process file of category IMAGE: {in_file}")
        return in_file, in_file
    if not _create_sidecar_file(in_file, converted_file_full_path, out_dir, "IMAGE"):
        print(f"Couldn't create sidecar file for: {in_file}")
        return in_file, in_file
    return in_file, converted_file_full_path


def _process_video_file(in_file: Path, internal_filename: str, out_dir: Path) -> tuple[Path, Path]:
    """
    Processes a file of file category VIDEO

    Args:
        in_file: the input file that should be processed
        internal_filename: the internal filename that should be used for the output file
        out_dir: the output directory where the processed file should be written to

    Returns:
        a tuple of the original file path and the path to the processed file
    """
    converted_file_full_path = _get_path_for_converted_file(PurePath(in_file).suffix, internal_filename, out_dir)
    try:
        shutil.copyfile(in_file, converted_file_full_path)
    except:
        print(f"Couldn't process file of category VIDEO: {in_file}")
        return in_file, in_file
    key_frames_result = _extract_key_frames(converted_file_full_path)
    if not key_frames_result:
        print(f"Couldn't process file of category VIDEO: {in_file}")
        return in_file, in_file
    if not _create_sidecar_file(in_file, converted_file_full_path, out_dir, "VIDEO"):
        print(f"Couldn't create sidecar file for: {in_file}")
        return in_file, in_file
    return in_file, converted_file_full_path
