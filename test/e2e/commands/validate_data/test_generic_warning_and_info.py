# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.validate_data import _prepare_data_for_validation_from_file
from dsp_tools.commands.validate_data.validate_data import _validate_data

# ruff: noqa: ARG001 Unused function argument


CONFIG = ValidateDataConfig(Path(), None, ValidationSeverity.INFO, False)


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.fixture(scope="module")
def no_violations_with_warnings_graphs(
    create_generic_project, authentication, shacl_validator: ShaclValidator
) -> tuple[RDFGraphs, set[str]]:
    file = Path("testdata/validate-data/generic/no_violations_with_warnings.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    return graphs, used_iris


@pytest.fixture(scope="module")
def no_violations_with_info_graphs(
    create_generic_project, authentication, shacl_validator: ShaclValidator
) -> tuple[RDFGraphs, set[str]]:
    file = Path("testdata/validate-data/generic/no_violations_with_info.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    return graphs, used_iris


def test_no_violations_with_warnings_not_on_prod(no_violations_with_warnings_graphs, authentication):
    config = ValidateDataConfig(Path(), None, ValidationSeverity.INFO, is_on_prod_server=False)
    graphs, used_iris = no_violations_with_warnings_graphs
    result = _validate_data(graphs=graphs, used_iris=used_iris, auth=authentication, config=config)
    assert result is True


def test_no_violations_with_warnings_on_prod(no_violations_with_warnings_graphs, authentication):
    config = ValidateDataConfig(Path(), None, ValidationSeverity.INFO, is_on_prod_server=True)
    graphs, used_iris = no_violations_with_warnings_graphs
    result = _validate_data(graphs=graphs, used_iris=used_iris, auth=authentication, config=config)
    assert result is False


def test_no_violations_with_info_not_on_prod(no_violations_with_info_graphs, authentication):
    config = ValidateDataConfig(Path(), None, ValidationSeverity.INFO, is_on_prod_server=False)
    graphs, used_iris = no_violations_with_info_graphs
    result = _validate_data(graphs=graphs, used_iris=used_iris, auth=authentication, config=config)
    assert result is True


def test_no_violations_with_info_on_prod(no_violations_with_info_graphs, authentication):
    config = ValidateDataConfig(Path(), None, ValidationSeverity.INFO, is_on_prod_server=True)
    graphs, used_iris = no_violations_with_info_graphs
    result = _validate_data(graphs=graphs, used_iris=used_iris, auth=authentication, config=config)
    assert result is True


if __name__ == "__main__":
    pytest.main([__file__])
