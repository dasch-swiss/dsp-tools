import glob
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Optional

import requests
from regex import regex
from requests import JSONDecodeError

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import login, make_chunks

logger = get_logger(__name__)


def _check_processed_dir(dir_with_processed_files: str) -> Path:
    """
    Checks the input parameter provided by the user and transforms it into a Path.

    Args:
        dir_with_processed_files: the directory where the processed files have been written to

    Raises:
        UserError: if the directory does not exist

    Returns:
        Path object of the directory
    """
    dir_with_processed_files_path = Path(dir_with_processed_files)
    if not dir_with_processed_files_path.is_dir():
        raise UserError(f"The folder with the processed files is invalid: {dir_with_processed_files}")
    return dir_with_processed_files_path


def get_pkl_files() -> list[Path]:
    """
    Get all pickle files starting with "processing_result_" in the current working directory.

    Raises:
        UserError: If no pickle file was found

    Returns:
        list of pickle files
    """
    if pkl_file_paths := [Path(x) for x in glob.glob("processing_result_*.pkl")]:
        return pkl_file_paths
    else:
        raise UserError("No pickle file found. Please run the processing step first.")


def _get_paths_from_pkl_files(pkl_files: list[Path]) -> list[Path]:
    """
    Read the pickle file(s) returned by the processing step.

    Args:
        pkl_files: pickle file(s) returned by the processing step

    Returns:
        list of file paths of the processed files (uuid filenames)
    """
    orig_paths_2_processed_paths: list[tuple[Path, Optional[Path]]] = []
    for pkl_file in pkl_files:
        orig_paths_2_processed_paths.extend(pickle.loads(pkl_file.read_bytes()))

    processed_paths: list[Path] = []
    for orig_path, processed_path in orig_paths_2_processed_paths:
        if processed_path:
            processed_paths.append(processed_path)
        else:
            print(f"{datetime.now()}: WARNING: There is no processed file for {orig_path}")
            logger.warning(f"There is no processed file for {orig_path}")

    return processed_paths


def _get_upload_candidates(
    dir_with_processed_files: Path,
    internal_filename_of_processed_file: Path,
) -> list[Path]:
    """
    Based on the base derivate file, get all files based on the same uuid.
    For example, if the base derivate file is tmp/1f/fb/1ffbbb30-77e8-414c-94ff-7e1c060f9146.jp2,
    the upload candidates are:
    - derivate: tmp/1f/fb/1ffbbb30-77e8-414c-94ff-7e1c060f9146.jp2
    - original: tmp/1f/fb/1ffbbb30-77e8-414c-94ff-7e1c060f9146.png.orig
    - sidecar:  tmp/1f/fb/1ffbbb30-77e8-414c-94ff-7e1c060f9146.info

    In case of video files, there is a preview file in addition to the above files:
     - tmp/1f/fb/1ffbbb30-77e8-414c-94ff-7e1c060f9146/1ffbbb30-77e8-414c-94ff-7e1c060f9146_m_0.jpg

    Args:
        dir_with_processed_files: path to the directory where the processed files are located
        internal_filename_of_processed_file: processed file (uuid filename)

    Returns:
        list of all processed files that belong to the same original file
    """
    upload_candidates = glob.glob(f"{dir_with_processed_files}/**/**/{internal_filename_of_processed_file.stem}/*.*")
    upload_candidates.extend(
        glob.glob(f"{dir_with_processed_files}/**/**/{internal_filename_of_processed_file.stem}*.*")
    )
    upload_candidates_paths = [Path(c) for c in upload_candidates]
    linestart = "\n" + " " * 67 + "- "
    cand = linestart + linestart.join([str(c) for c in upload_candidates])
    logger.info(f"Found the following upload candidates for {internal_filename_of_processed_file}: {cand}")
    return upload_candidates_paths


def _check_upload_candidates(
    internal_filename_of_processed_file: Path,
    upload_candidates: list[Path],
) -> bool:
    """
    Make sure that all upload candidates exist,
    and that there are at least 5 candidates for videos and 3 candidates for all other file types.

    Args:
        internal_filename_of_processed_file: base derivate file (uuid filename)
        upload_candidates: list of all files that belong to the same original file

    Returns:
        True if all checks passed, False otherwise
    """
    if not internal_filename_of_processed_file.is_file():
        print(f"{datetime.now()}: ERROR: The input file '{internal_filename_of_processed_file}' was not found.")
        logger.error(f"The input file '{internal_filename_of_processed_file}' was not found.")
        return False

    if not all(Path(c).is_file() for c in upload_candidates):
        err_msg = f"Not all upload candidates were found for file {internal_filename_of_processed_file}"
        print(f"{datetime.now()}: ERROR: {err_msg}")
        logger.error(err_msg)
        return False

    min_num_of_candidates = 4 if internal_filename_of_processed_file.suffix == ".mp4" else 3
    if len(upload_candidates) < min_num_of_candidates:
        linestart = "\n" + " " * 67 + "- "
        cand = linestart + linestart.join([str(c) for c in upload_candidates])
        msg = f"Found the following files for {internal_filename_of_processed_file}, but more were expected: {cand}"
        print(f"{datetime.now()}: ERROR: {msg}")
        logger.error(msg)
        return False

    logger.info(f"Upload candidates for {internal_filename_of_processed_file} are okay.")
    return True


