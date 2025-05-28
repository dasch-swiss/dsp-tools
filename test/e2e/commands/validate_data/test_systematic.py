# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.validate_data import validate_data
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
    creds = ServerCredentials("root@example.com", "test", api_url)
    no_violations = validate_data(file, creds, save_graphs=False)
    assert no_violations
