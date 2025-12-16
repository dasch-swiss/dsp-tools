# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.metadata_client import ExistingResourcesRetrieved
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validate_data import _validate_data
from test.e2e.commands.validate_data.util import prepare_data_for_validation_from_file

# ruff: noqa: ARG001 Unused function argument

CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=True,
    skip_ontology_validation=False,
    do_not_request_resource_metadata_from_db=False,
)
SHORTCODE = "9999"
METADATA_RETRIEVAL_SUCCESS = ExistingResourcesRetrieved.TRUE


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.mark.usefixtures("create_generic_project")
def test_minimal_correct(authentication) -> None:
    file = Path("testdata/validate-data/core_validation/minimal_correct.xml")
    graphs, triple_stores, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    validation_result = _validate_data(
        graphs, triple_stores, used_iris, parsed_resource, CONFIG, SHORTCODE, METADATA_RETRIEVAL_SUCCESS
    )
    assert validation_result.no_problems
    assert not validation_result.problems
    assert not validation_result.report_graphs


@pytest.mark.usefixtures("create_generic_project")
def test_cardinality_correct(authentication, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/core_validation/cardinality_correct.xml")
    graphs, triple_stores, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    validation_result = _validate_data(
        graphs, triple_stores, used_iris, parsed_resource, CONFIG, SHORTCODE, METADATA_RETRIEVAL_SUCCESS
    )
    assert validation_result.no_problems
    assert not validation_result.problems
    assert not validation_result.report_graphs


@pytest.mark.usefixtures("create_generic_project")
def test_content_correct(authentication, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/core_validation/content_correct.xml")
    graphs, triple_stores, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    validation_result = _validate_data(
        graphs, triple_stores, used_iris, parsed_resource, CONFIG, SHORTCODE, METADATA_RETRIEVAL_SUCCESS
    )
    assert validation_result.no_problems
    assert not validation_result.problems
    assert not validation_result.report_graphs


@pytest.mark.usefixtures("create_generic_project")
def test_file_value_correct(authentication, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/core_validation/file_value_correct.xml")
    graphs, triple_stores, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    validation_result = _validate_data(
        graphs, triple_stores, used_iris, parsed_resource, CONFIG, SHORTCODE, METADATA_RETRIEVAL_SUCCESS
    )
    assert validation_result.no_problems
    assert not validation_result.problems
    assert not validation_result.report_graphs


@pytest.mark.usefixtures("create_generic_project")
def test_dsp_inbuilt_correct(authentication, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/core_validation/dsp_inbuilt_correct.xml")
    graphs, triple_stores, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    validation_result = _validate_data(
        graphs, triple_stores, used_iris, parsed_resource, CONFIG, SHORTCODE, METADATA_RETRIEVAL_SUCCESS
    )
    assert validation_result.no_problems
    assert not validation_result.problems
    assert not validation_result.report_graphs