def _call_upload_without_processing_recursively(
    file: Path,
    sipi_url: str,
    con: Connection,
    err_msg: str,
) -> bool:
    """
    There are different kinds of failures in _upload_without_processing(),
    and each of them should be handled the same way:
    By calling this function.

    This function logs and prints the error message,
    sleeps for 2 seconds,
    and then calls _upload_without_processing() again.

    Args:
        file: file to upload
        sipi_url: URL of the SIPI server
        con: connection to the DSP server
        err_msg: message to print and log

    Returns:
        return value of _upload_without_processing()
    """
    print(f"{datetime.now()}: ERROR: {err_msg}")
    logger.error(err_msg, exc_info=True)
    sleep(2)
    return _upload_without_processing(
        file=file,
        sipi_url=sipi_url,
        con=con,
    )


def _upload_without_processing(
    file: Path,
    sipi_url: str,
    con: Connection,
) -> bool:
    """
    Send a single file to the "upload_without_processing" route.
    In case of failure, retry after 2 seconds
    by recursively calling this function again.
    Retry until the file could be uploaded.

    Args:
        file: file to upload
        sipi_url: URL of the SIPI server
        con: connection to the DSP server

    Returns:
        True if the file could be uploaded
    """
    try:
        with open(file, "rb") as bitstream:
            response_upload = requests.post(
                url=f"{regex.sub(r'/$', '', sipi_url)}/upload_without_processing",
                headers={"Authorization": f"Bearer {con.get_token()}"},
                files={"file": bitstream},
                timeout=8 * 60,
            )
    except Exception:  # pylint: disable=broad-exception-caught
        return _call_upload_without_processing_recursively(
            file=file,
            sipi_url=sipi_url,
            con=con,
            err_msg=(
                f"An exception occurred while opening the file {file} "
                "or while sending it to the /upload_without_processing route. Retrying..."
            ),
        )

    try:
        msg = response_upload.json().get("message")
    except JSONDecodeError:
        msg = None

    if msg == "server.fs.mkdir() failed: File exists":
        # This error can be safely ignored, since the file was uploaded correctly.
        logger.info(f"In spite of 'server.fs.mkdir() failed: File exists', successfully uploaded file {file}")
    elif response_upload.status_code != 200:
        return _call_upload_without_processing_recursively(
            file=file,
            sipi_url=sipi_url,
            con=con,
            err_msg=f"Uploading the file {file} returned non-200. Retrying... The response was {vars(response_upload)}",
        )
    else:
        logger.info(f"Successfully uploaded file {file}")

    return True


def _upload_file(
    dir_with_processed_files: Path,
    internal_filename_of_processed_file: Path,
    sipi_url: str,
    con: Connection,
) -> tuple[Path, bool]:
    """
    Retrieves all derivatives of one file and uploads them to the SIPI server.

    Args:
        dir_with_processed_files: path to the directory where the processed files are located
        internal_filename_of_processed_file: path to the derivate of the original file,
            i.e. the processed file (uuid filename)
        sipi_url: URL of the SIPI server
        con: connection to the DSP server

    Returns:
        tuple with the processed file and a boolean indicating if the upload was successful
    """
    upload_candidates = _get_upload_candidates(
        dir_with_processed_files=dir_with_processed_files,
        internal_filename_of_processed_file=internal_filename_of_processed_file,
    )

    check_result = _check_upload_candidates(
        internal_filename_of_processed_file=internal_filename_of_processed_file,
        upload_candidates=upload_candidates,
    )
    if not check_result:
        return internal_filename_of_processed_file, False

    results: list[bool] = []
    for candidate in upload_candidates:
        res = _upload_without_processing(
            file=candidate,
            sipi_url=sipi_url,
            con=con,
        )
        results.append(res)

    if not all(results):
        logger.error(f"Could not upload all files for {internal_filename_of_processed_file}.")
        return internal_filename_of_processed_file, False
    else:
        logger.info(f"Successfully uploaded all files for {internal_filename_of_processed_file}.")
        return internal_filename_of_processed_file, True


