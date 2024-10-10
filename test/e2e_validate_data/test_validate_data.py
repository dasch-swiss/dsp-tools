from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.validate_data.models.input_problems import ContentRegexViolation
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import ValidationReports
from dsp_tools.commands.validate_data.reformat_validaton_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
from test.e2e_validate_data.setup_testcontainers import get_containers

CREDS = ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")
LOCAL_API = "http://0.0.0.0:3333"
SAVE_GRAPHS = False


@pytest.fixture
def _create_project() -> Iterator[None]:
    with get_containers():
        success = create_project(Path("testdata/validate-data/project.json"), CREDS, verbose=True)
        assert success
        yield


@pytest.fixture
def cardinality_correct(_create_project: None) -> ValidationReports:
    return _get_validation_result(LOCAL_API, Path("testdata/validate-data/data/cardinality_correct.xml"), SAVE_GRAPHS)


@pytest.fixture
def cardinality_violation(_create_project: None) -> ValidationReports:
    return _get_validation_result(LOCAL_API, Path("testdata/validate-data/data/cardinality_violation.xml"), SAVE_GRAPHS)


@pytest.fixture
def content_correct(_create_project: None) -> ValidationReports:
    return _get_validation_result(LOCAL_API, Path("testdata/validate-data/data/content_correct.xml"), SAVE_GRAPHS)


@pytest.fixture
def content_violation(_create_project: None) -> ValidationReports:
    return _get_validation_result(LOCAL_API, Path("testdata/validate-data/data/content_violation.xml"), SAVE_GRAPHS)


@pytest.fixture
def every_combination_once(_create_project: None) -> ValidationReports:
    return _get_validation_result(
        LOCAL_API, Path("testdata/validate-data/data/every_combination_once.xml"), SAVE_GRAPHS
    )


@pytest.fixture
def minimal_correct(_create_project: None) -> ValidationReports:
    return _get_validation_result(LOCAL_API, Path("testdata/validate-data/data/minimal_correct.xml"), SAVE_GRAPHS)


@pytest.fixture
def value_type_violation(_create_project: None) -> ValidationReports:
    return _get_validation_result(LOCAL_API, Path("testdata/validate-data/data/value_type_violation.xml"), SAVE_GRAPHS)


class TestGetValidationResult:
    def test_cardinality_correct(self, cardinality_correct: ValidationReports) -> None:
        assert cardinality_correct.conforms

    def test_cardinality_violation(self, cardinality_violation: ValidationReports) -> None:
        assert not cardinality_violation.conforms

    def test_content_correct(self, content_correct: ValidationReports) -> None:
        assert content_correct.conforms

    def test_content_violation(self, content_violation: ValidationReports) -> None:
        assert not content_violation.conforms

    def test_every_combination_once(self, every_combination_once: ValidationReports) -> None:
        assert not every_combination_once.conforms

    def test_minimal_correct(self, minimal_correct: ValidationReports) -> None:
        assert minimal_correct.conforms

    def test_value_type_violation(self, value_type_violation: ValidationReports) -> None:
        assert not value_type_violation.conforms


class TestReformatValidationGraph:
    def test_reformat_cardinality_violation(self, cardinality_violation: ValidationReports) -> None:
        result = reformat_validation_graph(cardinality_violation)
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

    def test_reformat_value_type_violation(self, value_type_violation: ValidationReports) -> None:
        result = reformat_validation_graph(value_type_violation)
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

    def test_reformat_content_violation(self, content_violation: ValidationReports) -> None:
        result = reformat_validation_graph(content_violation)
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

    def test_reformat_every_constraint_once(self, every_combination_once: ValidationReports) -> None:
        result = reformat_validation_graph(every_combination_once)
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