import urllib.parse
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests
from pytest_unordered import unordered

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers

PROJECT_SHORTCODE = "4125"
E2E_TESTONTO_PREFIX = "e2e-testonto"
SECOND_ONTO_PREFIX = "second-onto"
PROPS_IN_ONTO_JSON = 1
RESCLASSES_IN_ONTO_JSON = 2
USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"


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
    assert create_project(Path("testdata/json-project/test-project-e2e.json"), creds, verbose=True)


@pytest.mark.usefixtures("_create_project")
def test_get_functionality() -> None:
    pytest.fail("implement this")
