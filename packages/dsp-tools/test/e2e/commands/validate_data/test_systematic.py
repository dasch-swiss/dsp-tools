from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.create import create
from dsp_tools.commands.validate_data.validate_data import validate_data
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts

EXIT_IF_EXISTS = True


@pytest.fixture(scope="module")
def create_project_systematic(creds: ServerCredentials) -> None:
    assert create(Path("testdata/json-project/systematic-project-4123.json"), creds, EXIT_IF_EXISTS)


@pytest.fixture(scope="module")
def api_url(container_ports: ExternalContainerPorts) -> str:
    return f"http://0.0.0.0:{container_ports.api}"


@pytest.mark.usefixtures("create_project_systematic")
def test_systematic(api_url: str) -> None:
    file = Path("testdata/xml-data/test-data-systematic-4123.xml")
    creds = ServerCredentials("root@example.com", "test", api_url)
    no_violations = validate_data(
        file,
        creds,
        ignore_duplicate_files_warning=False,
        save_graphs=False,
        skip_ontology_validation=False,
        id2iri_file=None,
        do_not_request_resource_metadata_from_db=True,
    )
    assert no_violations
