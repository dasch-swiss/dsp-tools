from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import upload_files
from dsp_tools.commands.project.create.project_create import create_project
from test.e2e.setup_testcontainers import SIPI_PATH_TMP_INGEST
from test.e2e.setup_testcontainers import get_containers

CREDS = ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")
XML_FILE = Path("testdata/xml-data/test-data-e2e.xml")
TMP_FOLDER = SIPI_PATH_TMP_INGEST / "import" / "4125" / "testdata" / "bitstreams"


@pytest.fixture()
def _create_project() -> Iterator[None]:
    with get_containers():
        success = create_project(Path("testdata/json-project/test-project-e2e.json"), CREDS, verbose=True)
        assert success
        yield


@pytest.mark.usefixtures("_create_project")
def test_ingest_upload() -> None:
    _test_upload_step()


def _test_upload_step() -> None:
    success = upload_files(XML_FILE, CREDS)
    assert success
    assert set(TMP_FOLDER.iterdir()) == {TMP_FOLDER / "test.jpg", TMP_FOLDER / "test.pdf"}
