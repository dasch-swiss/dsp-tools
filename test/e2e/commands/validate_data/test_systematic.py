from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.validate_data import _get_parsed_graphs
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
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
def _create_projects(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/json-project/test-project-systematic.json"), creds)


@pytest.fixture(scope="module")
def api_con(container_ports: ExternalContainerPorts) -> ApiConnection:
    return ApiConnection(f"http://0.0.0.0:{container_ports.api}")


@pytest.fixture(scope="module")
def shacl_validator(api_con: ApiConnection) -> ShaclValidator:
    return ShaclValidator(api_con)


@pytest.mark.usefixtures("_create_projects")
def test_systematic(api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/xml-data/test-data-systematic.xml")
    graphs = _get_parsed_graphs(api_con, file)
    systematic_correct = _get_validation_result(graphs, shacl_validator, None)
    assert not systematic_correct.conforms  # This test will be correct as soon as legal information is mandatory
