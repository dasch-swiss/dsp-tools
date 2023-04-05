import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path, PurePath
from typing import Union, Any

import docker
from docker.models.resource import Model
from lxml import etree

from dsp_tools.models.exceptions import BaseError


def get_file_paths_from_xml(xml_file: Path) -> list[str]:
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


def create_orig_file(in_file, random_file_name, out_dir):
    """
    Creates the .orig file expected by the API.

    Args:
        in_file ():
        random_file_name ():
        out_dir ():
    """
    orig_ext = PurePath(in_file).suffix  # .tif
    orig_file_basename = f"{random_file_name}{orig_ext}.orig"
    orig_file = PurePath(out_dir, orig_file_basename)
    shutil.copyfile(in_file, orig_file)


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


def process_file(
    in_file: Path,
    out_dir: Path
) -> tuple[Path, Path]:
    """
    Sends a file to SIPI to convert it. Creates a derivative, an original file and a sidecar file.

    Args:
        in_file: path to file
        out_dir: target location of processed files (.../images/tmp/processed)

    Returns:
        tuple consisting of the original path and the SIPI-internal filename
    """

    random_uuid = uuid.uuid4()

    # create .orig file
    create_orig_file(in_file, random_uuid, out_dir)

    # convert file (create derivative) and create sidecar file based on category (image, video or other)
    file_category = get_file_category(in_file)
    if file_category == "OTHER":
        ext = PurePath(in_file).suffix
        converted_file_basename = str(random_uuid) + ext
        converted_file = out_dir / converted_file_basename
        shutil.copyfile(in_file, converted_file)
        create_sidecar_file(in_file, converted_file, out_dir, file_category)
    elif file_category == "IMAGE":
        ext = ".jp2"
        converted_file_basename = str(random_uuid) + ext
        converted_file = out_dir / converted_file_basename
        convert_file_with_sipi(in_file, converted_file)
        create_sidecar_file(in_file, converted_file, out_dir, file_category)
    elif file_category == "VIDEO":
        ext = PurePath(in_file).suffix
        converted_file_basename = str(random_uuid) + ext
        converted_file = out_dir / converted_file_basename
        shutil.copyfile(in_file, converted_file)
        extract_key_frames(converted_file)
        create_sidecar_file(in_file, converted_file, out_dir, file_category)
    else:
        raise BaseError(f"Unexpected file category: {file_category}")

    return in_file, converted_file


def main():
    xml_file = Path("/Users/irina/GitHub/dsp-tools/enhanced-xmlupload-testproject/test.xml")

    out_dir = Path("/Users/irina/GitHub/dsp-api/sipi/images/tmp/processed/")
    out_dir.mkdir(parents=True, exist_ok=True)

    start_time_p = datetime.now()

    processed_files = []
    file_paths = get_file_paths_from_xml(xml_file)
    for in_file in file_paths:
        in_file = Path(in_file)
        orig, converted = process_file(in_file, out_dir)
        processed_files.append(converted)

    print("TIME PROCESSING FILES:", datetime.now() - start_time_p)

    # upload_candidates: list[str] = []
    # for processed_file in processed_files:
    #     upload_candidates.extend(glob.glob(f"{Path(root_dir)}/{Path(processed_file).stem}/**/*.*"))
    #     upload_candidates.extend(glob.glob(f"{Path(root_dir)}/{Path(processed_file).stem}*.*"))
    #
    # con = Connection("http://0.0.0.0:3333")
    # try_network_action(lambda: con.login("root@example.com", "test"))
    #
    # start_time_u = datetime.now()
    #
    # for candidate in upload_candidates:
    #     with open(candidate, "rb") as bitstream:
    #         response_upload = requests.post(
    #             url=f"http://0.0.0.0:1024/upload_without_processing?token={con.get_token()}",
    #             files={"file": bitstream}
    #         )
    #     if not response_upload.json().get("uploadedFiles"):
    #         raise BaseError(
    #             f"File {candidate} ({candidate}) could not be uploaded. The API response was: {response_upload.text}")
    #
    # print("TIME UPLOADING FILES:", datetime.now() - start_time_u)


if __name__ == "__main__":
    main()
