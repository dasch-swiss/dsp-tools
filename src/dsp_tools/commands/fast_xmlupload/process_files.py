"""This module handles processing of files referenced in the bitstream tags of an XML file."""

import hashlib
import json
import pickle
import shutil
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path, PurePath
from typing import Any, Literal, Optional, Union

import docker
import requests
from docker.models.containers import Container
from lxml import etree

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import http_call_with_retry, make_chunks

logger = get_logger(__name__)
sipi_container: Optional[Container] = None
export_moving_image_frames_script: Optional[Path] = None


def _get_export_moving_image_frames_script() -> None:
    """
    Downloads the shell script that is used to extract the preview image from a video.
    """
    user_folder = Path.home() / Path(".dsp-tools/fast-xmlupload")
    user_folder.mkdir(parents=True, exist_ok=True)
    global export_moving_image_frames_script
    export_moving_image_frames_script = user_folder / "export-moving-image-frames.sh"
    script_text_response = http_call_with_retry(
        action=requests.get,
        url="https://github.com/dasch-swiss/dsp-api/raw/main/sipi/scripts/export-moving-image-frames.sh",
    )
    script_text = script_text_response.text
    with open(export_moving_image_frames_script, "w", encoding="utf-8") as f:
        f.write(script_text)


def _determine_exit_code(
    files_to_process: list[Path],
    processed_files: list[tuple[Path, Optional[Path]]],
    is_last_batch: bool,
) -> Literal[0, 1, 2]:
    """
    Based on the result of the file processing,
    this function determines the exit code.
    If some files of the current batch could not be processed, the exit code is 1.
    If all files of the current batch were processed,
    the exit code is 0 if this is the last batch,
    and 2 if there are more batches to process.

    Args:
        files_to_process: list of all paths that should have been processed (current batch)
        processed_files: list of tuples of Paths. If the second Path is None, the file could not be processed.
        is_last_batch: true if this is the last batch of files to process

    Returns:
        exit code
    """
    processed_paths = [x[1] for x in processed_files if x and x[1]]
    if len(processed_paths) == len(files_to_process):
        print(f"{datetime.now()}: All files ({len(files_to_process)}) of this batch were processed: Okay")
        logger.info(f"All files ({len(files_to_process)}) of this batch were processed: Okay")
        if is_last_batch:
            print(f"{datetime.now()}: All multimedia files referenced in the XML are processed. No more batches.")
            logger.info("All multimedia files referenced in the XML are processed. No more batches.")
            return 0
        else:
            return 2
    else:
        ratio = f"{len(processed_paths)}/{len(files_to_process)}"
        msg = f"Some files of this batch could not be processed: Only {ratio} were processed. The failed ones are:"
        print(f"{datetime.now()}: ERROR: {msg}")
        logger.error(msg)
        for input_file, output_file in processed_files:
            if not output_file:
                print(f" - {input_file}")
                logger.error(f" - {input_file}")
        return 1


def _process_files_in_parallel(
    files_to_process: list[Path],
    input_dir: Path,
    output_dir: Path,
    nthreads: Optional[int],
) -> tuple[list[tuple[Path, Optional[Path]]], list[Path]]:
    """
    Creates a thread pool and executes the file processing in parallel.
    If a Docker API error occurs, the SIPI container is restarted,
    and the unprocessed files are returned,
    so that this function can be called again with the unprocessed files.

    Args:
        files_to_process: a list of all paths to the files that should be processed
        input_dir: the root directory of the input files
        output_dir: the directory where the processed files should be written to
        nthreads: number of threads to use for processing

    Returns:
        - a list of tuples with the original file path and the path to the processed file.
          (if a file could not be processed, the second path is None)
        - a list of all paths that could not be processed
          (this list will only have content if a Docker API error led to a restart of the SIPI container)
    """
    orig_filepath_2_uuid: list[tuple[Path, Optional[Path]]] = []
    for batch in make_chunks(lst=files_to_process, length=1000):
        if unprocessed_paths := _launch_thread_pool(nthreads, input_dir, output_dir, batch, orig_filepath_2_uuid):
            return orig_filepath_2_uuid, unprocessed_paths
    return orig_filepath_2_uuid, []


