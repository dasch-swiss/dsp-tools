# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest
from exception import TestDependencyNotSuccessfulError

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.metadata_client import ExistingResourcesRetrieved
from dsp_tools.clients.metadata_client_live import MetadataClientLive
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.input_problems import ValidateDataResult
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validate_data import _get_validation_status
from dsp_tools.commands.validate_data.validate_data import _validate_data
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from test.e2e.commands.validate_data.util import prepare_data_for_validation_from_file

# ruff: noqa: ARG001 Unused function argument


CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=False,
    skip_ontology_validation=False,
    do_not_request_resource_metadata_from_db=False,
)

SHORTCODE = "9999"
METADATA_RETRIEVAL_SUCCESS = ExistingResourcesRetrieved.TRUE


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.fixture(scope="module")
def no_violations_with_warnings_do_not_ignore_duplicate_files(
    create_generic_project, authentication, shacl_validator: ShaclCliValidator
) -> ValidateDataResult:
    file = Path("testdata/validate-data/core_validation/no_violations_with_warnings.xml")
    graphs, triple_stores, used_iris, parsed_resources = prepare_data_for_validation_from_file(file, authentication)
    return _validate_data(
        graphs, triple_stores, used_iris, parsed_resources, CONFIG, SHORTCODE, METADATA_RETRIEVAL_SUCCESS
    )


@pytest.fixture(scope="module")
def iri_reference_upload(
    create_generic_project, authentication
) -> tuple[ExistingResourcesRetrieved, list[dict[str, str]]]:
    success = xmlupload(
        Path("testdata/validate-data/core_validation/references_to_iri_in_db_referenced_resources.xml"),
        ServerCredentials(authentication.email, authentication.password, authentication.server),
        ".",
    )
    if not success:
        raise TestDependencyNotSuccessfulError("xmlupload")
    meta_client = MetadataClientLive(authentication.server, authentication)
    return meta_client.get_resource_metadata("9999")


@pytest.fixture(scope="module")
def with_iri_references(
    create_generic_project, iri_reference_upload, authentication, shacl_validator: ShaclCliValidator
) -> ValidateDataResult:
    xml_file = Path("testdata/validate-data/core_validation/references_to_iri_in_db.xml")
    id2iri_file = "testdata/validate-data/core_validation/references_to_iri_in_db_id2iri.json"
    graphs, triple_stores, used_iris, parsed_resources = prepare_data_for_validation_from_file(
        xml_file, authentication, id2iri_file
    )
    return _validate_data(
        graphs, triple_stores, used_iris, parsed_resources, CONFIG, SHORTCODE, METADATA_RETRIEVAL_SUCCESS
    )


def test_metadata_retrival(create_generic_project, iri_reference_upload, authentication):
    success, metadata = iri_reference_upload
    assert success == ExistingResourcesRetrieved.TRUE
    assert len(metadata) == 2
    res_1 = next(x for x in metadata if x["resourceIri"] == "http://rdfh.ch/9999/iri-from-resource-in-db")
    res_1_type = f"{authentication.server}/ontology/9999/onto/v2#ClassInheritedCardinalityOverwriting"
    assert res_1["resourceClassIri"] == res_1_type
    res_2 = next(x for x in metadata if x["resourceIri"] == "http://rdfh.ch/9999/resource-in-id2iri-mapping")
    res_2_type = f"{authentication.server}/ontology/9999/onto/v2#ClassWithEverything"
    assert res_2["resourceClassIri"] == res_2_type


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


class TestSortedProblems:
    def test_no_violations_with_warnings_problems(self, no_violations_with_warnings_do_not_ignore_duplicate_files):
        expected_warnings = [
            (None, ProblemType.FILE_DUPLICATE),  # triplicate_archive
            (None, ProblemType.FILE_DUPLICATE),  # duplicate_iiif
            # each type of missing legal info (authorship, copyright, license) produces one violation
            ("no_legal_info_archive", ProblemType.GENERIC),
            ("no_legal_info_archive", ProblemType.GENERIC),
            ("no_legal_info_archive", ProblemType.GENERIC),
            ("no_legal_info_iiif", ProblemType.GENERIC),
            ("no_legal_info_iiif", ProblemType.GENERIC),
            ("no_legal_info_iiif", ProblemType.GENERIC),
            ("no_legal_info_image_file", ProblemType.GENERIC),
            ("no_legal_info_image_file", ProblemType.GENERIC),
            ("no_legal_info_image_file", ProblemType.GENERIC),
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
        file = Path("testdata/validate-data/core_validation/no_violations_with_warnings.xml")
        config = ValidateDataConfig(
            xml_file=Path(),
            save_graph_dir=None,
            severity=ValidationSeverity.INFO,
            ignore_duplicate_files_warning=True,
            is_on_prod_server=False,
            skip_ontology_validation=False,
            do_not_request_resource_metadata_from_db=False,
        )
        graphs, triple_stores, used_iris, parsed_resources = prepare_data_for_validation_from_file(file, authentication)
        result = _validate_data(
            graphs, triple_stores, used_iris, parsed_resources, config, SHORTCODE, METADATA_RETRIEVAL_SUCCESS
        )
        expected_res_ids = {"no_legal_info_archive", "no_legal_info_iiif", "no_legal_info_image_file"}
        sorted_problems = result.problems
        assert isinstance(sorted_problems, SortedProblems)
        warnings_ids = {x.res_id for x in sorted_problems.user_warnings}
        assert warnings_ids == expected_res_ids

    def test_with_iri_references(self, with_iri_references):
        all_expected_violations = [
            ("link_to_resource_in_db_which_does_not_exist", ProblemType.LINK_TARGET_NOT_FOUND_IN_DB),
            (
                "richtext_with_standoff_to_resource_in_db_which_does_not_exist",
                ProblemType.LINK_TARGET_NOT_FOUND_IN_DB,
            ),
        ]
        sorted_problems = with_iri_references.problems
        assert isinstance(sorted_problems, SortedProblems)
        sorted_violations = sorted(sorted_problems.unique_violations, key=lambda x: str(x.res_id))
        assert len(sorted_problems.unique_violations) == len(all_expected_violations)
        assert not sorted_problems.user_warnings
        assert not sorted_problems.user_info
        assert not sorted_problems.unexpected_shacl_validation_components
        for one_result, expected_violation in zip(sorted_violations, all_expected_violations):
            assert one_result.problem_type == expected_violation[1]
            assert one_result.res_id == expected_violation[0]


if __name__ == "__main__":
    pytest.main([__file__])
