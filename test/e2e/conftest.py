from collections.abc import Iterator
from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers


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
def api_url(container_ports: ExternalContainerPorts) -> str:
    return f"http://0.0.0.0:{container_ports.api}"


@pytest.fixture(scope="module")
def shacl_validator(api_url: str) -> ShaclValidator:
    return ShaclValidator(api_url)


@pytest.fixture(scope="module")
def create_generic_project(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/validate-data/generic/project.json"), creds)
