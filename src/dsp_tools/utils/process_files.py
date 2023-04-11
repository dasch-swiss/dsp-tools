import glob
import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path, PurePath
from typing import Union, Any

import docker
import regex
import requests
from docker.models.resource import Model
from lxml import etree

from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import BaseError

tmp_location = Path.home() / Path(".dsp-tools")
tmp_location.mkdir(exist_ok=True)

extensions: dict[str, list[str]] = dict()
extensions["image"] = [".jpg", ".jpeg", ".tif", ".tiff", ".jp2", ".png"]
extensions["video"] = [".mp4"]
extensions["archive"] = [".7z", ".gz", ".gzip", ".tar", ".tar.gz", ".tgz", ".z", ".zip"]
extensions["text"] = [".csv", ".txt", ".xml", ".xsd", ".xsl"]
extensions["document"] = [".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx"]
extensions["audio"] = [".mp3", ".wav"]
all_extensions: list[str] = list()
[all_extensions.extend(ext) for ext in extensions.values()]
extension2restype = dict()
for ext in all_extensions:
    if ext in extensions.get("image", []):
        restype = ":ImageThing"
    elif ext in extensions.get("video", []):
        restype = ":MovieThing"
    elif ext in extensions.get("archive", []):
        restype = ":ZipThing"
    elif ext in extensions.get("text", []):
        restype = ":TextThing"
    elif ext in extensions.get("document", []):
        restype = ":DocumentThing"
    elif ext in extensions.get("audio", []):
        restype = ":AudioThing"
    else:
        raise BaseError("Invalid extension")
    extension2restype[ext] = restype



def __upload_derivative(
    sipi_processed_path: str,
    orig_file: str,
    internal_filename: str,
    remote_sipi_server: str,
    con: Connection
) -> tuple[int, str]:
    upload_candidates: list[str] = []
    upload_candidates.extend(glob.glob(f"{Path(sipi_processed_path)}/{Path(internal_filename).stem}/**/*.*"))
    upload_candidates.extend(glob.glob(f"{Path(sipi_processed_path)}/{Path(internal_filename).stem}*.*"))

    orig_file_path = Path(orig_file)
    min_num_of_candidates = 5 if orig_file_path.suffix == ".mp4" else 3
    if len(upload_candidates) < min_num_of_candidates:
        raise BaseError(
            f"SIPI created the following files for {orig_file_path}, but more were expected: {upload_candidates}")

    for candidate in upload_candidates:
        with open(candidate, "rb") as bitstream:
            response_upload = requests.post(
                url=f"{regex.sub(r'/$', '', remote_sipi_server)}/upload_without_processing?token={con.get_token()}",
                files={"file": bitstream}
            )
        if not response_upload.json().get("uploadedFiles"):
            raise BaseError(
                f"File {candidate} ({orig_file_path!s}) could not be uploaded. The API response was: {response_upload.text}")

    print(f" - Uploaded {len(upload_candidates)} files for {orig_file}")
    return len(upload_candidates), str(orig_file_path)


def process_files(
    out_dir: str,
    xml_file: str
) -> bool:
    """
    Process the files referenced in the given XML file.

    Args:
        out_dir: path to the directory where the transformed / created files should be written to
        xml_file: path to xml file containing the data
    Returns:
        success status
    """
    start_time = datetime.now()

    all_paths = _get_file_paths_from_xml(xml_file=Path(xml_file))

    print(f"{datetime.now()}: Start local file processing...")

    orig_filepath_2_uuid: dict[str, str] = dict()

    # create processing thread pool
    with ThreadPoolExecutor() as e1:
        processing_jobs = [e1.submit(
            _process_file,
            Path(orig_file),
            Path(out_dir)
        ) for orig_file in all_paths]

    result = []
    for processed in as_completed(processing_jobs):
        result.append(processed.result())
    print(result)
    print("TIME PROCESSING FILES:", datetime.now() - start_time)
    # print(f"{datetime.now()}: Start uploading files...")
    # with ThreadPoolExecutor(uploading_threads, "upload") as e2:
    #     uploading_jobs = []
    #     for processed in as_completed(processing_jobs):
    #         try:
    #             orig_file, internal_filename = processed.result()
    #             orig_filepath_2_uuid[orig_file] = str(internal_filename)
    #             uploading_jobs.append(
    #                 e2.submit(
    #                     __upload_derivative,
    #                     sipi_processed_path,
    #                     orig_file,
    #                     str(internal_filename),
    #                     remote_sipi_server,
    #                     con
    #                 )
    #             )
    #         except Exception as ex:
    #             print(f"processing generated an exception: {ex}")
    #         else:
    #             print(f" - Successfully preprocessed {orig_file} with internal filename: {internal_filename}")
    #
    # for uploaded in as_completed(uploading_jobs):
    #     try:
    #         uploaded.result()
    #     except Exception as ex:
    #         print(f"upload generated an exception: {ex}")

    # end_multithreading_time = datetime.now()
    # multithreading_duration = end_multithreading_time - start_multithreading_time
    # print(
    #     f"Time of multithreading (with {processing_threads} threads for preprocessing and {uploading_threads} threads for uploading): {multithreading_duration.seconds} seconds")
    #
    # for tag in xml_file_tree.iter():
    #     if tag.text in orig_filepath_2_uuid:
    #         tag.text = orig_filepath_2_uuid[tag.text]
    #
    # print("Preprocessing successfully finished! Start with regular xml upload...")
    #
    # xml_upload(
    #     input_file=xml_file_tree,
    #     server=remote_dsp_server,
    #     user=user,
    #     password=password,
    #     imgdir=".",
    #     sipi=remote_sipi_server,
    #     verbose=verbose,
    #     incremental=incremental,
    #     save_metrics=False,
    #     preprocessing_done=True
    # )
    #
    # duration = datetime.now() - start_time
    # print(f"Total time of enhanced xmlupload: {duration.seconds} seconds")
    # print(f"Time of multithreading: {multithreading_duration.seconds} seconds")
    #
    # for filename in os.listdir(sipi_processed_path):
    #     file_path = os.path.join(sipi_processed_path, filename)
    #     try:
    #         if os.path.isfile(file_path) or os.path.islink(file_path):
    #             os.unlink(file_path)
    #         elif os.path.isdir(file_path):
    #             shutil.rmtree(file_path)
    #     except Exception as e:
    #         print("Failed to delete %s. Reason: %s" % (file_path, e))

    return True


