from pathlib import Path

import pytest
from requests_mock import Mocker

from dsp_tools.commands.xmlupload.models.mass_ingest_client import MassIngestClient
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError

DSP_INGEST_URL = "https://example.com"
SHORTCODE = "0001"


@pytest.fixture()
def ingest_client() -> MassIngestClient:
    return MassIngestClient(DSP_INGEST_URL, "token", SHORTCODE)


@pytest.fixture()
def tmp_file(tmp_path: Path) -> Path:
    return tmp_path / "filename.xml"


def _make_url(file: Path) -> str:
    return f"{DSP_INGEST_URL}/projects/{SHORTCODE}/bulk-ingest/upload/{file.name}"


def test_ingest_success(ingest_client: MassIngestClient, requests_mock: Mocker, tmp_file: Path) -> None:
    tmp_file.write_text("<xml></xml>")
    url = _make_url(DSP_INGEST_URL, SHORTCODE, tmp_file)
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
    ingest_client: MassIngestClient, requests_mock: Mocker, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(DSP_INGEST_URL, SHORTCODE, tmp_file), status_code=401)
    with pytest.raises(BadCredentialsError):
        ingest_client._upload(tmp_file)


def test_ingest_failure_when_other_error(
    ingest_client: MassIngestClient, requests_mock: Mocker, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(DSP_INGEST_URL, SHORTCODE, tmp_file), status_code=500)
    with pytest.raises(PermanentConnectionError):
        ingest_client._upload(tmp_file)