def _launch_thread_pool(
    nthreads: int | None,
    input_dir: Path,
    output_dir: Path,
    files_to_process: list[Path],
    orig_filepath_2_uuid: list[tuple[Path, Optional[Path]]],
) -> list[Path]:
    total = len(files_to_process)
    with ThreadPoolExecutor(max_workers=nthreads) as pool:
        processing_jobs = [pool.submit(_process_file, f, input_dir, output_dir) for f in files_to_process]
        for processed in as_completed(processing_jobs):
            try:
                orig_file, internal_file = processed.result()
                orig_filepath_2_uuid.append((orig_file, internal_file))
                msg = f"Successfully processed file {len(orig_filepath_2_uuid)}/{total} of this batch: {orig_file}"
                print(f"{datetime.now()}: {msg}")
                logger.info(msg)
            except docker.errors.APIError:
                print(f"{datetime.now()}: ERROR: A Docker exception occurred. Cancel jobs and restart SIPI...")
                logger.error("A Docker exception occurred. Cancel jobs and restart SIPI...", exc_info=True)
                for job in processing_jobs:
                    job.cancel()
                _restart_sipi_container(input_dir, output_dir)
                processed_paths = [x[0] for x in orig_filepath_2_uuid]
                unprocessed_paths = [x for x in files_to_process if x not in processed_paths]
                return unprocessed_paths
    return []


def _write_result_to_pkl_file(processed_files: list[tuple[Path, Optional[Path]]]) -> None:
    """
    Writes the processing result to a pickle file in the working directory.

    Args:
        processed_files: the result of the file processing

    Raises:
        UserError: if the file could not be written
    """
    filename = Path(f"processing_result_{datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f')}.pkl")

    try:
        with open(filename, "wb") as pkl_file:
            pickle.dump(processed_files, pkl_file)
        print(f"{datetime.now()}: The result was written to: {filename}")
    except OSError:
        err_msg = f"An error occurred while writing the result to the pickle file. Content of file: {processed_files}"
        logger.error(err_msg, exc_info=True)
        raise UserError(err_msg) from None


def _check_input_params(
    input_dir: str,
    out_dir: str,
    xml_file: str,
) -> tuple[Path, Path, Path]:
    """
    Checks the input parameters provided by the user and transforms them into Path objects.
    If the output directory doesn't exist, it is created.

    Args:
        input_dir: the root directory of the input files
        out_dir: the output directory where the created files should be written to
        xml_file: the XML file the paths are extracted from

    Raises:
        UserError: if one of the parameters is not valid

    Returns:
        A tuple with the Path objects of the input strings
    """
    input_dir_path = Path(input_dir)
    out_dir_path = Path(out_dir)
    xml_file_path = Path(xml_file)

    try:
        out_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception:  # pylint: disable=broad-exception-caught
        raise UserError(f"Couldn't create directory {out_dir_path}") from None

    if not input_dir_path.is_dir():
        raise UserError(f"{input_dir} is not a directory")
    if not xml_file_path.is_file():
        raise UserError(f"{xml_file} is not a file")

    return input_dir_path, out_dir_path, xml_file_path


def _get_file_paths_from_xml(xml_file: Path) -> list[Path]:
    """
    Parse XML file to get all file paths.
    If the same file is referenced several times in the XML,
    it is only returned once.

    Args:
        xml_file: path to the XML file

    Raises:
        UserError: if a referenced file doesn't exist in the file system

    Returns:
        list of all paths in the <bitstream> tags
    """
    tree: etree._ElementTree[etree._Element] = etree.parse(xml_file)
    bitstream_paths: set[Path] = set()
    for x in tree.iter():
        if x.text and etree.QName(x).localname.endswith("bitstream"):
            path = Path(x.text)
            if path.is_file():
                bitstream_paths.add(path)
            else:
                msg = f"{datetime.now()}: ERROR: '{path}' is referenced in the XML file, but it doesn't exist."
                logger.error(msg)
                raise UserError(msg)

    return list(bitstream_paths)


def _restart_sipi_container(
    input_dir: Path,
    output_dir: Path,
) -> None:
    """
    Stop a possibly existing SIPI container,
    then create and start a new one.

    Args:
        input_dir: the root directory of the images that should be processed, is mounted into the container
        output_dir: the output directory where the processed files should be written to, is mounted into the container
    """
    _stop_and_remove_sipi_container()
    global sipi_container
    docker_client = docker.from_env()
    sipi_container = docker_client.containers.run(
        image="daschswiss/sipi:3.8.1",
        name="sipi",
        volumes=[
            f"{input_dir.absolute()}:/sipi/processing-input",
            f"{output_dir.absolute()}:/sipi/processing-output",
        ],
        entrypoint=["tail", "-f", "/dev/null"],
        detach=True,
    )
    print(f"{datetime.now()}: Created and started Sipi container.")
    logger.info("Created and started Sipi container.")


