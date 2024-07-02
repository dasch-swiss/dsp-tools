from pathlib import Path
from typing import Iterator

import pandas as pd
import pytest
from pytest_unordered import unordered

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files import ingest_files
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import upload_files
from dsp_tools.commands.project.create.project_create import create_project
from test.e2e.setup_testcontainers import get_containers

CREDS = ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")
XML_FILE = Path("testdata/xml-data/test-data-e2e.xml")
SHORTCODE = "4125"


@pytest.fixture(scope="module")
def mapping_file() -> Iterator[Path]:
    mapping_file = Path(f"mapping-{SHORTCODE}.csv")
    yield mapping_file
    mapping_file.unlink(missing_ok=True)


@pytest.fixture()
def _create_project() -> Iterator[None]:
    with get_containers():
        success = create_project(Path("testdata/json-project/test-project-e2e.json"), CREDS, verbose=True)
        assert success
        yield


@pytest.mark.usefixtures("_create_project")
def test_ingest_upload(caplog: pytest.LogCaptureFixture, mapping_file: Path) -> None:
    _test_upload_step(caplog)
    _test_ingest_step(caplog, mapping_file)


def _test_upload_step(caplog: pytest.LogCaptureFixture) -> None:
    success = upload_files(XML_FILE, CREDS)
    assert success
    log_messages = [rec.message for rec in caplog.records]
    assert "Found 2 files" in log_messages[-6]
    assert "Uploaded file 'testdata/bitstreams/test.jpg'" in log_messages[-3]
    assert "Uploaded file 'testdata/bitstreams/test.pdf'" in log_messages[-2]
    assert "Uploaded all 2 files" in log_messages[-1]
    caplog.clear()


def _test_ingest_step(caplog: pytest.LogCaptureFixture, mapping_file: Path) -> None:
    success = ingest_files(CREDS, SHORTCODE)
    assert success
    logs = [rec.message for rec in caplog.records]
    assert logs[-3] == "Kicked off the ingest process on the server http://0.0.0.0:3340. Wait until it completes..."
    assert logs[-2] == "Ingest process completed."
    assert logs[-1] == f"Saved mapping CSV to '{mapping_file}'"
    caplog.clear()

    df = pd.read_csv(mapping_file)
    assert df["original"].tolist() == unordered(["testdata/bitstreams/test.jpg", "testdata/bitstreams/test.pdf"])
