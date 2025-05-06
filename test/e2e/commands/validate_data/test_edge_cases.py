from collections.abc import Iterator
from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _get_parsed_graphs
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
from dsp_tools.commands.validate_data.validate_ontology import validate_ontology
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers


@pytest.fixture(scope="module")
def container_ports() -> Iterator[ExternalContainerPorts]:
    with get_containers() as metadata:
        yield metadata.ports


@pytest.fixture(scope="module")
def creds(container_ports: ExternalContainerPorts) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_ports.api}",
        f"http://0.0.0.0:{container_ports.ingest}",
    )


@pytest.fixture(scope="module")
def api_url(container_ports: ExternalContainerPorts) -> str:
    return f"http://0.0.0.0:{container_ports.api}"


@pytest.fixture(scope="module")
def shacl_validator(api_url: str) -> ShaclValidator:
    return ShaclValidator(api_url)


@pytest.fixture(scope="module")
def _create_projects(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/validate-data/special_characters/project_special_characters.json"), creds)
    assert create_project(Path("testdata/validate-data/inheritance/project_inheritance.json"), creds)
    assert create_project(Path("testdata/validate-data/erroneous_ontology/project_erroneous_ontology.json"), creds)


@pytest.fixture(scope="module")
def special_characters_violation(
    _create_projects: Iterator[None], api_url: str, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/special_characters/special_characters_violation.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def inheritance_violation(
    _create_projects: Iterator[None], api_url: str, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/inheritance/inheritance_violation.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def validate_ontology_violation(
    _create_projects: Iterator[None], api_url: str, shacl_validator: ShaclValidator
) -> OntologyValidationProblem | None:
    file = Path("testdata/validate-data/erroneous_ontology/erroneous_ontology.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    return validate_ontology(graphs.ontos, shacl_validator, None)


@pytest.mark.usefixtures("_create_projects")
def test_special_characters_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/special_characters/special_characters_correct.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    special_characters_correct = _get_validation_result(graphs, shacl_validator, None)
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


@pytest.mark.usefixtures("_create_projects")
def test_inheritance_correct(api_url: str, shacl_validator: ShaclValidator) -> None:
    file = Path("testdata/validate-data/inheritance/inheritance_correct.xml")
    graphs, _ = _get_parsed_graphs(api_url, file)
    inheritance_correct = _get_validation_result(graphs, shacl_validator, None)
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
        "isPartOf must either have cardinality 1 or 0-1.",
        "seqnum must either have cardinality 1 or 0-1.",
    }
    missing_is_part_of = {"A class with a cardinality for seqnum also requires a cardinality for isPartOf."}
    missing_seqnum = {"A class with a cardinality for isPartOf also requires a cardinality for seqnum."}
    mixed_cards = {"The cardinalities for seqnum and isPartOf must be identical within one resource class."}
    expected_results = [
        ("error:ImageWithKnoraProp_ErroneousCards", erroneous_cards_msg),
        ("error:ImageWithKnoraProp_ErroneousCards", erroneous_cards_msg),
        ("error:ImageWithKnoraProp_MissingIsPartOf", missing_is_part_of),
        ("error:ImageWithKnoraProp_MissingSeqnum", missing_seqnum),
        ("error:ImageWithKnoraProp_MixedValidCards", mixed_cards),
        ("error:ImageWithSubProp_ErroneousCards", erroneous_cards_msg),
        ("error:ImageWithSubProp_ErroneousCards", erroneous_cards_msg),
        ("error:ImageWithSubProp_MissingIsPartOf", missing_is_part_of),
        ("error:ImageWithSubProp_MissingSeqnum", missing_seqnum),
        ("error:ImageWithSubProp_MixedValidCards", mixed_cards),
    ]
    sorted_problems = sorted(validate_ontology_violation.problems, key=lambda x: x.res_iri)
    assert len(validate_ontology_violation.problems) == len(expected_results)
    for one_result, expected in zip(sorted_problems, expected_results):
        assert one_result.res_iri == expected[0]
        assert one_result.msg in expected[1]
