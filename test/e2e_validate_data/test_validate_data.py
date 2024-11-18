from functools import lru_cache
from pathlib import Path
from typing import Iterator

import pytest
from rdflib import BNode
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.models.input_problems import ContentRegexProblem
from dsp_tools.commands.validate_data.models.input_problems import DuplicateValueProblem
from dsp_tools.commands.validate_data.models.input_problems import FileValueProblem
from dsp_tools.commands.validate_data.models.input_problems import GenericProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkedResourceDoesNotExistProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkTargetTypeMismatchProblem
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeProblem
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.reformat_validaton_result import _extract_base_info_of_resource_results
from dsp_tools.commands.validate_data.reformat_validaton_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validate_data import _get_parsed_graphs
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
from test.e2e_validate_data.setup_testcontainers import get_containers

CREDS = ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")
LOCAL_API = "http://0.0.0.0:3333"
DONT_SAVE_GRAPHS = False


@lru_cache(maxsize=None)
@pytest.fixture
def _create_project_generic() -> Iterator[None]:
    with get_containers():
        success = create_project(Path("testdata/validate-data/generic/project.json"), CREDS)
        assert success
        yield


@lru_cache(maxsize=None)
@pytest.fixture
def api_con() -> ApiConnection:
    return ApiConnection(LOCAL_API)


