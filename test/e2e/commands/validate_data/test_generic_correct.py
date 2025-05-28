# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.validate_data import _prepare_data_for_validation_from_file
from dsp_tools.commands.validate_data.validate_data import _validate_data

# ruff: noqa: ARG001 Unused function argument

CONFIG = ValidateDataConfig(Path(), None, ValidationSeverity.INFO, is_on_prod_server=True)


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.mark.usefixtures("create_generic_project")
def test_minimal_correct(authentication) -> None:
    file = Path("testdata/validate-data/generic/minimal_correct.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    validation_success = _validate_data(graphs, used_iris, authentication, CONFIG)
    assert validation_success


@pytest.mark.usefixtures("create_generic_project")
def test_cardinality_correct(authentication, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/cardinality_correct.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    validation_success = _validate_data(graphs, used_iris, authentication, CONFIG)
    assert validation_success


@pytest.mark.usefixtures("create_generic_project")
def test_content_correct(authentication, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/content_correct.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    validation_success = _validate_data(graphs, used_iris, authentication, CONFIG)
    assert validation_success


@pytest.mark.usefixtures("create_generic_project")
def test_file_value_correct(authentication, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/file_value_correct.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    validation_success = _validate_data(graphs, used_iris, authentication, CONFIG)
    assert validation_success


@pytest.mark.usefixtures("create_generic_project")
def test_dsp_inbuilt_correct(authentication, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/dsp_inbuilt_correct.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    validation_success = _validate_data(graphs, used_iris, authentication, CONFIG)
    assert validation_success
