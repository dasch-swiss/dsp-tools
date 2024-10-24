import urllib
from pathlib import Path

import pytest
from requests_mock import Mocker

from dsp_tools.commands.xmlupload.models.ingest import DspIngestClientLive
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError
from test.integration.commands.xmlupload.authentication_client_mock import AuthenticationClientMockBase


@pytest.fixture
def dsp_ingest_url() -> str:
    return "https://example.com"


@pytest.fixture
def shortcode() -> str:
    return "0001"


@pytest.fixture
def ingest_client(dsp_ingest_url: str, shortcode: str) -> DspIngestClientLive:
    return DspIngestClientLive(dsp_ingest_url, AuthenticationClientMockBase(), shortcode, ".")


@pytest.fixture
def tmp_file(tmp_path: Path) -> Path:
    return tmp_path / "éèêëàâæç îïôœùûüÿ.xml"


def _make_url(dsp_ingest_url: str, shortcode: str, file: Path) -> str:
    filename = urllib.parse.quote(file.name)
    return f"{dsp_ingest_url}/projects/{shortcode}/assets/ingest/{filename}"


def test_ingest_success(
    dsp_ingest_url: str, ingest_client: DspIngestClientLive, requests_mock: Mocker, shortcode: str, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(dsp_ingest_url, shortcode, tmp_file), json={"internalFilename": tmp_file.name})
    res = ingest_client._ingest(tmp_file)
    assert res.internal_filename == tmp_file.name


def test_ingest_failure_when_file_not_found(ingest_client: DspIngestClientLive, tmp_file: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ingest_client._ingest(tmp_file)


def test_ingest_failure_when_authentication_error(
    dsp_ingest_url: str, ingest_client: DspIngestClientLive, requests_mock: Mocker, shortcode: str, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(dsp_ingest_url, shortcode, tmp_file), status_code=401)
    with pytest.raises(BadCredentialsError):
        ingest_client._ingest(tmp_file)


def test_ingest_failure_when_other_error(
    dsp_ingest_url: str, ingest_client: DspIngestClientLive, requests_mock: Mocker, shortcode: str, tmp_file: Path
) -> None:
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(dsp_ingest_url, shortcode, tmp_file), status_code=500)
    with pytest.raises(PermanentConnectionError):
        ingest_client._ingest(tmp_file)
