import json
from pathlib import Path
from typing import Any

import pytest
import regex

from dsp_tools.commands.create.exceptions import ProjectJsonSchemaValidationError
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.project_validate import _validate_parsed_json_project
from dsp_tools.commands.create.project_validate import parse_and_validate_project
from dsp_tools.utils.exceptions import JSONFileParsingError
from dsp_tools.utils.json_parsing import parse_json_file

SERVER = "http://0.0.0.0:3333"


@pytest.fixture
def tp_systematic() -> dict[str, Any]:
    tp_systematic_file = "testdata/json-project/systematic-project-4123.json"
    with open(tp_systematic_file, encoding="utf-8") as json_file:
        tp_systematic: dict[str, Any] = json.load(json_file)
    return tp_systematic


@pytest.fixture
def tp_systematic_ontology(tp_systematic: dict[str, Any]) -> dict[str, Any]:
    onto: dict[str, Any] = tp_systematic["project"]["ontologies"][0]
    return onto


def test_validate_project(tp_systematic: dict[str, Any]) -> None:
    result, potential_circles = _validate_parsed_json_project(tp_systematic, SERVER)
    assert not potential_circles
    assert isinstance(result, ParsedProject)


def test_json_schema_validation_error():
    with pytest.raises(
        ProjectJsonSchemaValidationError, match=regex.escape("validation error: 'hasColor' does not match")
    ):
        parse_and_validate_project(Path("testdata/invalid-testdata/json-project/invalid-super-property.json"), SERVER)


def test_circular_reference_error():
    result, potential_circles = parse_and_validate_project(
        Path("testdata/invalid-testdata/json-project/circular-ontology.json"), SERVER
    )
    assert len(potential_circles) == 1
    assert potential_circles[0].subject == "circular-onto:Class1"
    assert potential_circles[0].prop == "circular-onto:linkToKnoraApiClass"
    assert potential_circles[0].object_cls == "knora-api:Resource"
    assert potential_circles[0].card == "1-n"
    assert isinstance(result, list)
    assert len(result) == 3

    circular_min_card = next(
        x for x in result if x.problems[0].problem == InputProblemType.MIN_CARDINALITY_ONE_WITH_CIRCLE
    )
    assert len(circular_min_card.problems) == 1
    expected_min_card = (
        "Cycle:\n"
        "    circular-onto:Class1 -- circular-onto:linkToClass2 --> circular-onto:Class2\n"
        "    circular-onto:Class2 -- circular-onto:linkToClass1 --> circular-onto:Class1"
    )
    assert circular_min_card.problems[0].problematic_object == expected_min_card

    circular_prop = next(x for x in result if x.problems[0].problem == InputProblemType.CIRCULAR_PROPERTY_INHERITANCE)
    assert len(circular_prop.problems) == 1
    expected_prop = (
        "Cycle: circular-onto:circularProperty2 -> circular-onto:circularProperty1 -> circular-onto:circularProperty2"
    )
    assert circular_prop.problems[0].problematic_object == expected_prop

    circular_cls = next(x for x in result if x.problems[0].problem == InputProblemType.CIRCULAR_CLASS_INHERITANCE)
    assert len(circular_cls.problems) == 1
    expected_cls = "Cycle: circular-onto:CircularClass2 -> circular-onto:CircularClass1 -> circular-onto:CircularClass2"
    assert circular_cls.problems[0].problematic_object == expected_cls


def test_duplicate_list_error():
    result, potential_circles = parse_and_validate_project(
        Path("testdata/invalid-testdata/json-project/duplicate-listnames.json"), SERVER
    )
    assert not potential_circles
    assert isinstance(result, list)
    assert len(result) == 1
    problem = result[0]
    assert problem.problems[0].problematic_object == "Node name 'first node of testlist'"
    assert problem.problems[0].problem == InputProblemType.DUPLICATE_LIST_NODE_NAME


def test_check_for_undefined_cardinalities() -> None:
    result, potential_circles = parse_and_validate_project(
        Path("testdata/invalid-testdata/json-project/cardinality-problems.json"), SERVER
    )
    assert not potential_circles
    assert isinstance(result, list)
    assert len(result) == 2
    undefined_card = next(
        x for x in result if x.problems[0].problem == InputProblemType.UNDEFINED_PROPERTY_IN_CARDINALITY
    )
    assert len(undefined_card.problems) == 1
    assert (
        undefined_card.problems[0].problematic_object
        == "Class 'onto:UndefinedPropInCardinality' / Property 'onto:CardinalityThatWasNotDefinedInPropertiesSection'"
    )
    duplicate_card = next(
        x for x in result if x.problems[0].problem == InputProblemType.DUPLICATE_PROPERTY_IN_CARDINALITY
    )
    assert len(duplicate_card.problems) == 1
    assert (
        duplicate_card.problems[0].problematic_object
        == "Class 'onto:DuplicateCardinality' / Properties 'onto:hasSimpleText'"
    )


def test_check_for_undefined_super_property() -> None:
    result, potential_circles = parse_and_validate_project(
        Path("testdata/invalid-testdata/json-project/nonexisting-super-property.json"), SERVER
    )
    assert not potential_circles
    assert isinstance(result, list)
    assert len(result) == 1
    problems = result[0]
    assert len(problems.problems) == 1
    assert problems.problems[0].problem == InputProblemType.UNDEFINED_SUPER_PROPERTY
    assert "nonexisting-super-property-onto:hasSimpleText" in problems.problems[0].problematic_object
    assert ":SuperPropertyThatWasNotDefined" in problems.problems[0].problematic_object


def test_check_for_undefined_super_class() -> None:
    result, potential_circles = parse_and_validate_project(
        Path("testdata/invalid-testdata/json-project/nonexisting-super-resource.json"), SERVER
    )
    assert not potential_circles
    assert isinstance(result, list)
    assert len(result) == 1
    problems = result[0]
    assert problems.problems[0].problem == InputProblemType.UNDEFINED_SUPER_CLASS
    assert "nonexisting-super-resource-onto:TestThing2" in problems.problems[0].problematic_object
    assert ":SuperResourceThatWasNotDefined" in problems.problems[0].problematic_object


def test_parse_json_file_invalid_file() -> None:
    err_msg = regex.escape(
        "The input file 'testdata/xml-data/test-data-systematic-4123.xml' cannot be parsed to a JSON object."
    )
    with pytest.raises(JSONFileParsingError, match=err_msg):
        parse_json_file(Path("testdata/xml-data/test-data-systematic-4123.xml"))


def test_check_for_duplicate_resources() -> None:
    result, potential_circles = parse_and_validate_project(
        Path("testdata/invalid-testdata/json-project/duplicate-resource.json"), SERVER
    )
    assert not potential_circles
    assert isinstance(result, list)
    assert len(result) == 1
    problem = result[0]
    assert problem.problems[0].problematic_object == "testonto:minimalResource"
    assert problem.problems[0].problem == InputProblemType.DUPLICATE_CLASS_NAME


def test_check_for_duplicate_properties() -> None:
    result, potential_circles = parse_and_validate_project(
        Path("testdata/invalid-testdata/json-project/duplicate-property.json"), SERVER
    )
    assert not potential_circles
    assert isinstance(result, list)
    assert len(result) == 1
    problem = result[0]
    assert problem.problems[0].problematic_object == "testonto:hasInt"
    assert problem.problems[0].problem == InputProblemType.DUPLICATE_PROPERTY_NAME


if __name__ == "__main__":
    pytest.main([__file__])
