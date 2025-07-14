# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validation.get_validation_report import get_validation_report
from dsp_tools.commands.validate_data.validation.validate_ontology import validate_ontology
from test.e2e_validate_data.util import prepare_data_for_validation_from_file

CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=False,
)


@pytest.fixture(scope="module")
def _create_projects_edge_cases(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/validate-data/special_characters/project_special_characters.json"), creds)
    assert create_project(Path("testdata/validate-data/inheritance/project_inheritance.json"), creds)
    assert create_project(Path("testdata/validate-data/erroneous_ontology/project_erroneous_ontology.json"), creds)


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.fixture(scope="module")
def special_characters_violation(
    _create_projects_edge_cases, authentication: AuthenticationClient, shacl_validator: ShaclCliValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/special_characters/special_characters_violation.xml")
    graphs, _ = prepare_data_for_validation_from_file(file, authentication, CONFIG.ignore_duplicate_files_warning)
    return get_validation_report(graphs, shacl_validator)


@pytest.fixture(scope="module")
def inheritance_violation(
    _create_projects_edge_cases, authentication: AuthenticationClient, shacl_validator: ShaclCliValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/inheritance/inheritance_violation.xml")
    graphs, _ = prepare_data_for_validation_from_file(file, authentication, CONFIG.ignore_duplicate_files_warning)
    return get_validation_report(graphs, shacl_validator)


@pytest.fixture(scope="module")
def validate_ontology_violation(
    _create_projects_edge_cases, authentication: AuthenticationClient
) -> OntologyValidationProblem | None:
    file = Path("testdata/validate-data/erroneous_ontology/erroneous_ontology.xml")
    graphs, _ = prepare_data_for_validation_from_file(file, authentication, CONFIG.ignore_duplicate_files_warning)
    shacl_validator = ShaclCliValidator()
    return validate_ontology(graphs.ontos, shacl_validator, CONFIG)


@pytest.mark.usefixtures("_create_projects_edge_cases")
def test_special_characters_correct(authentication: AuthenticationClient, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/special_characters/special_characters_correct.xml")
    graphs, _ = prepare_data_for_validation_from_file(file, authentication, CONFIG.ignore_duplicate_files_warning)
    special_characters_correct = get_validation_report(graphs, shacl_validator)
    assert special_characters_correct.conforms


def test_special_characters_violation(special_characters_violation: ValidationReportGraphs) -> None:
    assert not special_characters_violation.conforms


def test_reformat_special_characters_violation(special_characters_violation: ValidationReportGraphs) -> None:
    expected_tuples = [
        (
            "node_backslash",
            (
                "A valid node from the list 'list \\ ' space' must be used with this property "
                "(input displayed in format 'listName / NodeName')."
            ),
            "list \\ ' space / other \\ backslash",
        ),
        (
            "node_double_quote",
            (
                "A valid node from the list 'list \\ ' space' must be used with this property "
                "(input displayed in format 'listName / NodeName')."
            ),
            '''list \\ ' space / other double quote "''',
        ),
        (
            "node_single_quote",
            (
                "A valid node from the list 'list \\ ' space' must be used with this property "
                "(input displayed in format 'listName / NodeName')."
            ),
            "list \\ ' space / other single quote '",
        ),
        ("non_ascii_latin_alphabet", "", ""),
        ("non_ascii_other_alphabet", "", ""),
        ("special_char", "", ""),
        (
            "wrong_list_name",
            (
                "A valid node from the list 'list \\ ' space' must be used with this property "
                "(input displayed in format 'listName / NodeName')."
            ),
            "other / \\ backslash",
        ),
    ]
    result = reformat_validation_graph(special_characters_violation)
    sorted_problems = sort_user_problems(result)
    assert len(sorted_problems.unique_violations) == len(expected_tuples)
    assert not sorted_problems.user_warnings
    assert not sorted_problems.user_info
    assert not sorted_problems.unexpected_shacl_validation_components
    alphabetically_sorted = sorted(result.problems, key=lambda x: x.res_id)
    for prblm, expected in zip(alphabetically_sorted, expected_tuples):
        if prblm.problem_type == ProblemType.GENERIC:
            assert prblm.res_id == expected[0]
            assert prblm.message == expected[1]
            assert prblm.input_value == expected[2]
        elif prblm.problem_type == ProblemType.INPUT_REGEX:
            assert prblm.res_id == expected[0]


@pytest.mark.usefixtures("_create_projects_edge_cases")
def test_inheritance_correct(authentication: AuthenticationClient, shacl_validator: ShaclCliValidator) -> None:
    file = Path("testdata/validate-data/inheritance/inheritance_correct.xml")
    graphs, _ = prepare_data_for_validation_from_file(file, authentication, CONFIG.ignore_duplicate_files_warning)
    inheritance_correct = get_validation_report(graphs, shacl_validator)
    assert inheritance_correct.conforms


def test_inheritance_violation(inheritance_violation: ValidationReportGraphs) -> None:
    assert not inheritance_violation.conforms


def test_reformat_inheritance_violation(inheritance_violation: ValidationReportGraphs) -> None:
    expected_results = [
        ("ResourceSubCls1", {"onto:hasText0"}),
        ("ResourceSubCls2", {"onto:hasTextSubProp1", "onto:hasText0"}),
        ("ResourceSubCls2", {"onto:hasTextSubProp1", "onto:hasText0"}),
        ("ResourceUnrelated", {"onto:hasText0"}),
    ]
    result = reformat_validation_graph(inheritance_violation)
    sorted_problems = sort_user_problems(result)
    assert len(sorted_problems.unique_violations) == len(expected_results)
    assert not sorted_problems.user_warnings
    assert not sorted_problems.user_info
    assert not sorted_problems.unexpected_shacl_validation_components
    alphabetically_sorted = sorted(result.problems, key=lambda x: x.res_id)
    for one_result, expected in zip(alphabetically_sorted, expected_results):
        assert one_result.problem_type == ProblemType.NON_EXISTING_CARD
        assert one_result.res_id == expected[0]
        assert one_result.prop_name in expected[1]


def test_validate_ontology_violation(validate_ontology_violation: ValidationReportGraphs | None) -> None:
    assert isinstance(validate_ontology_violation, OntologyValidationProblem)
    erroneous_cards_msg = {
        "seqnum must either have cardinality 1 or 0-1.",
    }
    missing_is_part_of = {"A class with a cardinality for seqnum also requires a cardinality for isPartOf."}
    missing_seqnum = {"A class with a cardinality for isPartOf also requires a cardinality for seqnum."}
    expected_results = [
        ("error:ImageWithKnoraProp_ErroneousCards", erroneous_cards_msg),
        ("error:ImageWithKnoraProp_MissingIsPartOf", missing_is_part_of),
        ("error:ImageWithKnoraProp_MissingSeqnum", missing_seqnum),
        ("error:ImageWithSubProp_ErroneousCards", erroneous_cards_msg),
        ("error:ImageWithSubProp_MissingIsPartOf", missing_is_part_of),
        ("error:ImageWithSubProp_MissingSeqnum", missing_seqnum),
    ]
    sorted_problems = sorted(validate_ontology_violation.problems, key=lambda x: x.res_iri)
    assert len(validate_ontology_violation.problems) == len(expected_results)
    for one_result, expected in zip(sorted_problems, expected_results):
        assert one_result.res_iri == expected[0]
        assert one_result.msg in expected[1]
