import json
import re
import urllib
from pathlib import Path

import pytest
from requests import RequestException
from requests_mock import Mocker

from dsp_tools.commands.ingest_xmlupload.bulk_ingest_client import BulkIngestClient
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import UserError

DSP_INGEST_URL = "https://example.com"
SHORTCODE = "0001"


@pytest.fixture
def ingest_client() -> BulkIngestClient:
    return BulkIngestClient(DSP_INGEST_URL, "token", SHORTCODE)


@pytest.fixture
def tmp_file(tmp_path: Path) -> Path:
    return tmp_path / "filename_îïôœùûüÿ.xml"


def _make_url(file: Path) -> str:
    filename = urllib.parse.quote(str(file))
    return f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest/ingest/{filename}"


def test_upload_file_success(ingest_client: BulkIngestClient, requests_mock: Mocker, tmp_file: Path) -> None:
    file_content = "<xml></xml>"
    tmp_file.write_text(file_content)
    url = _make_url(tmp_file)
    requests_mock.post(url, status_code=200)
    failure_detail = ingest_client.upload_file(tmp_file)
    assert not failure_detail
    assert len(requests_mock.request_history) == 1
    req = requests_mock.request_history[0]
    assert req.url == url
    assert req.method == "POST"
    assert req.headers["Authorization"] == "Bearer token"
    assert req.headers["Content-Type"] == "application/octet-stream"
    assert req.body == file_content.encode()


def test_upload_file_with_inexisting_file(ingest_client: BulkIngestClient) -> None:
    failure_detail = ingest_client.upload_file(Path("inexisting.xml"))
    assert failure_detail
    assert failure_detail.filepath == Path("inexisting.xml")
    assert failure_detail.reason == "File could not be opened/read: No such file or directory"


def test_upload_file_failure_upon_request_exception(
    ingest_client: BulkIngestClient, requests_mock: Mocker, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(tmp_file), exc=RequestException("Test exception"))
    failure_detail = ingest_client.upload_file(tmp_file)
    assert failure_detail
    assert failure_detail.filepath == tmp_file
    assert failure_detail.reason == "Exception of requests library: Test exception"


def test_upload_file_failure_upon_server_error(
    ingest_client: BulkIngestClient, requests_mock: Mocker, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(tmp_file), status_code=500)
    failure_detail = ingest_client.upload_file(tmp_file)
    assert failure_detail
    assert failure_detail.filepath == tmp_file
    assert failure_detail.reason == "Response 500"


def test_upload_file_failure_upon_server_error_with_response_text(
    ingest_client: BulkIngestClient, requests_mock: Mocker, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(tmp_file), status_code=500, text="response text")
    failure_detail = ingest_client.upload_file(tmp_file)
    assert failure_detail
    assert failure_detail.filepath == tmp_file
    assert failure_detail.reason == "Response 500: response text"


def test_trigger_if_success(ingest_client: BulkIngestClient, requests_mock: Mocker) -> None:
    url = f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest"
    requests_mock.post(url, status_code=202, text=json.dumps({"id": SHORTCODE}))
    ingest_client.trigger_ingest_process()
    assert len(requests_mock.request_history) == 1
    req = requests_mock.request_history[0]
    assert req.url == url
    assert req.method == "POST"
    assert req.headers["Authorization"] == "Bearer token"


def test_trigger_if_unauthorized(ingest_client: BulkIngestClient, requests_mock: Mocker) -> None:
    url = f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest"
    requests_mock.post(url, status_code=401)
    with pytest.raises(BadCredentialsError):
        ingest_client.trigger_ingest_process()


def test_trigger_if_forbidden(ingest_client: BulkIngestClient, requests_mock: Mocker) -> None:
    url = f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest"
    requests_mock.post(url, status_code=403)
    with pytest.raises(BadCredentialsError):
        ingest_client.trigger_ingest_process()


def test_trigger_wrong_shortcode(ingest_client: BulkIngestClient, requests_mock: Mocker) -> None:
    ingest_client.shortcode = "9999"
    url = f"{DSP_INGEST_URL}/projects/9999/bulk-ingest"
    requests_mock.post(url, status_code=404)
    err_msg = re.escape(
        "No assets have been uploaded for project 9999. "
        "Before using the 'ingest-files' command, you must upload some files with the 'upload-files' command."
    )
    with pytest.raises(UserError, match=err_msg):
        ingest_client.trigger_ingest_process()


def test_trigger_when_ingest_already_running(
    ingest_client: BulkIngestClient, requests_mock: Mocker, capsys: pytest.CaptureFixture[str]
) -> None:
    url = f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest"
    requests_mock.post(url, status_code=409)
    ingest_client.trigger_ingest_process()
    expected = f"Ingest process on the server {DSP_INGEST_URL} is already running. Wait until it completes..."
    captured = capsys.readouterr().out.removesuffix("\n")
    assert captured == expected


def test_trigger_on_internal_server_error(ingest_client: BulkIngestClient, requests_mock: Mocker) -> None:
    url = f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest"
    requests_mock.post(url, status_code=500)
    with pytest.raises(UserError, match=re.escape("Server is unavailable. Please try again later.")):
        ingest_client.trigger_ingest_process()


def test_trigger_on_server_unavailable(ingest_client: BulkIngestClient, requests_mock: Mocker) -> None:
    url = f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest"
    requests_mock.post(url, status_code=503)
    with pytest.raises(UserError, match=re.escape("Server is unavailable. Please try again later.")):
        ingest_client.trigger_ingest_process()


def test_trigger_when_server_response_doesnt_contain_right_shortcode(
    ingest_client: BulkIngestClient, requests_mock: Mocker
) -> None:
    url = f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest"
    requests_mock.post(url, status_code=202)
    err_msg = re.escape("Failed to trigger the ingest process. Please check the server logs, or try again later.")
    with pytest.raises(UserError, match=err_msg):
        ingest_client.trigger_ingest_process()
