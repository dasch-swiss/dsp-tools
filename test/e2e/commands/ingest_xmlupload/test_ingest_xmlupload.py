from pathlib import Path
from typing import Iterator

import pandas as pd
import pytest
import regex
from pytest_unordered import unordered

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml import ingest_xmlupload
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
    _test_xmlupload_step(caplog)


def _test_upload_step(caplog: pytest.LogCaptureFixture) -> None:
    success = upload_files(XML_FILE, CREDS)
    assert success
    log_messages = [rec.message for rec in caplog.records]
    assert log_messages[0] == f"Found 2 files to upload onto server {CREDS.dsp_ingest_url}."
    assert log_messages[-3] == "Uploaded file 'testdata/bitstreams/test.jpg'"
    assert log_messages[-2] == "Uploaded file 'testdata/bitstreams/test.pdf'"
    assert log_messages[-1] == f"Uploaded all 2 files onto server {CREDS.dsp_ingest_url}."
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


def _test_xmlupload_step(caplog: pytest.LogCaptureFixture) -> None:
    success = ingest_xmlupload(XML_FILE, CREDS)
    assert success
    logs = [rec.message for rec in caplog.records]
    expected_logs = [
        "The file 'mapping-4125.csv' is used to map the internal original filepaths to the internal image IDs.",
        (
            "All multimedia files referenced in the XML file were uploaded through dsp-ingest.\n"
            "All multimedia files uploaded through dsp-ingest were referenced in the XML file."
        ),
    ]
    assert all(expected_log in logs for expected_log in expected_logs)
    expected_log_regexes = [
        "Created resource 1/3",
        "Created resource 2/3",
        "Created resource 3/3",
    ]
    assert all(any(regex.search(exp, log) for log in logs) for exp in expected_log_regexes)
    caplog.clear()
