from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import upload_files
from dsp_tools.commands.project.create.project_create import create_project
from test.e2e.setup_testcontainers import get_containers

CREDS = ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")
XML_FILE = Path("testdata/xml-data/test-data-e2e.xml")


@pytest.fixture()
def _create_project() -> Iterator[None]:
    with get_containers():
        success = create_project(Path("testdata/json-project/test-project-e2e.json"), CREDS, verbose=True)
        assert success
        yield


@pytest.mark.usefixtures("_create_project")
def test_ingest_upload(caplog: pytest.LogCaptureFixture) -> None:
    _test_upload_step(caplog)


def _test_upload_step(caplog: pytest.LogCaptureFixture) -> None:
    success = upload_files(XML_FILE, CREDS)
    assert success
    log_messages = [rec.message for rec in caplog.records]
    assert log_messages[0] == f"Found 2 files to upload onto server {CREDS.dsp_ingest_url}."
    assert log_messages[1] == "Uploaded file 'testdata/bitstreams/test.jpg'"
    assert log_messages[2] == "Uploaded file 'testdata/bitstreams/test.pdf'"
    assert log_messages[3] == f"Uploaded all 2 files onto server {CREDS.dsp_ingest_url}."
    caplog.clear()