def _get_file_paths_from_xml(xml_file: Path) -> list[str]:
    """
    Parse XML file to get all file paths.

    Args:
        xml_file: path to the XML file

    Returns:
        list of all paths in the <bitstream> tags
    """
    tree: etree._ElementTree = etree.parse(xml_file)
    bitstream_paths = [x.text for x in tree.iter()
                       if etree.QName(x).localname.endswith("bitstream") and x.text is not None]
    return bitstream_paths


def get_sipi_container() -> Union[Model, Any]:
    """
    Checks the locally running containers and returns the Sipi container

    Returns:
        the sipi container
    """
    docker_client = docker.from_env()
    containers = docker_client.containers.list()
    for c in containers:
        if "sipi" in c.name:
            return c


def compute_sha256(file: Path):
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


def convert_file_with_sipi(in_file_local_path, out_file_local_path) -> bool:
    """
    Converts a file by calling a locally running Sipi container

    Args:
        in_file_local_path: input file
        out_file_local_path: output file
    """
    mounted_path_on_sipi = "images/tmp/"
    out_dir_sipi = "processed/"
    in_file_sipi_path = mounted_path_on_sipi + os.path.basename(in_file_local_path)  # images/tmp/test.tif
    out_file_sipi_path = mounted_path_on_sipi + out_dir_sipi + os.path.basename(
        out_file_local_path)  # images/tmp/processed/76c99684-354f-4e8c-9c20-2b25901a1862.jp2
    sipi_container = get_sipi_container()
    # result = sipi_container.exec_run(f"/sipi/sipi --topleft {in_file_sipi_path} {out_file_sipi_path}")
    result = sipi_container.exec_run(f"/sipi/sipi {in_file_sipi_path} {out_file_sipi_path}")
    if result.exit_code != 0:
        print("Sipi image conversion failed:", result)
        return False
    return True


def _create_orig_file(in_file, random_file_name, out_dir):
    """
    Creates the .orig file expected by the API.

    Args:
        in_file ():
        random_file_name ():
        out_dir ():
    """
    orig_ext = PurePath(in_file).suffix  # .tif
    orig_file_basename = f"{random_file_name}{orig_ext}.orig"
    orig_file_full_path = PurePath(out_dir, orig_file_basename)
    shutil.copyfile(in_file, orig_file_full_path)


def get_video_metadata_with_ffprobe(file_path):
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


def create_sidecar_file(
    orig_file: Path,
    converted_file: Path,
    out_dir: Path,
    file_category: str):
    if file_category not in ("IMAGE", "VIDEO", "OTHER"):
        raise BaseError(f"Unexpected file category {file_category}")

    original_filename = PurePath(orig_file).name  # test.tif

    checksum_original = compute_sha256(orig_file)
    checksum_derivative = compute_sha256(converted_file)

    internal_filename = PurePath(converted_file).name
    random_part_of_filename = PurePath(converted_file).stem
    original_extension = PurePath(orig_file).suffix
    original_internal_filename = f"{random_part_of_filename}{original_extension}.orig"
    sidecar_dict = {"originalFilename": original_filename,
                    "checksumOriginal": checksum_original,
                    "checksumDerivative": checksum_derivative,
                    "internalFilename": internal_filename,
                    "originalInternalFilename": original_internal_filename}

    if file_category == "VIDEO":
        video_metadata = get_video_metadata_with_ffprobe(converted_file)
        sidecar_dict["width"] = video_metadata["width"]
        sidecar_dict["height"] = video_metadata["height"]
        sidecar_dict["duration"] = float(video_metadata["duration"])
        nb_frames = int(video_metadata["nb_frames"])
        duration = float(video_metadata["duration"])
        fps = nb_frames / duration
        sidecar_dict["fps"] = fps

    sidecar_json = json.dumps(sidecar_dict, indent=4)

    sidecar_file_basename = f"{random_part_of_filename}.info"
    sidecar_file = PurePath(out_dir, sidecar_file_basename)

    with open(sidecar_file, "w") as f:
        f.write(sidecar_json)


