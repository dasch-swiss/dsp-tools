from pathlib import Path

import pytest
from requests_mock import Mocker

from dsp_tools.commands.xmlupload.models.mass_ingest_client import MassIngestClient
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError


@pytest.fixture()
def dsp_ingest_url() -> str:
    return "https://example.com"


@pytest.fixture()
def shortcode() -> str:
    return "0001"


@pytest.fixture()
def ingest_client(dsp_ingest_url: str, shortcode: str) -> MassIngestClient:
    return MassIngestClient(dsp_ingest_url, "token", shortcode)


@pytest.fixture()
def tmp_file(tmp_path: Path) -> Path:
    return tmp_path / "filename.xml"


def _make_url(dsp_ingest_url: str, shortcode: str, file: Path) -> str:
    return f"{dsp_ingest_url}/projects/{shortcode}/bulk-ingest/upload/{file.name}"


def test_ingest_success(
    dsp_ingest_url: str, ingest_client: MassIngestClient, requests_mock: Mocker, shortcode: str, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    url = _make_url(dsp_ingest_url, shortcode, tmp_file)
    requests_mock.post(url, status_code=200)
    success = ingest_client.upload_file(tmp_file)
    assert success
    assert len(requests_mock.request_history) == 1
    req = requests_mock.request_history[0]
    assert req.url == url
    assert req.method == "POST"
    assert req.headers["Authorization"] == "Bearer token"
    assert req.headers["Content-Type"] == "application/octet-stream"
    assert req.body.name == str(tmp_file)


def test_ingest_failure_when_authentication_error(
    dsp_ingest_url: str, ingest_client: MassIngestClient, requests_mock: Mocker, shortcode: str, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(dsp_ingest_url, shortcode, tmp_file), status_code=401)
    with pytest.raises(BadCredentialsError):
        ingest_client._upload(tmp_file)


def test_ingest_failure_when_other_error(
    dsp_ingest_url: str, ingest_client: MassIngestClient, requests_mock: Mocker, shortcode: str, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(dsp_ingest_url, shortcode, tmp_file), status_code=500)
    with pytest.raises(PermanentConnectionError):
        ingest_client._upload(tmp_file)
