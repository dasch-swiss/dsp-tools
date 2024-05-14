from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.models.ingest import DspIngestClient
from dsp_tools.commands.xmlupload.models.ingest import IngestClient
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import UserError


@pytest.fixture()
def dsp_ingest_url() -> str:
    return "https://example.com"


@pytest.fixture()
def ingest_client(dsp_ingest_url) -> IngestClient:
    return DspIngestClient(dsp_ingest_url, "token")


@pytest.fixture()
def shortcode() -> str:
    return "0001"


@pytest.fixture()
def tmp_file(tmp_path) -> Path:
    return tmp_path / "filename.xml"


def test_ingest_success(dsp_ingest_url, ingest_client, requests_mock, shortcode, tmp_file):
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(
        f"{dsp_ingest_url}/projects/{shortcode}/assets/ingest/{tmp_file.name}", json={"internalFilename": tmp_file.name}
    )
    res = ingest_client.ingest(shortcode, tmp_file)
    assert res.internal_filename == tmp_file.name


def test_ingest_failure_when_file_not_found(ingest_client, shortcode, tmp_file):
    with pytest.raises(UserError):
        ingest_client.ingest(shortcode, tmp_file)


def test_ingest_failure_when_authentication_error(dsp_ingest_url, ingest_client, requests_mock, shortcode, tmp_file):
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(f"{dsp_ingest_url}/projects/{shortcode}/assets/ingest/{tmp_file.name}", status_code=401)
    with pytest.raises(BadCredentialsError):
        ingest_client.ingest(shortcode, tmp_file)


def test_ingest_failure_when_other_error(dsp_ingest_url, ingest_client, requests_mock, shortcode, tmp_file):
    tmp_file.write_text("<xml></xml>")
    requests_mock.post(f"{dsp_ingest_url}/projects/{shortcode}/assets/ingest/{tmp_file.name}", status_code=500)
    with pytest.raises(PermanentConnectionError):
        ingest_client.ingest(shortcode, tmp_file)