@lru_cache(maxsize=None)
@pytest.fixture
def cardinality_correct(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/cardinality_correct.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def unknown_classes_graphs(_create_project_generic: Iterator[None], api_con: ApiConnection) -> RDFGraphs:
    file = Path("testdata/validate-data/generic/unknown_classes.xml")
    return _get_parsed_graphs(api_con, file)


@lru_cache(maxsize=None)
@pytest.fixture
def cardinality_violation(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/cardinality_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def content_correct(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/content_correct.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def content_violation(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/content_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def every_combination_once(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/every_combination_once.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def minimal_correct(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/minimal_correct.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def value_type_violation(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/value_type_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def unique_value_violation(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/unique_value_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def file_value_correct(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/file_value_correct.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def file_value_violation(_create_project_generic: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/file_value_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def _create_project_special() -> Iterator[None]:
    with get_containers():
        success = create_project(
            Path("testdata/validate-data/special_characters/project_special_characters.json"), CREDS
        )
        assert success
        yield


@lru_cache(maxsize=None)
@pytest.fixture
def special_characters_correct(
    _create_project_special: Iterator[None], api_con: ApiConnection
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/special_characters/special_characters_correct.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def special_characters_violation(
    _create_project_special: Iterator[None], api_con: ApiConnection
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/special_characters/special_characters_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def _create_project_inheritance() -> Iterator[None]:
    with get_containers():
        success = create_project(Path("testdata/validate-data/inheritance/project_inheritance.json"), CREDS)
        assert success
        yield


@lru_cache(maxsize=None)
@pytest.fixture
def inheritance_correct(_create_project_inheritance: Iterator[None], api_con: ApiConnection) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/inheritance/inheritance_correct.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


@lru_cache(maxsize=None)
@pytest.fixture
def inheritance_violation(
    _create_project_inheritance: Iterator[None], api_con: ApiConnection
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/inheritance/inheritance_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, api_con, file, DONT_SAVE_GRAPHS)


def test_extract_identifiers_of_resource_results(every_combination_once: ValidationReportGraphs) -> None:
    report_and_onto = every_combination_once.validation_graph + every_combination_once.onto_graph
    data_and_onto = every_combination_once.data_graph + every_combination_once.onto_graph
    result = _extract_base_info_of_resource_results(report_and_onto, data_and_onto)
    result_sorted = sorted(result, key=lambda x: str(x.resource_iri))
    expected_iris = [
        (URIRef("http://data/empty_label"), None),
        (URIRef("http://data/geoname_not_number"), BNode),
        (URIRef("http://data/id_card_one"), None),
        (URIRef("http://data/id_closed_constraint"), None),
        (URIRef("http://data/id_max_card"), None),
        (URIRef("http://data/id_missing_file_value"), None),
        (URIRef("http://data/id_simpletext"), BNode),
        (URIRef("http://data/id_uri"), BNode),
        (URIRef("http://data/identical_values"), None),
        (URIRef("http://data/link_target_non_existent"), BNode),
        (URIRef("http://data/link_target_wrong_class"), BNode),
        (URIRef("http://data/list_node_non_existent"), BNode),
    ]
    assert len(result) == len(expected_iris)
    for result_info, expected_iri in zip(result_sorted, expected_iris):
        assert result_info.resource_iri == expected_iri[0]
        if expected_iri[1] is None:
            assert not result_info.detail
        else:
            detail_base_info = result_info.detail
            assert isinstance(detail_base_info, DetailBaseInfo)
            assert isinstance(detail_base_info.detail_bn, expected_iri[1])


class TestCheckConforms:
    def test_cardinality_correct(self, cardinality_correct: ValidationReportGraphs) -> None:
        assert cardinality_correct.conforms

    def test_cardinality_violation(self, cardinality_violation: ValidationReportGraphs) -> None:
        assert not cardinality_violation.conforms

    def test_content_correct(self, content_correct: ValidationReportGraphs) -> None:
        assert content_correct.conforms

    def test_content_violation(self, content_violation: ValidationReportGraphs) -> None:
        assert not content_violation.conforms

    def test_every_combination_once(self, every_combination_once: ValidationReportGraphs) -> None:
        assert not every_combination_once.conforms

    def test_minimal_correct(self, minimal_correct: ValidationReportGraphs) -> None:
        assert minimal_correct.conforms

    def test_value_type_violation(self, value_type_violation: ValidationReportGraphs) -> None:
        assert not value_type_violation.conforms

    def test_unique_value_violation(self, unique_value_violation: ValidationReportGraphs) -> None:
        assert not unique_value_violation.conforms

    def test_file_value_correct(self, file_value_correct: ValidationReportGraphs) -> None:
        assert file_value_correct.conforms

    def test_file_value_cardinality_violation(self, file_value_violation: ValidationReportGraphs) -> None:
        assert not file_value_violation.conforms

    def test_special_characters_correct(self, special_characters_correct: ValidationReportGraphs) -> None:
        assert special_characters_correct.conforms

    def test_special_characters_violation(self, special_characters_violation: ValidationReportGraphs) -> None:
        assert not special_characters_violation.conforms

    def test_inheritance_correct(self, inheritance_correct: ValidationReportGraphs) -> None:
        assert inheritance_correct.conforms

    def test_inheritance_violation(self, inheritance_violation: ValidationReportGraphs) -> None:
        assert not inheritance_violation.conforms


class TestReformatValidationGraph:
    def test_reformat_cardinality_violation(self, cardinality_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(cardinality_violation)
        expected_info_tuples = [
            (MinCardinalityProblem, "id_card_one"),
            (NonExistentCardinalityProblem, "id_closed_constraint"),
            (MaxCardinalityProblem, "id_max_card"),
            (MinCardinalityProblem, "id_min_card"),
            (NonExistentCardinalityProblem, "super_prop_no_card"),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert isinstance(one_result, expected_info[0])
            assert one_result.res_id == expected_info[1]

    def test_reformat_value_type_violation(self, value_type_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(value_type_violation)
        assert not result.unexpected_results
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        expected_info_tuples = [
            ("id_bool", "BooleanValue", "onto:testBoolean"),
            ("id_color", "ColorValue", "onto:testColor"),
            ("id_date", "DateValue", "onto:testSubDate1"),
            ("id_decimal", "DecimalValue", "onto:testDecimalSimpleText"),
            ("id_geoname", "GeonameValue", "onto:testGeoname"),
            ("id_integer", "IntValue", "onto:testIntegerSimpleText"),
            ("id_link", "LinkValue", "onto:testHasLinkTo"),
            ("id_list", "ListValue", "onto:testListProp"),
            ("id_richtext", "TextValue with formatting", "onto:testRichtext"),
            ("id_simpletext", "TextValue without formatting", "onto:testTextarea"),
            ("id_time", "TimeValue", "onto:testTimeValue"),
            ("id_uri", "UriValue", "onto:testUriValue"),
            ("is_link_should_be_integer", "IntValue", "onto:testIntegerSpinbox"),
            ("is_link_should_be_text", "TextValue without formatting", "onto:testTextarea"),
        ]
        assert len(result.problems) == len(expected_info_tuples)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert isinstance(one_result, ValueTypeProblem)
            assert one_result.res_id == expected_info[0]
            assert one_result.expected_type == expected_info[1]
            assert one_result.prop_name == expected_info[2]

    def test_reformat_content_violation(self, content_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(content_violation)
        assert not result.unexpected_results
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        expected_info_tuples = [
            ("empty_label", "rdfs:label", "The label must be a non-empty string"),
            ("empty_text_rich", "onto:testRichtext", "The value must be a non-empty string"),
            ("empty_text_simple", "onto:testTextarea", "The value must be a non-empty string"),
            ("geoname_not_number", "onto:testGeoname", "The value must be a valid geoname code"),
            ("link_target_non_existent", "onto:testHasLinkTo", "other"),
            ("link_target_wrong_class", "onto:testHasLinkToCardOneResource", "id_9_target"),
            (
                "list_name_attrib_empty",
                "onto:testListProp",
                "The list that should be used with this property is: firstList.",
            ),
            (
                "list_name_non_existent",
                "onto:testListProp",
                "The list that should be used with this property is: firstList.",
            ),
            ("list_node_non_existent", "onto:testListProp", "Unknown list node for list: firstList."),
            ("text_only_whitespace_simple", "onto:testTextarea", "The value must be a non-empty string"),
        ]
        assert len(result.problems) == len(expected_info_tuples)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert one_result.res_id == expected_info[0]
            assert one_result.prop_name == expected_info[1]
            if isinstance(one_result, ContentRegexProblem):
                assert one_result.expected_format == expected_info[2]
            elif isinstance(one_result, GenericProblem):
                assert one_result.results_message == expected_info[2]
            elif isinstance(one_result, LinkTargetTypeMismatchProblem):
                assert one_result.link_target_id == expected_info[2]
            elif isinstance(one_result, LinkedResourceDoesNotExistProblem):
                assert one_result.link_target_id == expected_info[2]
            else:
                assert isinstance(one_result, LinkedResourceDoesNotExistProblem)

    def test_reformat_every_constraint_once(self, every_combination_once: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(every_combination_once)
        expected_info_tuples = [
            ("empty_label", ContentRegexProblem),
            ("geoname_not_number", ContentRegexProblem),
            ("id_card_one", MinCardinalityProblem),
            ("id_closed_constraint", NonExistentCardinalityProblem),
            ("id_max_card", MaxCardinalityProblem),
            ("id_missing_file_value", FileValueProblem),
            ("id_simpletext", ValueTypeProblem),
            ("id_uri", ValueTypeProblem),
            ("identical_values", DuplicateValueProblem),
            ("link_target_non_existent", LinkedResourceDoesNotExistProblem),
            ("link_target_wrong_class", LinkTargetTypeMismatchProblem),
            ("list_node_non_existent", GenericProblem),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert one_result.res_id == expected_info[0]
            assert isinstance(one_result, expected_info[1])

    def test_reformat_unique_value_violation(self, unique_value_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(unique_value_violation)
        expected_ids = [
            "identical_values_LinkValue",
            "identical_values_listNode",
            "identical_values_valueAsString",
            "identical_values_valueHas",
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_ids)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_id in zip(sorted_problems, expected_ids):
            assert isinstance(one_result, DuplicateValueProblem)
            assert one_result.res_id == expected_id

    def test_reformat_file_value_violation(self, file_value_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(file_value_violation)
        expected_info_tuples = ["id_video_missing", "id_video_wrong_extension"]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert isinstance(one_result, FileValueProblem)
            assert one_result.res_id == expected_info

    def test_reformat_special_characters_violation(self, special_characters_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(special_characters_violation)
        expected_tuples = [
            ("node_backslash", "Unknown list node for list: list \\ ' space.", "other \\ backslash"),
            ("node_double_quote", "Unknown list node for list: list \\ ' space.", 'other double quote "'),
            ("node_single_quote", "Unknown list node for list: list \\ ' space.", "other single quote '"),
            ("non_ascii_latin_alphabet", "", ""),
            ("non_ascii_other_alphabet", "", ""),
            ("special_char", "", ""),
            ("wrong_list_name", "The list that should be used with this property is: list \\ ' space.", "other"),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for prblm, expected in zip(sorted_problems, expected_tuples):
            if isinstance(prblm, GenericProblem):
                assert prblm.res_id == expected[0]
                assert prblm.problem == expected[1]
                assert prblm.actual_content == expected[2]
            elif isinstance(prblm, ContentRegexProblem):
                assert prblm.res_id == expected[0]

    def test_reformat_inheritance_violation(self, inheritance_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(inheritance_violation)
        expected_results = [
            ("ResourceSubCls1", {"onto:hasText0"}),
            ("ResourceSubCls2", {"onto:hasTextSubProp1", "onto:hasText0"}),
            ("ResourceSubCls2", {"onto:hasTextSubProp1", "onto:hasText0"}),
            ("ResourceUnrelated", {"onto:hasText0"}),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_results)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected in zip(sorted_problems, expected_results):
            assert isinstance(one_result, NonExistentCardinalityProblem)
            assert one_result.res_id == expected[0]
            assert one_result.prop_name in expected[1]


def test_check_for_unknown_resource_classes(unknown_classes_graphs: RDFGraphs) -> None:
    result = _check_for_unknown_resource_classes(unknown_classes_graphs)
    assert isinstance(result, UnknownClassesInData)
    expected = {"onto:NonExisting", "unknown:ClassWithEverything", "unknownClass"}
    assert result.unknown_classes == expected


if __name__ == "__main__":
    pytest.main([__file__])