def get_file_category(file: Path):
    IMAGE_JP2 = "image/jp2"
    IMAGE_JPX = "image/jpx"
    IMAGE_TIFF = "image/tiff"
    IMAGE_PNG = "image/png"
    IMAGE_JPG = "image/jpeg"
    APPLICATION_XML = "application/xml"
    TEXT_XML = "text/xml"
    TEXT_PLAIN = "text/plain"
    TEXT_CSV = "text/csv"
    AUDIO_MP3 = "audio/mpeg"
    AUDIO_WAV = "audio/wav"
    AUDIO_X_WAV = "audio/x-wav"
    AUDIO_VND_WAVE = "audio/vnd.wave"
    APPLICATION_CSV = "application/csv"
    APPLICATION_PDF = "application/pdf"
    APPLICATION_DOC = "application/msword"
    APPLICATION_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    APPLICATION_XLS = "application/vnd.ms-excel"
    APPLICATION_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    APPLICATION_PPT = "application/vnd.ms-powerpoint"
    APPLICATION_PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    APPLICATION_ZIP = "application/zip"
    APPLICATION_TAR = "application/x-tar"
    APPLICATION_GZIP = "application/gzip"
    APPLICATION_7Z = "application/x-7z-compressed"
    APPLICATION_TGZ = "application/x-compress"
    APPLICATION_Z = "application/x-compress"
    VIDEO_MP4 = "video/mp4"

    image_mimetypes = [IMAGE_JP2,
                       IMAGE_JPG,
                       IMAGE_JPX,
                       IMAGE_PNG,
                       IMAGE_TIFF]
    video_mimetypes = [VIDEO_MP4]
    other_mimetypes = [AUDIO_MP3,
                       AUDIO_VND_WAVE,
                       AUDIO_WAV,
                       AUDIO_X_WAV,
                       APPLICATION_CSV,
                       APPLICATION_XML,
                       TEXT_CSV,
                       TEXT_PLAIN,
                       TEXT_XML,
                       APPLICATION_DOC,
                       APPLICATION_DOCX,
                       APPLICATION_PDF,
                       APPLICATION_PPT,
                       APPLICATION_PPTX,
                       APPLICATION_XLS,
                       APPLICATION_XLSX,
                       APPLICATION_7Z,
                       APPLICATION_GZIP,
                       APPLICATION_TAR,
                       APPLICATION_TGZ,
                       APPLICATION_Z,
                       APPLICATION_ZIP
                       ]

    # image_extensions = []
    # video_extensions = ["mp4"]
    # other_extensions = ["mp3", "wav", "csv",
    #                     "odd", "rng", "txt",
    #                     "xml", "xsd", "xsl", "doc",
    #                     "docx", "pdf", "ppt", "pptx",
    #                     "xls", "xlsx", "7z", "gz",
    #                     "gzip", "tar", "tgz", "z", "zip"]

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


def extract_key_frames(file: Path):
    result = subprocess.call(['sh', '/Users/irina/GitHub/dsp-tools/export-moving-image-frames.sh', '-i', file])
    if result != 0:
        raise BaseError(f"Something happened while extracting frames from: {file}")


def _create_random_uuid() -> uuid.UUID:
    return uuid.uuid4()


def _ensure_path_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _process_file(
    in_file: Path,
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

    # ensure the output directory exists, create it if not
    _ensure_path_exists(out_dir)

    random_uuid = _create_random_uuid

    # create .orig file
    _create_orig_file(in_file, random_uuid, out_dir)

    # convert file (create derivative) and create sidecar file based on category (image, video or other)
    file_category = get_file_category(in_file)
    if file_category == "OTHER":
        ext = PurePath(in_file).suffix
        converted_file_basename = str(random_uuid) + ext
        converted_file_full_path = out_dir / converted_file_basename
        shutil.copyfile(in_file, converted_file_full_path)
        create_sidecar_file(in_file, converted_file_full_path, out_dir, file_category)
    elif file_category == "IMAGE":
        ext = ".jp2"
        converted_file_basename = str(random_uuid) + ext
        converted_file_full_path = out_dir / converted_file_basename
        convert_file_with_sipi(in_file, converted_file_full_path)
        create_sidecar_file(in_file, converted_file_full_path, out_dir, file_category)
    elif file_category == "VIDEO":
        ext = PurePath(in_file).suffix
        converted_file_basename = str(random_uuid) + ext
        converted_file_full_path = out_dir / converted_file_basename
        shutil.copyfile(in_file, converted_file_full_path)
        extract_key_frames(converted_file_full_path)
        create_sidecar_file(in_file, converted_file_full_path, out_dir, file_category)
    else:
        raise BaseError(f"Unexpected file category: {file_category}")

    return in_file, converted_file_full_path
