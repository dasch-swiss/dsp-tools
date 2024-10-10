from pathlib import Path

import pytest
from rdflib import Graph

from dsp_tools.commands.validate_data.models.input_problems import ContentRegexViolation
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import ValidationReports
from dsp_tools.commands.validate_data.reformat_validaton_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _get_data_info_from_file

LOCAL_API = "http://0.0.0.0:3333"


@pytest.fixture
def cardinality_violation_data() -> Graph:
    data, _ = _get_data_info_from_file(Path("testdata/validate-data/data/cardinality_violation.xml"), LOCAL_API)
    return data.make_graph()


@pytest.fixture
def cardinality_violation_result() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_results/cardinality_violation_result.ttl")
    return g


@pytest.fixture
def value_type_violation_data() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_results/value_type_violation_data.ttl")
    return g


@pytest.fixture
def value_type_violation_result() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_results/value_type_violation_result.ttl")
    return g


@pytest.fixture
def content_violation_data() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_results/content_violation_data.ttl")
    return g


@pytest.fixture
def content_violation_result() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_results/content_violation_result.ttl")
    return g


@pytest.fixture
def every_combination_once_data() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_results/every_combination_once_data.ttl")
    return g


@pytest.fixture
def every_combination_once_result_cardinality() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_results/every_combination_once_result_cardinality.ttl")
    return g


@pytest.fixture
def every_constraint_once_result_content() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_results/every_constraint_once_result_content.ttl")
    return g


def test_reformat_cardinality_violation(cardinality_violation_result: Graph, cardinality_violation_data: Graph) -> None:
    val_rep = ValidationReports(
        conforms=False,
        content_validation=None,
        cardinality_validation=cardinality_violation_result,
        shacl_graphs=Graph(),
        data_graph=cardinality_violation_data,
    )
    result = reformat_validation_graph(val_rep)
    expected_info_tuples = [
        (MinCardinalityViolation, "id_card_one"),
        (NonExistentCardinalityViolation, "id_closed_constraint"),
        (MaxCardinalityViolation, "id_max_card"),
        (MinCardinalityViolation, "id_min_card"),
    ]
    assert not result.unexpected_results
    assert len(result.problems) == 4
    sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
    for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
        assert isinstance(one_result, expected_info[0])
        assert one_result.res_id == expected_info[1]


def test_reformat_value_type_violation(value_type_violation_result: Graph, value_type_violation_data: Graph) -> None:
    val_rep = ValidationReports(
        conforms=False,
        content_validation=value_type_violation_result,
        cardinality_validation=None,
        shacl_graphs=Graph(),
        data_graph=value_type_violation_data,
    )
    result = reformat_validation_graph(val_rep)
    assert not result.unexpected_results
    assert len(result.problems) == 12
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
    ]
    for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
        assert isinstance(one_result, ValueTypeViolation)
        assert one_result.res_id == expected_info[0]
        assert one_result.expected_type == expected_info[1]
        assert one_result.prop_name == expected_info[2]


def test_reformat_content_violation(content_violation_result: Graph, content_violation_data: Graph) -> None:
    val_rep = ValidationReports(
        conforms=False,
        content_validation=content_violation_result,
        cardinality_validation=None,
        shacl_graphs=Graph(),
        data_graph=content_violation_data,
    )
    result = reformat_validation_graph(val_rep)
    assert not result.unexpected_results
    assert len(result.problems) == 4
    sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
    expected_info_tuples = [
        ("empty_text_rich", "onto:testRichtext", "The value must be a non-empty string"),
        ("empty_text_simple", "onto:testTextarea", "The value must be a non-empty string"),
        ("geoname_not_number", "onto:testGeoname", "The value must be a valid geoname code"),
        ("text_only_whitespace_simple", "onto:testTextarea", "The value must be a non-empty string"),
    ]
    for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
        assert isinstance(one_result, ContentRegexViolation)
        assert one_result.res_id == expected_info[0]
        assert one_result.prop_name == expected_info[1]
        assert one_result.expected_format == expected_info[2]


def test_reformat_every_constraint_once(
    every_combination_once_result_cardinality: Graph,
    every_constraint_once_result_content: Graph,
    every_combination_once_data: Graph,
) -> None:
    val_rep = ValidationReports(
        conforms=False,
        content_validation=every_constraint_once_result_content,
        cardinality_validation=every_combination_once_result_cardinality,
        shacl_graphs=Graph(),
        data_graph=every_combination_once_data,
    )
    result = reformat_validation_graph(val_rep)
    expected_info_tuples = [
        ("geoname_not_number", ContentRegexViolation),
        ("id_card_one", MinCardinalityViolation),
        ("id_closed_constraint", NonExistentCardinalityViolation),
        ("id_max_card", MaxCardinalityViolation),
        ("id_simpletext", ValueTypeViolation),
        ("id_uri", ValueTypeViolation),
    ]
    assert not result.unexpected_results
    assert len(result.problems) == 6
    sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
    for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
        assert one_result.res_id == expected_info[0]
        assert isinstance(one_result, expected_info[1])


if __name__ == "__main__":
    pytest.main([__file__])
