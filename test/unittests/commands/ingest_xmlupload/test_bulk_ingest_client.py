from pathlib import Path

import pytest
from requests import RequestException
from requests_mock import Mocker

from dsp_tools.commands.ingest_xmlupload.bulk_ingest_client import BulkIngestClient

DSP_INGEST_URL = "https://example.com"
SHORTCODE = "0001"


@pytest.fixture()
def ingest_client() -> BulkIngestClient:
    return BulkIngestClient(DSP_INGEST_URL, "token", SHORTCODE)


@pytest.fixture()
def tmp_file(tmp_path: Path) -> Path:
    return tmp_path / "filename.xml"


def _make_url(file: Path) -> str:
    return f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest/ingest/{file}"


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
