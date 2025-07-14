# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validate_data import _validate_data
from test.e2e_validate_data.util import prepare_data_for_validation_from_file

# ruff: noqa: ARG001 Unused function argument

CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=True,
)


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.mark.usefixtures("create_generic_project")
def test_minimal_correct(authentication) -> None:
    file = Path("testdata/validate-data/generic/minimal_correct.xml")
    graphs, used_iris = prepare_data_for_validation_from_file(
        file, authentication, CONFIG.ignore_duplicate_files_warning
    )
    validation_success = _validate_data(graphs, used_iris, CONFIG)
    assert validation_success


@pytest.mark.usefixtures("create_generic_project")
def test_cardinality_correct(authentication, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/generic/cardinality_correct.xml")
    graphs, used_iris = prepare_data_for_validation_from_file(
        file, authentication, CONFIG.ignore_duplicate_files_warning
    )
    validation_success = _validate_data(graphs, used_iris, CONFIG)
    assert validation_success


@pytest.mark.usefixtures("create_generic_project")
def test_content_correct(authentication, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/generic/content_correct.xml")
    graphs, used_iris = prepare_data_for_validation_from_file(
        file, authentication, CONFIG.ignore_duplicate_files_warning
    )
    validation_success = _validate_data(graphs, used_iris, CONFIG)
    assert validation_success


@pytest.mark.usefixtures("create_generic_project")
def test_file_value_correct(authentication, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/generic/file_value_correct.xml")
    graphs, used_iris = prepare_data_for_validation_from_file(
        file, authentication, CONFIG.ignore_duplicate_files_warning
    )
    validation_success = _validate_data(graphs, used_iris, CONFIG)
    assert validation_success


@pytest.mark.usefixtures("create_generic_project")
def test_dsp_inbuilt_correct(authentication, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/generic/dsp_inbuilt_correct.xml")
    graphs, used_iris = prepare_data_for_validation_from_file(
        file, authentication, CONFIG.ignore_duplicate_files_warning
    )
    validation_success = _validate_data(graphs, used_iris, CONFIG)
    assert validation_success