def _stop_and_remove_sipi_container() -> None:
    """
    Stop and remove the SIPI container.
    """
    global sipi_container
    if not sipi_container:
        # the Sipi container is not stored in the global variable, but perhaps it exists
        docker_client = docker.from_env()
        try:
            sipi_container = docker_client.containers.get("sipi")
        except docker.errors.NotFound:
            # printing is not necessary, the user doesn't need to know that there is no Sipi container
            logger.warning("There is no Sipi container that could be removed.")
            return

    # at this point, a Sipi container exists and is stored in the global variable
    try:
        sipi_container.stop()
        sipi_container.remove()
        print(f"{datetime.now()}: Stopped and removed Sipi container.")
        logger.info("Stopped and removed Sipi container.")
    except docker.errors.APIError:
        print(f"{datetime.now()}: WARNING: It was not possible to stop and remove the Sipi container.")
        logger.warning("It was not possible to stop and remove the Sipi container.")


def _compute_sha256(file: Path) -> Optional[str]:
    """
    Calculates SHA256 checksum of a file

    Args:
        file: path of the file

    Returns:
        the calculated checksum
    """
    if not file.is_file():
        print(f"{datetime.now()}: ERROR: Couldn't calculate checksum for {file}, because such a file doesn't exist.")
        logger.error(f"Couldn't calculate checksum for {file}, because such a file doesn't exist.")
        return None
    hash_sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def _convert_file_with_sipi(
    in_file_local_path: Path,
    input_dir: Path,
    out_file_local_path: Path,
    output_dir: Path,
) -> bool:
    """
    Converts a file by calling a locally running Sipi container.

    Args:
        in_file_local_path: path to input file
        input_dir: the directory where the input files are located
        out_file_local_path: path to output file,
            e.g. tmp/in/te/internal_file_name.jp2 if the internal filename is "internal_file_name"
        output_dir: the directory where the processed files are written to,
            e.g. tmp/in/te/ if the internal filename is "internal_file_name"

    Returns:
        success status
    """
    original_output_dir = output_dir.parent.parent
    in_file_sipi_path = Path("processing-input") / in_file_local_path.relative_to(input_dir)
    out_file_sipi_path = Path("processing-output") / out_file_local_path.relative_to(original_output_dir)

    if not sipi_container:
        print(f"{datetime.now()}: ERROR: Cannot convert file {in_file_local_path} with Sipi: Sipi container not found.")
        logger.error(f"Cannot convert file {in_file_local_path} with Sipi: Sipi container not found.")
        return False
    result = sipi_container.exec_run(f"/sipi/sipi '{in_file_sipi_path}' {out_file_sipi_path}")
    if result.exit_code != 0:
        print(f"{datetime.now()}: ERROR: Sipi conversion of {in_file_local_path} failed: {result}")
        logger.error(f"Sipi conversion of {in_file_local_path} failed: {result}")
        return False
    return True


def _create_orig_file(
    in_file: Path,
    internal_file_name: str,
    out_dir: Path,
) -> bool:
    """
    Creates the .orig file expected by the API.

    Args:
        in_file: the input file from which the .orig should be created
        internal_file_name: the internal filename which should be used for the .orig file
        out_dir: the directory where the .orig file should be written to,
            e.g. tmp/in/te/ if the internal filename is "internal_file_name"

    Returns:
        success status
    """
    orig_ext = PurePath(in_file).suffix
    orig_file_full_path = Path(out_dir, f"{internal_file_name}{orig_ext}.orig")
    try:
        shutil.copyfile(in_file, orig_file_full_path)
        logger.info(f"Created .orig file {orig_file_full_path}")
        return True
    except Exception:  # pylint: disable=broad-exception-caught
        print(f"{datetime.now()}: ERROR: Couldn't create .orig file {orig_file_full_path}")
        logger.error(f"Couldn't create .orig file {orig_file_full_path}", exc_info=True)
        return False


