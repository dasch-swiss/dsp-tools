import json
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.project.get.get import get_project
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers

################################################################################
# NOTE
# This is still quite minimal.
# More thorough testing is done in test/legacy_e2e/test_create_get_xmlupload.py.
# In the future, the legacy tests should be migrated to this file.
################################################################################

TESTFILE_PATH = Path("testdata/json-project/test-project-e2e.json")
PROJECT_SHORTCODE = "4125"


@pytest.fixture(scope="module")
def container_ports() -> Iterator[ExternalContainerPorts]:
    with get_containers() as metadata:
        yield metadata.ports


@pytest.fixture(scope="module")
def creds(container_ports: ExternalContainerPorts) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_ports.api}",
        f"http://0.0.0.0:{container_ports.ingest}",
    )


@pytest.fixture(scope="module")
def _create_project(creds: ServerCredentials) -> None:
    assert create_project(TESTFILE_PATH, creds, verbose=True)


@pytest.fixture(scope="module")
def _original_project() -> dict[str, Any]:
    result: dict[str, Any] = json.loads(TESTFILE_PATH.read_text())
    return result


@pytest.fixture(scope="module")
def _retrieved_project(_create_project: None, creds: ServerCredentials) -> Iterator[dict[str, Any]]:
    with TemporaryDirectory() as tmpdir:
        retrieved_project = Path(f"{tmpdir}/retrieved_project.json")
        get_project(PROJECT_SHORTCODE, str(retrieved_project), creds, verbose=True)
        yield json.loads(retrieved_project.read_text())


def test_get_functionality(_original_project: dict[str, Any], _retrieved_project: dict[str, Any]) -> None:  # noqa: PT019
    assert _original_project["project"]["default_permissions"] == _retrieved_project["project"]["default_permissions"]
    assert (
        _original_project["project"]["default_permissions_overrule"]
        == _retrieved_project["project"]["default_permissions_overrule"]
    )
