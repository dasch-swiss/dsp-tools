from pathlib import Path

import pandas as pd

from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailureDetail
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailureDetails

SHORTCODE = "0001"
DSP_INGEST_URL = "https://ingest.test.dasch.swiss"


def test_no_failures() -> None:
    failures: list[UploadFailureDetail | None] = [None, None, None]
    aggregated_failures = UploadFailureDetails(failures, SHORTCODE, DSP_INGEST_URL)
    msg = aggregated_failures.execute_error_protocol()
    assert msg == ""


def test_one_failure() -> None:
    f1 = UploadFailureDetail(Path("path1"), "reason1")
    failures: list[UploadFailureDetail | None] = [None, f1, None]
    aggregated_failures = UploadFailureDetails(failures, SHORTCODE, DSP_INGEST_URL)
    msg = aggregated_failures.execute_error_protocol()
    expected = (
        f"Uploaded 2/3 files onto server {DSP_INGEST_URL}. Failed to upload the following 1 files:\n"
        " - path1: reason1"
    )
    assert msg == expected


def test_several_failures() -> None:
    f1 = UploadFailureDetail(Path("path1"), "reason1")
    f2 = UploadFailureDetail(Path("path2"), "reason2")
    f3 = UploadFailureDetail(Path("path3"), "reason3")
    failures: list[UploadFailureDetail | None] = [None, f1, None, f2, f3]
    aggregated_failures = UploadFailureDetails(failures, SHORTCODE, DSP_INGEST_URL)
    msg = aggregated_failures.execute_error_protocol()
    expected = (
        f"Uploaded 2/5 files onto server {DSP_INGEST_URL}. Failed to upload the following 3 files:\n"
        " - path1: reason1\n"
        " - path2: reason2\n"
        " - path3: reason3"
    )
    assert msg == expected


def test_all_failures() -> None:
    f1 = UploadFailureDetail(Path("path1"), "reason1")
    f2 = UploadFailureDetail(Path("path2"), "reason2")
    f3 = UploadFailureDetail(Path("path3"), "reason3")
    failures: list[UploadFailureDetail | None] = [f1, f2, f3]
    aggregated_failures = UploadFailureDetails(failures, SHORTCODE, DSP_INGEST_URL)
    msg = aggregated_failures.execute_error_protocol()
    expected = (
        f"Uploaded 0/3 files onto server {DSP_INGEST_URL}. Failed to upload the following 3 files:\n"
        " - path1: reason1\n"
        " - path2: reason2\n"
        " - path3: reason3"
    )
    assert msg == expected


def test_several_failures_with_file_writing() -> None:
    f1 = UploadFailureDetail(Path("path1"), "reason1")
    f2 = UploadFailureDetail(Path("path2"), "reason2")
    f3 = UploadFailureDetail(Path("path3"), "reason3")
    failures: list[UploadFailureDetail | None] = [None, f1, None, f2, f3]
    aggregated_failures = UploadFailureDetails(failures, SHORTCODE, DSP_INGEST_URL, maximum_prints=2)
    msg = aggregated_failures.execute_error_protocol()
    expected_output_path = Path(f"upload_failures_{SHORTCODE}_ingest.test.dasch.swiss.csv")
    expected = (
        f"Uploaded 2/5 files onto server {DSP_INGEST_URL}. Failed to upload 3 files. "
        f"The full list of failed files has been saved to '{expected_output_path}'."
    )
    assert msg == expected

    df = pd.read_csv(expected_output_path)
    assert df["Filepath"].tolist() == ["path1", "path2", "path3"]
    assert df["Reason"].tolist() == ["reason1", "reason2", "reason3"]
    expected_output_path.unlink()