def _upload_files_in_parallel(
    dir_with_processed_files: Path,
    internal_filenames_of_processed_files: list[Path],
    sipi_url: str,
    con: Connection,
    nthreads: int,
) -> list[tuple[Path, bool]]:
    """
    Use a ThreadPoolExecutor to upload the files in parallel.

    Args:
        dir_with_processed_files: path to the directory where the processed files are located
        internal_filenames_of_processed_files: list of uuid filenames,
            each filename being the path to the derivate of the original file
        sipi_url: URL of the SIPI server
        con: connection to the DSP server
        nthreads: number of threads to use for the upload (optimum depends on the number of CPUs on the server)

    Returns:
        _description_
    """
    result: list[tuple[Path, bool]] = []
    for batch in make_chunks(lst=internal_filenames_of_processed_files, length=1000):
        _launch_thread_pool(nthreads, dir_with_processed_files, sipi_url, con, batch, result)
    return result


def _launch_thread_pool(
    nthreads: int,
    dir_with_processed_files: Path,
    sipi_url: str,
    con: Connection,
    batch: list[Path],
    result: list[tuple[Path, bool]],
) -> None:
    with ThreadPoolExecutor(max_workers=nthreads) as pool:
        upload_jobs = [
            pool.submit(
                _upload_file,
                dir_with_processed_files,
                internal_filename_of_processed_file,
                sipi_url,
                con,
            )
            for internal_filename_of_processed_file in batch
        ]
        for uploaded in as_completed(upload_jobs):
            result.append(uploaded.result())
            if len(result) % 1000 == 0:
                print(f"{datetime.now()}: Uploaded {len(result)} files...")


def _check_if_all_files_were_uploaded(
    result: list[tuple[Path, bool]],
    internal_filenames_of_processed_files: list[Path],
) -> bool:
    """
    Print the files which could not be uploaded.

    Args:
        result: list of tuples with the path of the file and the success status
        internal_filenames_of_processed_files: list of files that should have been uploaded (uuid filenames)

    Returns:
        True if all files were uploaded, False otherwise
    """
    if len(result) == len(internal_filenames_of_processed_files):
        success = True
        print(f"{datetime.now()}: Number of files of which the derivates were uploaded: {len(result)}: Okay")
        logger.info(f"Number of files of which the derivates were uploaded: {len(result)}: Okay")
    else:
        success = False
        ratio = f"{len(result)}/{len(internal_filenames_of_processed_files)}"
        msg = f"Some derivates of some files could not be uploaded: Only {ratio} were uploaded. The failed ones are:"
        print(f"{datetime.now()}: ERROR: {msg}")
        logger.error(msg)

    for path, res in result:
        if not res:
            print(f" - {path} could not be uploaded.")
            logger.error(f"{path} could not be uploaded.")

    return success


def upload_files(
    dir_with_processed_files: str,
    nthreads: int,
    user: str,
    password: str,
    dsp_url: str,
    sipi_url: str,
) -> bool:
    """
    Uploads the processed files to the DSP server, using multithreading.
    Before using this method, the files must be processed by the processing step.

    Args:
        dir_with_processed_files: path to the directory where the processed files are located
        nthreads: number of threads to use for uploading (optimum depends on the number of CPUs on the server)
        user: the user's e-mail for login into DSP
        password: the user's password for login into DSP
        dsp_url: URL to the DSP server
        sipi_url: URL of the SIPI server

    Returns:
        success status
    """
    dir_with_processed_files_path = _check_processed_dir(dir_with_processed_files)
    pkl_file_paths = get_pkl_files()
    logger.info("Found the following pickle files:")
    for pkl in pkl_file_paths:
        logger.info(f" - {str(pkl)}")

    # read paths from pkl file
    internal_filenames_of_processed_files = _get_paths_from_pkl_files(pkl_files=pkl_file_paths)
    print(f"{datetime.now()}: Found {len(internal_filenames_of_processed_files)} files to upload...")
    logger.info(f"Found {len(internal_filenames_of_processed_files)} files to upload...")

    # create connection to DSP
    con = login(
        server=dsp_url,
        user=user,
        password=password,
    )

    # upload files in parallel
    start_time = datetime.now()
    print(f"{start_time}: Start file uploading...")
    logger.info("Start file uploading...")
    result = _upload_files_in_parallel(
        dir_with_processed_files=dir_with_processed_files_path,
        internal_filenames_of_processed_files=internal_filenames_of_processed_files,
        sipi_url=sipi_url,
        con=con,
        nthreads=nthreads,
    )

    # check if all files were uploaded
    end_time = datetime.now()
    print(f"{datetime.now()}: Uploading files took {end_time - start_time}")
    logger.info(f"Uploading files took {end_time - start_time}")
    return _check_if_all_files_were_uploaded(
        result=result,
        internal_filenames_of_processed_files=internal_filenames_of_processed_files,
    )
