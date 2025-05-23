# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
from dsp_tools.commands.validate_data.validate_data import _prepare_data_for_validation_from_file

# ruff: noqa: ARG001 Unused function argument

CONFIG = ValidateDataConfig(Path(), None, ValidationSeverity.INFO)


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.fixture(scope="module")
def minimal_correct_graphs(create_generic_project, authentication: AuthenticationClient) -> tuple[RDFGraphs, set[str]]:
    file = Path("testdata/validate-data/generic/minimal_correct.xml")
    return _prepare_data_for_validation_from_file(file, authentication)


def test_minimal_correct(minimal_correct_graphs: tuple[RDFGraphs, set[str]], shacl_validator: ShaclValidator) -> None:
    graphs, _ = minimal_correct_graphs
    minimal_correct = _get_validation_result(graphs, shacl_validator, CONFIG)
    assert minimal_correct.conforms


def test_check_for_unknown_resource_classes(minimal_correct_graphs: tuple[RDFGraphs, set[str]]) -> None:
    graphs, used_iris = minimal_correct_graphs
    result = _check_for_unknown_resource_classes(graphs, used_iris)
    assert not result


@pytest.mark.usefixtures("create_generic_project")
def test_cardinality_correct(authentication, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/cardinality_correct.xml")
    graphs, _ = _prepare_data_for_validation_from_file(file, authentication)
    cardinality_correct = _get_validation_result(graphs, shacl_validator, CONFIG)
    assert cardinality_correct.conforms


@pytest.mark.usefixtures("create_generic_project")
def test_content_correct(authentication, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/content_correct.xml")
    graphs, _ = _prepare_data_for_validation_from_file(file, authentication)
    content_correct = _get_validation_result(graphs, shacl_validator, CONFIG)
    # The referenced absolute IRIs are perceived as a violation in SHACL
    # because the resource does not exist in the graph
    assert not content_correct.conforms
    reformatted = reformat_validation_graph(content_correct)
    sorted_messages = sort_user_problems(reformatted)
    assert not sorted_messages.unique_violations
    assert len(sorted_messages.user_info) == 1
    assert not sorted_messages.unexpected_shacl_validation_components


@pytest.mark.usefixtures("create_generic_project")
def test_file_value_correct(authentication, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/file_value_correct.xml")
    graphs, _ = _prepare_data_for_validation_from_file(file, authentication)
    file_value_correct = _get_validation_result(graphs, shacl_validator, CONFIG)
    assert file_value_correct.conforms


@pytest.mark.usefixtures("create_generic_project")
def test_dsp_inbuilt_correct(authentication, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/generic/dsp_inbuilt_correct.xml")
    graphs, _ = _prepare_data_for_validation_from_file(file, authentication)
    dsp_inbuilt_correct = _get_validation_result(graphs, shacl_validator, CONFIG)
    assert dsp_inbuilt_correct.conforms