def _get_video_metadata_with_ffprobe(file_path: Path) -> Optional[dict[str, Any]]:
    """
    Gets video metadata by running ffprobe

    Args:
        file_path: path to the file which the metadata should be extracted from

    Returns:
        the metadata object as json
    """
    command_array = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,bit_rate,duration,nb_frames,r_frame_rate",
        "-print_format",
        "json",
        "-i",
        str(file_path),
    ]
    try:
        result = subprocess.run(
            command_array,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
    except Exception:  # pylint: disable=broad-exception-caught
        print(f"{datetime.now()}: ERROR: Exception occurred while running ffprobe for {file_path}")
        logger.error(f"Exception occurred while running ffprobe for {file_path}", exc_info=True)
        return None
    if result.returncode == 0:
        logger.info(f"Successfully ran ffprobe for {file_path}")
        video_metadata: dict[str, Any] = json.loads(result.stdout)["streams"][0]  # get first stream
        return video_metadata
    else:
        print(f"{datetime.now()}: ERROR: Couldn't run ffprobe for {file_path}")
        logger.error(f"Couldn't run ffprobe for {file_path}")
        return None


def _create_sidecar_file(
    orig_file: Path,
    converted_file: Path,
    file_category: str,
) -> bool:
    """
    Creates the sidecar file for a given file. Depending on the file category, it adds category specific metadata.

    Args:
        orig_file: path to the original file
        converted_file: path to the converted file, e.g. out_dir/in/te/internal_filename.ext
        file_category: the file category, either IMAGE, VIDEO or OTHER

    Returns:
        true if successful, false otherwise
    """
    if file_category not in ("IMAGE", "VIDEO", "OTHER"):
        print(f"{datetime.now()}: ERROR: Unexpected file category {file_category}")
        logger.error(f"Unexpected file category {file_category}")
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
    sidecar_dict: dict[str, Union[str, float]] = {
        "originalFilename": original_filename,
        "checksumOriginal": checksum_original,
        "checksumDerivative": checksum_derivative,
        "internalFilename": internal_filename,
        "originalInternalFilename": original_internal_filename,
    }

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
    sidecar_file = PurePath(converted_file.parent, sidecar_file_basename)

    with open(sidecar_file, "w", encoding="utf-8") as f:
        sidecar_json = json.dumps(sidecar_dict, indent=4)
        f.write(sidecar_json)

    logger.info(f"Created sidecar file {sidecar_file}")
    return True


def _get_file_category_from_extension(file: Path) -> Optional[str]:
    """
    Gets the file category of a file according to its extension.

    Args:
        file: file which the category should be got from

    Returns:
        the file category, either IMAGE, VIDEO or OTHER (or None)
    """
    extensions = {
        "image": [".jpg", ".jpeg", ".tif", ".tiff", ".jp2", ".png"],
        "video": [".mp4"],
        "archive": [".7z", ".gz", ".gzip", ".tar", ".tar.gz", ".tgz", ".z", ".zip"],
        "text": [".csv", ".txt", ".xml", ".xsd", ".xsl"],
        "document": [".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx"],
        "audio": [".mp3", ".wav"],
    }
    if file.suffix.lower() in extensions["video"]:
        category = "VIDEO"
    elif file.suffix.lower() in extensions["image"]:
        category = "IMAGE"
    elif file.suffix.lower() in (
        extensions["archive"] + extensions["text"] + extensions["document"] + extensions["audio"]
    ):
        category = "OTHER"
    else:
        category = None
        print(f"{datetime.now()}: ERROR: Couldn't get category for {file}")
        logger.error(f"Couldn't get category for {file}")
    return category


def _extract_preview_from_video(file: Path) -> bool:
    """
    Extracts a preview image of a video and writes it to disk.

    Args:
        file: the video file which the preview is extracted from

    Returns:
        true if successful, false otherwise
    """

    result = subprocess.call(["/bin/bash", f"{export_moving_image_frames_script}", "-i", f"{file}"])
    return result == 0


def _process_file(
    in_file: Path,
    input_dir: Path,
    output_dir: Path,
) -> tuple[Path, Optional[Path]]:
    """
    Creates all expected derivative files and writes the output into the provided output directory.

    In case of image: .orig file, JP2 derivate, sidecar file
    In case of video: .orig file, identical derivate file, sidecar file, folder with 1 preview image
    other files: .orig file, identical derivate file, sidecar file

    Args:
        in_file: path to input file that should be processed
        input_dir: root directory of the input files
        output_dir: target location where the created files are written to.
            If the directory doesn't exist, it is created

    Returns:
        tuple consisting of the original path and the internal filename.
        If there was an error, the internal filename is None.
    """
    # ensure that input file exists
    if not in_file.is_file():
        print(f"{datetime.now()}: ERROR: '{in_file}' does not exist. Skipping...")
        logger.error(f"'{in_file}' does not exist. Skipping...")
        return in_file, None

    # get random UUID for internal file handling, and create directory structure
    internal_filename = str(uuid.uuid4())
    out_dir_full = Path(output_dir, internal_filename[:2], internal_filename[2:4])
    out_dir_full.mkdir(parents=True, exist_ok=True)

    # create .orig file
    if not _create_orig_file(
        in_file=in_file,
        internal_file_name=internal_filename,
        out_dir=out_dir_full,
    ):
        return in_file, None

    # convert file (create derivative) and create sidecar file based on category (image, video or other)
    file_category = _get_file_category_from_extension(in_file)
    if not file_category:
        return in_file, None

    if file_category == "OTHER":
        result = _process_other_file(
            in_file=in_file,
            internal_filename=internal_filename,
            out_dir=out_dir_full,
        )
    elif file_category == "IMAGE":
        result = _process_image_file(
            in_file=in_file,
            internal_filename=internal_filename,
            out_dir=out_dir_full,
            input_dir=input_dir,
        )
    elif file_category == "VIDEO":
        result = _process_video_file(
            in_file=in_file,
            internal_filename=internal_filename,
            out_dir=out_dir_full,
        )
    else:
        print(f"{datetime.now()}: ERROR: Unexpected file category for {in_file}: {file_category}")
        logger.error(f"Unexpected file category for {in_file}: {file_category}")
        return in_file, None

    return result


def _process_other_file(
    in_file: Path,
    internal_filename: str,
    out_dir: Path,
) -> tuple[Path, Optional[Path]]:
    """
    Processes a file of file category OTHER.
    There is no real derivate created,
    but the original file is copied,
    and a sidecar file is created.

    Args:
        in_file: the input file that should be processed
        internal_filename: the internal filename that should be used for the output file
        out_dir: the output directory where the processed file should be written to,
            e.g. tmp/in/te/ if the internal filename is "internal_file_name"

    Returns:
        a tuple of the original file path and the path to the processed file.
        If there was an error, the internal filename is None.
    """
    converted_file_full_path = out_dir / Path(internal_filename).with_suffix(in_file.suffix)
    try:
        shutil.copyfile(in_file, converted_file_full_path)
    except Exception:  # pylint: disable=broad-exception-caught
        print(f"{datetime.now()}: ERROR: Couldn't process file of category OTHER: {in_file}")
        logger.error(f"Couldn't process file of category OTHER: {in_file}", exc_info=True)
        return in_file, None
    if not _create_sidecar_file(
        orig_file=in_file,
        converted_file=converted_file_full_path,
        file_category="OTHER",
    ):
        print(f"{datetime.now()}: ERROR: Couldn't create sidecar file for: {in_file}")
        logger.error(f"Couldn't create sidecar file for: {in_file}")
        return in_file, None
    return in_file, converted_file_full_path


def _process_image_file(
    in_file: Path,
    internal_filename: str,
    out_dir: Path,
    input_dir: Path,
) -> tuple[Path, Optional[Path]]:
    """
    Processes a file of file category IMAGE

    Args:
        in_file: the input file that should be processed
        internal_filename: the internal filename that should be used for the output file
        out_dir: the output directory where the processed file should be written to,
            e.g. tmp/in/te/ if the internal filename is "internal_file_name"
        input_dir: root directory of the input files

    Returns:
        a tuple of the original file path and the path to the processed file.
        If there was an error, the internal filename is None.
    """
    converted_file_full_path = out_dir / Path(internal_filename).with_suffix(".jp2")
    sipi_result = _convert_file_with_sipi(
        in_file_local_path=in_file,
        input_dir=input_dir,
        out_file_local_path=converted_file_full_path,
        output_dir=out_dir,
    )
    if not sipi_result:
        print(f"{datetime.now()}: ERROR: Couldn't process file of category IMAGE: {in_file}")
        logger.error(f"Couldn't process file of category IMAGE: {in_file}")
        return in_file, None
    if not _create_sidecar_file(
        orig_file=in_file,
        converted_file=converted_file_full_path,
        file_category="IMAGE",
    ):
        print(f"{datetime.now()}: ERROR: Couldn't create sidecar file for: {in_file}")
        logger.error(f"Couldn't create sidecar file for: {in_file}")
        return in_file, None
    return in_file, converted_file_full_path


def _process_video_file(
    in_file: Path,
    internal_filename: str,
    out_dir: Path,
) -> tuple[Path, Optional[Path]]:
    """
    Processes a file of file category VIDEO

    Args:
        in_file: the input file that should be processed
        internal_filename: the internal filename that should be used for the output file
        out_dir: the output directory where the processed file should be written to,
            e.g. tmp/in/te/ if the internal filename is "internal_file_name"

    Returns:
        a tuple of the original file path and the path to the processed file.
        If there was an error, the internal filename is None.
    """
    converted_file_full_path = out_dir / Path(internal_filename).with_suffix(in_file.suffix)
    # create derivate file (identical to original file)
    try:
        shutil.copyfile(in_file, converted_file_full_path)
    except Exception:  # pylint: disable=broad-exception-caught
        print(f"{datetime.now()}: ERROR: Couldn't create derivate file for video '{in_file}'")
        logger.error(f"Couldn't create derivate file for video '{in_file}'", exc_info=True)
        return in_file, None

    # create preview image
    preview_result = _extract_preview_from_video(converted_file_full_path)
    if not preview_result:
        print(f"{datetime.now()}: ERROR: Couldn't create preview image for video '{in_file}'")
        logger.error(f"Couldn't create preview image for video '{in_file}'")
        return in_file, None

    # create sidecar file
    if not _create_sidecar_file(
        orig_file=in_file,
        converted_file=converted_file_full_path,
        file_category="VIDEO",
    ):
        print(f"{datetime.now()}: ERROR: Couldn't create sidecar file for video '{in_file}'")
        logger.error(f"Couldn't create sidecar file for video '{in_file}'")
        return in_file, None

    return in_file, converted_file_full_path


def _write_processed_and_unprocessed_files_to_txt_files(
    all_files: list[Path],
    processed_files: list[tuple[Path, Optional[Path]]],
) -> bool:
    """
    Determine the files that were processed and write them to 'processed_files.txt'.
    Determine the files that were not processed and write them to 'unprocessed_files.txt'.

    Args:
        all_files: list of all paths that should be processed
        processed_files: list of tuples (orig path, processed path). 2nd path is None if a file could not be processed.

    Returns:
        True if all multimedia files in the XML file were processed, False otherwise
    """
    success = True
    processed_original_paths = [x[0] for x in processed_files]
    with open("processed_files.txt", "x", encoding="utf-8") as f:
        f.write("\n".join([str(x) for x in processed_original_paths]))
    msg = "Wrote 'processed_files.txt'"

    if unprocessed_original_paths := [x for x in all_files if x not in processed_original_paths]:
        with open("unprocessed_files.txt", "x", encoding="utf-8") as f:
            f.write("\n".join([str(x) for x in unprocessed_original_paths]))
        msg += " and 'unprocessed_files.txt'"
        success = False

    print(f"{datetime.now()}: {msg}")
    logger.info(msg)
    return success


def handle_interruption(
    all_files: list[Path],
    processed_files: list[tuple[Path, Optional[Path]]],
    exception: BaseException,
) -> None:
    """
    Handles an interruption of the processing.
    Writes the pickle file,
    and the txt files with the processed and unprocessed files,
    and exits the program with exit code 1.

    Args:
        all_files: list of all paths that should be processed
        processed_files: list of tuples (orig path, processed path). 2nd path is None if a file could not be processed.
        exception: the exception that was raised
    """
    msg = "ERROR while processing the files. Writing pickle file and human-readable txt files..."
    print(f"{datetime.now()}: {msg}")
    logger.error(msg, exc_info=exception)

    _write_processed_and_unprocessed_files_to_txt_files(
        all_files=all_files,
        processed_files=processed_files,
    )
    _write_result_to_pkl_file(processed_files)

    sys.exit(1)


def double_check_unprocessed_files(
    all_files: list[Path],
    processed_files: list[Path],
    unprocessed_files: list[Path],
) -> None:
    """
    Checks if the files in 'unprocessed_files.txt' are consistent with the files in 'processed_files.txt'.

    Args:
        all_files: list of all paths in the <bitstream> tags of the XML file
        processed_files: the paths from 'processed_files.txt'
        unprocessed_files: the paths from 'unprocessed_files.txt' (or all_files if there is no such file)

    Raises:
        UserError: if there is a file 'unprocessed_files.txt', but no file 'processed_files.txt'
        UserError: if the files 'unprocessed_files.txt' and 'processed_files.txt' are inconsistent
    """
    unprocessed_files_txt_exists = sorted(unprocessed_files) != sorted(all_files)
    if unprocessed_files_txt_exists and not processed_files:
        logger.error("There is a file 'unprocessed_files.txt', but no file 'processed_files.txt'")
        raise UserError("There is a file 'unprocessed_files.txt', but no file 'processed_files.txt'")

    if processed_files and sorted(unprocessed_files) == sorted(all_files):
        logger.error("There is a file 'processed_files.txt', but no file 'unprocessed_files.txt'")
        raise UserError("There is a file 'processed_files.txt', but no file 'unprocessed_files.txt'")

    if unprocessed_files_txt_exists:
        # there is a 'unprocessed_files.txt' file. check it for consistency
        unprocessed_files_from_processed_files = [x for x in all_files if x not in processed_files]
        if sorted(unprocessed_files_from_processed_files) != sorted(unprocessed_files):
            logger.error("The files 'unprocessed_files.txt' and 'processed_files.txt' are inconsistent")
            raise UserError("The files 'unprocessed_files.txt' and 'processed_files.txt' are inconsistent")


def process_files(
    input_dir: str,
    output_dir: str,
    xml_file: str,
    nthreads: Optional[int],
) -> bool:
    """
    Process the files referenced in the given XML file.
    Writes the processed files
    (derivative, .orig file, sidecar file, as well as the preview file for movies)
    to the given output directory.
    Additionally, writes a pickle file containing the mapping between the original files and the processed files,
    e.g. Path('multimedia/nested/subfolder/test.tif'), Path('tmp/0b/22/0b22570d-515f-4c3d-a6af-e42b458e7b2b.jp2').

    Args:
        input_dir: path to the directory where the files should be read from
        output_dir: path to the directory where the transformed / created files should be written to
        xml_file: path to xml file containing the resources
        nthreads: number of threads to use for processing

    Returns:
        True if all multimedia files in the XML file were processed, False otherwise
    """
    input_dir_path, output_dir_path, xml_file_path = _check_input_params(
        input_dir=input_dir,
        out_dir=output_dir,
        xml_file=xml_file,
    )
    all_files = _get_file_paths_from_xml(xml_file_path)
    _restart_sipi_container(
        input_dir=input_dir_path,
        output_dir=output_dir_path,
    )
    if any(path.suffix == ".mp4" for path in all_files):
        _get_export_moving_image_frames_script()

    start_time = datetime.now()
    print(f"{start_time}: Start local file processing...")
    logger.info("Start local file processing...")

    processed_files: list[tuple[Path, Optional[Path]]] = []
    unprocessed_files = all_files
    while unprocessed_files:
        try:
            result, unprocessed_files = _process_files_in_parallel(
                files_to_process=unprocessed_files,
                input_dir=input_dir_path,
                output_dir=output_dir_path,
                nthreads=nthreads,
            )
            processed_files.extend(result)
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            handle_interruption(
                all_files=all_files,
                processed_files=processed_files,
                exception=exc,
            )

    end_time = datetime.now()
    print(f"{end_time}: Processing files took: {end_time - start_time}")
    logger.info(f"Processing files took: {end_time - start_time}")

    success = _write_processed_and_unprocessed_files_to_txt_files(
        all_files=all_files,
        processed_files=processed_files,
    )
    _write_result_to_pkl_file(processed_files)

    if success:
        # if there were problems, don't remove the sipi container. it might contain valuable log data.
        _stop_and_remove_sipi_container()
        return True
    else:
        print("Something went wrong. The SIPI container is still available to be analyzed. Don't forget to remove it.")
        return False
