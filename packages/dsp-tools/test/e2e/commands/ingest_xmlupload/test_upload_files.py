from collections.abc import Iterator
from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.create import create
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import upload_files
from test.e2e.setup_testcontainers.containers import ContainerMetadata
from test.e2e.setup_testcontainers.setup import get_containers

PROJECT_FILE = Path("testdata/json-project/systematic-project-4123.json")
XML_FILE = Path("testdata/xml-data/test-data-systematic-4123.xml")
SHORTCODE = "4123"
EXIT_IF_EXISTS = True
EXPECTED_FILE_COUNT = 41


@pytest.fixture(scope="module")
def container_metadata() -> Iterator[ContainerMetadata]:
    with get_containers() as metadata:
        yield metadata


@pytest.fixture(scope="module")
def tmp_folder(container_metadata: ContainerMetadata) -> Path:
    return container_metadata.artifact_dirs.tmp_ingest / "import" / SHORTCODE


@pytest.fixture(scope="module")
def creds(container_metadata: ContainerMetadata) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_metadata.ports.api}",
        f"http://0.0.0.0:{container_metadata.ports.ingest}",
    )


@pytest.fixture(scope="module")
def _create_project(creds: ServerCredentials) -> None:
    assert create(PROJECT_FILE, creds, EXIT_IF_EXISTS)


@pytest.mark.usefixtures("_create_project")
def test_upload_files_with_placeholder(creds: ServerCredentials, tmp_folder: Path) -> None:
    success = upload_files(XML_FILE, creds, Path(".").absolute())
    assert success
    uploaded = {x.relative_to(tmp_folder) for x in tmp_folder.glob("**/*.*")}
    assert len(uploaded) == EXPECTED_FILE_COUNT
