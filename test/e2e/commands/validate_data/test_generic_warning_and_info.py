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
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
from dsp_tools.commands.validate_data.validate_data import _get_validation_status
from dsp_tools.commands.validate_data.validate_data import _prepare_data_for_validation_from_file

# ruff: noqa: ARG001 Unused function argument


CONFIG = ValidateDataConfig(Path(), None, ValidationSeverity.INFO, is_on_prod_server=False)


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.fixture(scope="module")
def no_violations_with_warnings(
    create_generic_project, authentication, shacl_validator: ShaclValidator
) -> SortedProblems:
    file = Path("testdata/validate-data/generic/no_violations_with_warnings.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    report = _get_validation_result(graphs, shacl_validator, CONFIG)
    reformatted = reformat_validation_graph(report)
    return sort_user_problems(reformatted)


@pytest.fixture(scope="module")
def no_violations_with_info(create_generic_project, authentication, shacl_validator: ShaclValidator) -> SortedProblems:
    file = Path("testdata/validate-data/generic/no_violations_with_info.xml")
    graphs, used_iris = _prepare_data_for_validation_from_file(file, authentication)
    report = _get_validation_result(graphs, shacl_validator, CONFIG)
    reformatted = reformat_validation_graph(report)
    return sort_user_problems(reformatted)


class TestGetCorrectValidationResult:
    def test_no_violations_with_warnings_not_on_prod(self, no_violations_with_warnings):
        result = _get_validation_status(no_violations_with_warnings, is_on_prod=False)
        assert result is True

    def test_no_violations_with_warnings_on_prod(self, no_violations_with_warnings):
        result = _get_validation_status(no_violations_with_warnings, is_on_prod=True)
        assert result is False

    def test_no_violations_with_info_not_on_prod(self, no_violations_with_info):
        result = _get_validation_status(no_violations_with_info, is_on_prod=False)
        assert result is True

    def test_no_violations_with_info_on_prod(self, no_violations_with_info):
        result = _get_validation_status(no_violations_with_info, is_on_prod=True)
        assert result is True


class TestSortedProblems:
    def test_no_violations_with_warnings_problems(self, no_violations_with_warnings):
        expected_warnings = [
            # each type of missing legal info (authorship, copyright, license) produces one violation
            ("archive_no_legal_info", ProblemType.GENERIC),
            ("archive_no_legal_info", ProblemType.GENERIC),
            ("archive_no_legal_info", ProblemType.GENERIC),
            ("iiif_no_legal_info", ProblemType.GENERIC),
            ("iiif_no_legal_info", ProblemType.GENERIC),
            ("iiif_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
        ]
        sorted_warnings = sorted(no_violations_with_warnings.user_warnings, key=lambda x: x.res_id)
        assert not no_violations_with_warnings.unique_violations
        assert len(no_violations_with_warnings.user_warnings) == len(expected_warnings)
        assert not no_violations_with_warnings.user_info
        assert not no_violations_with_warnings.unexpected_shacl_validation_components
        for one_result, expected_info in zip(sorted_warnings, expected_warnings):
            assert one_result.problem_type == expected_info[1]
            assert one_result.res_id == expected_info[0]

    def test_no_violations_with_info(self, no_violations_with_info):
        all_expected_info = [
            ("duplicate_iiif_1", ProblemType.FILE_DUPLICATE),
            ("duplicate_iiif_2", ProblemType.FILE_DUPLICATE),
            ("duplicate_still_image_1", ProblemType.FILE_DUPLICATE),
            ("duplicate_still_image_2", ProblemType.FILE_DUPLICATE),
            ("link_to_resource_in_db", ProblemType.INEXISTENT_LINKED_RESOURCE),
            ("triplicate_archive_1", ProblemType.FILE_DUPLICATE),
            ("triplicate_archive_2", ProblemType.FILE_DUPLICATE),
            ("triplicate_archive_3", ProblemType.FILE_DUPLICATE),
        ]
        sorted_info = sorted(no_violations_with_info.user_info, key=lambda x: x.res_id)
        assert not no_violations_with_info.unique_violations
        assert not no_violations_with_info.user_warnings
        assert len(no_violations_with_info.user_info) == len(all_expected_info)
        assert not no_violations_with_info.unexpected_shacl_validation_components
        for one_result, expected_info in zip(sorted_info, all_expected_info):
            assert one_result.problem_type == expected_info[1]
            assert one_result.res_id == expected_info[0]


if __name__ == "__main__":
    pytest.main([__file__])
