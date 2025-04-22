from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.validate_data import _check_for_unknown_resource_classes
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
def api_url(container_ports: ExternalContainerPorts) -> str:
    return f"http://0.0.0.0:{container_ports.api}"


@pytest.fixture(scope="module")
def shacl_validator(api_url: str) -> ShaclValidator:
    return ShaclValidator(api_url)


@pytest.fixture(scope="module")
def _create_projects(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/validate-data/generic/project.json"), creds)


@pytest.mark.usefixtures("_create_projects")
def test_cardinality_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/cardinality_correct.xml")
    graphs = _get_parsed_graphs(api_url, file)
    cardinality_correct = _get_validation_result(graphs, shacl_validator, None)
    assert cardinality_correct.conforms


@pytest.mark.usefixtures("_create_projects")
def test_content_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/content_correct.xml")
    graphs = _get_parsed_graphs(api_url, file)
    content_correct = _get_validation_result(graphs, shacl_validator, None)
    assert content_correct.conforms


@pytest.fixture(scope="module")
def minimal_correct_graphs(_create_projects: Iterator[None], api_url: str) -> RDFGraphs:
    file = Path("testdata/validate-data/generic/minimal_correct.xml")
    return _get_parsed_graphs(api_url, file)

def test_minimal_correct(minimal_correct_graphs: RDFGraphs, shacl_validator: ShaclValidator) -> None:
    minimal_correct = _get_validation_result(minimal_correct_graphs, shacl_validator, None)
    assert minimal_correct.conforms


def test_check_for_unknown_resource_classes(minimal_correct_graphs: RDFGraphs) -> None:
    result = _check_for_unknown_resource_classes(minimal_correct_graphs
                                                 )
    assert not result


@pytest.mark.usefixtures("_create_projects")
def test_file_value_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/file_value_correct.xml")
    graphs = _get_parsed_graphs(api_url, file)
    file_value_correct = _get_validation_result(graphs, shacl_validator, None)
    assert file_value_correct.conforms


@pytest.mark.usefixtures("_create_projects")
def test_dsp_inbuilt_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/dsp_inbuilt_correct.xml")
    graphs = _get_parsed_graphs(api_url, file)
    dsp_inbuilt_correct = _get_validation_result(graphs, shacl_validator, None)
    assert dsp_inbuilt_correct.conforms
