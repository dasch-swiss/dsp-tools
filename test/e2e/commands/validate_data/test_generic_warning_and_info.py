# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.input_problems import ValidateDataResult
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validate_data import _get_validation_status
from dsp_tools.commands.validate_data.validate_data import _validate_data
from test.e2e.commands.validate_data.util import prepare_data_for_validation_from_file

# ruff: noqa: ARG001 Unused function argument


CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=False,
    skip_ontology_validation=False,
)


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.fixture(scope="module")
def no_violations_with_warnings_do_not_ignore_duplicate_files(
    create_generic_project, authentication, shacl_validator: ShaclCliValidator
) -> ValidateDataResult:
    file = Path("testdata/validate-data/generic/no_violations_with_warnings.xml")
    graphs, used_iris, parsed_resources = prepare_data_for_validation_from_file(file, authentication)
    return _validate_data(graphs, used_iris, parsed_resources, CONFIG)


@pytest.fixture(scope="module")
def no_violations_with_info(
    create_generic_project, authentication, shacl_validator: ShaclCliValidator
) -> ValidateDataResult:
    file = Path("testdata/validate-data/generic/no_violations_with_info.xml")
    graphs, used_iris, parsed_resources = prepare_data_for_validation_from_file(file, authentication)
    return _validate_data(graphs, used_iris, parsed_resources, CONFIG)


class TestGetCorrectValidationResult:
    def test_no_violations_with_warnings_not_on_prod(self, no_violations_with_warnings_do_not_ignore_duplicate_files):
        # this boolean carries the information if there are problems of any severity level,
        # but not if the validation will pass
        assert not no_violations_with_warnings_do_not_ignore_duplicate_files.no_problems
        sorted_problems = no_violations_with_warnings_do_not_ignore_duplicate_files.problems
        assert isinstance(sorted_problems, SortedProblems)
        result = _get_validation_status(sorted_problems, is_on_prod=False)
        assert result is True

    def test_no_violations_with_warnings_on_prod(self, no_violations_with_warnings_do_not_ignore_duplicate_files):
        sorted_problems = no_violations_with_warnings_do_not_ignore_duplicate_files.problems
        assert isinstance(sorted_problems, SortedProblems)
        result = _get_validation_status(sorted_problems, is_on_prod=True)
        assert result is False

    def test_no_violations_with_info_not_on_prod(self, no_violations_with_info):
        # this boolean carries the information if there are problems of any severity level,
        # but not if the validation will pass
        assert not no_violations_with_info.no_problems
        sorted_problems = no_violations_with_info.problems
        assert isinstance(sorted_problems, SortedProblems)
        result = _get_validation_status(sorted_problems, is_on_prod=False)
        assert result is True

    def test_no_violations_with_info_on_prod(self, no_violations_with_info):
        sorted_problems = no_violations_with_info.problems
        assert isinstance(sorted_problems, SortedProblems)
        result = _get_validation_status(sorted_problems, is_on_prod=True)
        assert result is True


class TestSortedProblems:
    def test_no_violations_with_warnings_problems(self, no_violations_with_warnings_do_not_ignore_duplicate_files):
        expected_warnings = [
            (None, ProblemType.FILE_DUPLICATE),  # triplicate_archive
            (None, ProblemType.FILE_DUPLICATE),  # duplicate_iiif
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
        sorted_problems = no_violations_with_warnings_do_not_ignore_duplicate_files.problems
        assert isinstance(sorted_problems, SortedProblems)
        sorted_warnings = sorted(sorted_problems.user_warnings, key=lambda x: str(x.res_id))
        assert not sorted_problems.unique_violations
        assert len(sorted_problems.user_warnings) == len(expected_warnings)
        assert not sorted_problems.user_info
        assert not sorted_problems.unexpected_shacl_validation_components
        for one_result, expected_info in zip(sorted_warnings, expected_warnings):
            assert one_result.problem_type == expected_info[1]
            assert one_result.res_id == expected_info[0]

    def test_no_violations_with_warnings_problems_ignore_duplicates(self, authentication):
        # This only tests if the duplicates were ignored, the details of the result is tested separately
        file = Path("testdata/validate-data/generic/no_violations_with_warnings.xml")
        config = ValidateDataConfig(
            xml_file=Path(),
            save_graph_dir=None,
            severity=ValidationSeverity.INFO,
            ignore_duplicate_files_warning=True,
            is_on_prod_server=False,
            skip_ontology_validation=False,
        )
        graphs, used_iris, parsed_resources = prepare_data_for_validation_from_file(file, authentication)
        result = _validate_data(graphs, used_iris, parsed_resources, config)
        expected_res_ids = {"archive_no_legal_info", "iiif_no_legal_info", "image_no_legal_info"}
        sorted_problems = result.problems
        assert isinstance(sorted_problems, SortedProblems)
        warnings_ids = {x.res_id for x in sorted_problems.user_warnings}
        assert warnings_ids == expected_res_ids

    def test_no_violations_with_info(self, no_violations_with_info):
        all_expected_info = [
            ("link_to_resource_in_db", ProblemType.INEXISTENT_LINKED_RESOURCE),
            ("richtext_with_standoff_to_resource_in_db", ProblemType.INEXISTENT_LINKED_RESOURCE),
        ]
        sorted_problems = no_violations_with_info.problems
        assert isinstance(sorted_problems, SortedProblems)
        sorted_info = sorted(sorted_problems.user_info, key=lambda x: str(x.res_id))
        assert not sorted_problems.unique_violations
        assert not sorted_problems.user_warnings
        assert len(sorted_problems.user_info) == len(all_expected_info)
        assert not sorted_problems.unexpected_shacl_validation_components
        for one_result, expected_info in zip(sorted_info, all_expected_info):
            assert one_result.problem_type == expected_info[1]
            assert one_result.res_id == expected_info[0]


if __name__ == "__main__":
    pytest.main([__file__])
