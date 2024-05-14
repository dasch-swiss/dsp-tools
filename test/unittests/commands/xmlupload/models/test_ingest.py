import pytest

from dsp_tools.commands.xmlupload.models.ingest import DspIngestClient
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import UserError


def test_ingest(tmp_path, requests_mock):
    dsp_ingest_url = "http://example.com"
    shortcode = "0001"
    filename = "filename.xml"
    p = tmp_path / filename
    p.write_text("<xml></xml>")
    client = DspIngestClient(dsp_ingest_url, "token")
    requests_mock.post(
        f"{dsp_ingest_url}/projects/{shortcode}/assets/ingest/{filename}", json={"internalFilename": filename}
    )
    res = client.ingest(shortcode, p)
    assert res.internal_filename == filename


def test_ingest_failure_when_file_not_found(tmp_path):
    dsp_ingest_url = "http://example.com"
    shortcode = "0001"
    filename = "filename.xml"
    p = tmp_path / filename
    client = DspIngestClient(dsp_ingest_url, "token")
    with pytest.raises(UserError):
        client.ingest(shortcode, p)


def test_ingest_failure_when_authentication_error(tmp_path, requests_mock):
    dsp_ingest_url = "http://example.com"
    shortcode = "0001"
    filename = "filename.xml"
    p = tmp_path / filename
    p.write_text("<xml></xml>")
    client = DspIngestClient(dsp_ingest_url, "token")
    requests_mock.post(f"{dsp_ingest_url}/projects/{shortcode}/assets/ingest/{filename}", status_code=401)
    with pytest.raises(BadCredentialsError):
        client.ingest(shortcode, p)


def test_ingest_failure_when_other_error(tmp_path, requests_mock):
    dsp_ingest_url = "http://example.com"
    shortcode = "0001"
    filename = "filename.xml"
    p = tmp_path / filename
    p.write_text("<xml></xml>")
    client = DspIngestClient(dsp_ingest_url, "token")
    requests_mock.post(f"{dsp_ingest_url}/projects/{shortcode}/assets/ingest/{filename}", status_code=500)
    with pytest.raises(PermanentConnectionError):
        client.ingest(shortcode, p)
