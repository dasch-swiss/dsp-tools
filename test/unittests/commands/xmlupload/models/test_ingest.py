from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.models.ingest import AssetClient
from dsp_tools.commands.xmlupload.models.ingest import DspIngestClientLive
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.utils.connection_live import ConnectionLive


@pytest.fixture()
def dsp_ingest_url() -> str:
    return "https://example.com"


@pytest.fixture()
def shortcode() -> str:
    return "0001"


@pytest.fixture()
def ingest_client(dsp_ingest_url: str, shortcode: str) -> AssetClient:
    return DspIngestClientLive(ConnectionLive(dsp_ingest_url), shortcode, ".")


@pytest.fixture()
def tmp_file(tmp_path: Path) -> Path:
    return tmp_path / "filename.xml"


def _make_url(dsp_ingest_url: str, shortcode: str, file: Path) -> str:
    return f"{dsp_ingest_url}/projects/{shortcode}/assets/ingest/{file.name}"


def test_ingest_success(dsp_ingest_url, ingest_client, requests_mock, shortcode, tmp_file):  # type: ignore[no-untyped-def]
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(dsp_ingest_url, shortcode, tmp_file), json={"internalFilename": tmp_file.name})
    res = ingest_client._ingest(tmp_file)
    assert res.internal_filename == tmp_file.name


def test_ingest_failure_when_file_not_found(ingest_client, tmp_file):  # type: ignore[no-untyped-def]
    with pytest.raises(FileNotFoundError):
        ingest_client._ingest(tmp_file)


def test_ingest_failure_when_other_error(dsp_ingest_url, ingest_client, requests_mock, shortcode, tmp_file):  # type: ignore[no-untyped-def]
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(_make_url(dsp_ingest_url, shortcode, tmp_file), status_code=500)
    with pytest.raises(PermanentConnectionError):
        ingest_client._ingest(tmp_file)
