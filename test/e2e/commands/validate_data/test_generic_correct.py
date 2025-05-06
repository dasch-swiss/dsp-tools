from collections.abc import Iterator
from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
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
    graphs, _ = _get_parsed_graphs(api_url, file)
    cardinality_correct = _get_validation_result(graphs, shacl_validator, None)
    assert cardinality_correct.conforms


@pytest.mark.usefixtures("_create_projects")
def test_content_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/content_correct.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    content_correct = _get_validation_result(graphs, shacl_validator, None)
    # The referenced absolute IRIs are perceived as a violation in SHACL
    # because the resource does not exist in the graph
    assert not content_correct.conforms
    reformatted = reformat_validation_graph(content_correct)
    sorted_messages = sort_user_problems(reformatted)
    assert not sorted_messages.unique_violations
    assert len(sorted_messages.user_info) == 1
    assert not sorted_messages.unexpected_shacl_validation_components


@pytest.fixture(scope="module")
def minimal_correct_graphs(_create_projects: Iterator[None], api_url: str) -> tuple[RDFGraphs, set[str]]:
    file = Path("testdata/validate-data/generic/minimal_correct.xml")
    return _get_parsed_graphs(api_url, file)


def test_minimal_correct(minimal_correct_graphs: tuple[RDFGraphs, set[str]], shacl_validator: ShaclValidator) -> None:
    graphs, _ = minimal_correct_graphs
    minimal_correct = _get_validation_result(graphs, shacl_validator, None)
    assert minimal_correct.conforms


def test_check_for_unknown_resource_classes(minimal_correct_graphs: tuple[RDFGraphs, set[str]]) -> None:
    graphs, used_iris = minimal_correct_graphs
    result = _check_for_unknown_resource_classes(graphs, used_iris)
    assert not result


@pytest.mark.usefixtures("_create_projects")
def test_file_value_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/file_value_correct.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    file_value_correct = _get_validation_result(graphs, shacl_validator, None)
    assert file_value_correct.conforms


@pytest.mark.usefixtures("_create_projects")
def test_dsp_inbuilt_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/dsp_inbuilt_correct.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    dsp_inbuilt_correct = _get_validation_result(graphs, shacl_validator, None)
    assert dsp_inbuilt_correct.conforms
