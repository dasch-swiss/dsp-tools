from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.validate_data import _get_parsed_graphs
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts

# ruff: noqa: ARG001 Unused function argument


@pytest.fixture(scope="module")
def create_project_systematic(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/json-project/test-project-systematic.json"), creds)


@pytest.fixture(scope="module")
def api_url(container_ports: ExternalContainerPorts) -> str:
    return f"http://0.0.0.0:{container_ports.api}"


@pytest.fixture(scope="module")
def shacl_validator(api_url: str) -> ShaclValidator:
    return ShaclValidator(api_url)


@pytest.mark.usefixtures("create_project_systematic")
def test_systematic(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/xml-data/test-data-systematic.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    systematic_correct = _get_validation_result(graphs, shacl_validator, None)
    assert not systematic_correct.conforms  # This test will be correct as soon as legal information is mandatory
