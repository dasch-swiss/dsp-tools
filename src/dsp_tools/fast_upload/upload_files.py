import glob
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from regex import regex

from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import BaseError
from dsp_tools.utils.shared import login


def _get_upload_candidates(root_dir: Path, filename: Path) -> list[Path]:
    upload_candidates: list[str] = []
    upload_candidates.extend(glob.glob(f"{root_dir}/{filename.stem}/**/*.*"))
    upload_candidates.extend(glob.glob(f"{root_dir}/{filename.stem}/*.*"))
    upload_candidates.extend(glob.glob(f"{root_dir}/{filename.stem}*.*"))
    upload_candidates_paths = [Path(c) for c in upload_candidates]
    return upload_candidates_paths


def _check_upload_candidates(input_file: Path, list_of_paths: list[Path]) -> bool:
    if not input_file.is_file():
        print(f"The input file was not found {input_file}")
        return False

    if not all(Path(c).is_file() for c in list_of_paths):
        print(f"Not all upload candidates were found for file {input_file}")
        return False

    min_num_of_candidates = 5 if input_file.suffix == ".mp4" else 3
    if len(list_of_paths) < min_num_of_candidates:
        print(
            f"Found the following files for {input_file}, but more were expected: {list_of_paths}. Skipping...")
        return False

    return True


def _upload_without_processing(file: Path, sipi_url: str, con: Connection) -> bool:
    try:
        with open(file, "rb") as bitstream:
            response_upload = requests.post(
                url=f"{regex.sub(r'/$', '', sipi_url)}/upload_without_processing?token={con.get_token()}",
                files={"file": bitstream}
            )
    except:
        print(f"An error occurred while uploading the file {file}")
        return False

    if response_upload.status_code != 200:
        print(f"An error occurred while uploading the file {file}. The response was {response_upload.json()}")
        return False

    return True


def _upload_file(sipi_processed_path: Path,
                 processed_file: Path,
                 sipi_url: str,
                 con: Connection
                 ) -> tuple[Path, bool]:
    upload_candidates: list[Path] = _get_upload_candidates(sipi_processed_path, processed_file)

    check_result = _check_upload_candidates(processed_file, upload_candidates)
    if not check_result:
        return Path(processed_file), False

    result: list[bool] = []
    for candidate in upload_candidates:
        res: bool = _upload_without_processing(candidate, sipi_url, con)
        result.append(res)

    if not any(result):
        return processed_file, False

    return processed_file, True


def _get_paths_from_pkl_file(pkl_file: Path) -> list[Path]:
    with open(pkl_file, 'rb') as f:
        orig_paths_2_processed_paths: list[tuple[Path, Path]] = pickle.load(f)

    processed_paths: list[Path] = []
    for orig_processed in orig_paths_2_processed_paths:
        processed_paths.append(orig_processed[1])

    return processed_paths


def _check_params(paths_file: str, processed_dir: str) -> Optional[tuple[Path, Path]]:
    """
    Checks the input parameters provided by the user and transforms them into the expected types.

    Args:
        paths_file: the XML file the paths are extracted from
        processed_dir: the output directory where the created files should be written to

    Returns:
        A tuple with the Path objects of the input strings
    """
    paths_file = Path(paths_file)
    processed_dir = Path(processed_dir)

    if not paths_file.is_file():
        print(f"{paths_file} is not a file")
        return None
    if not processed_dir.is_dir():
        print(f"{processed_dir} is not a directory")
        return None

    return paths_file, processed_dir


def _upload_files_in_parallel(processed_dir: Path,
                              paths: list[Path],
                              sipi_url: str,
                              con: Connection
                              ) -> list[tuple[Path, bool]]:
    with ThreadPoolExecutor() as pool:
        upload_jobs = [pool.submit(
            _upload_file,
            processed_dir,
            file,
            sipi_url,
            con
        ) for file in paths]

    result: list[tuple[Path, bool]] = []
    for uploaded in as_completed(upload_jobs):
        result.append(uploaded.result())
    return result


def _check_result(result: list[tuple[Path, bool]]):
    print("Checking result...")
    for path, res in result:
        if not res:
            print(f"Something went wrong with uploading {path}. Please check.")


def upload_files(paths_file: str,
                 processed_dir: str,
                 user: str,
                 password: str,
                 dsp_url: str,
                 sipi_url: str
                 ) -> bool:
    """
    Reads the paths from the pickle file and uploads all files without processing.

    Args:
        paths_file: path to the pickle file which contains the paths of the processed files
        processed_dir: path to the directory where the processed files are located
        user: the user's e-mail for login into DSP
        password: the user's password for login into DSP
        dsp_url: URL to the DSP server
        sipi_url: URL to the Sipi server
    Returns:
        success status
    """
    # check params
    param_check_result = _check_params(paths_file, processed_dir)
    if param_check_result:
        paths_file, processed_dir = param_check_result
    else:
        raise BaseError("Error reading the input parameters. Please check them.")

    # read paths from pkl file
    paths = _get_paths_from_pkl_file(pkl_file=paths_file)

    # create connection to DSP
    con = login(dsp_url, user, password)

    print(f"{datetime.now()}: Start file uploading...")
    start_time = datetime.now()
    result: list[tuple[Path, bool]] = _upload_files_in_parallel(processed_dir, paths, sipi_url, con)
    print(f"{datetime.now()}: Uploading files took {datetime.now() - start_time}")

    _check_result(result)
    print(f"The result was: {result}")

    return True

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

