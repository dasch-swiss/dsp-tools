# mypy: disable-error-code="no-untyped-def"
import json
from pathlib import Path
from typing import Any

import pytest
import regex

from dsp_tools.commands.create.exceptions import ProjectJsonSchemaValidationError
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.project_validate import _check_for_duplicate_res_and_props
from dsp_tools.commands.create.project_validate import _check_for_undefined_cardinalities
from dsp_tools.commands.create.project_validate import _check_for_undefined_super_class
from dsp_tools.commands.create.project_validate import _check_for_undefined_super_property
from dsp_tools.commands.create.project_validate import _validate_parsed_json_project
from dsp_tools.commands.create.project_validate import parse_and_validate_project
from dsp_tools.error.exceptions import JSONFileParsingError
from dsp_tools.utils.json_parsing import parse_json_file

SERVER = "https://server.che"


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


@pytest.fixture
def tp_circular_ontology() -> dict[str, Any]:
    tp_circular_ontology_file = "testdata/invalid-testdata/json-project/circular-ontology.json"
    with open(tp_circular_ontology_file, encoding="utf-8") as json_file:
        tp_circular_ontology: dict[str, Any] = json.load(json_file)
    return tp_circular_ontology


def test_validate_project(tp_systematic: dict[str, Any]) -> None:
    assert _validate_parsed_json_project(tp_systematic, SERVER) == []


def test_json_schema_validation_error():
    with pytest.raises(
        ProjectJsonSchemaValidationError, match=regex.escape("validation error: 'hasColor' does not match")
    ):
        parse_and_validate_project(Path("testdata/invalid-testdata/json-project/invalid-super-property.json"), SERVER)


def test_circular_reference_error(tp_circular_ontology):
    result = _validate_parsed_json_project(tp_circular_ontology, SERVER)
    assert isinstance(result, list)
    assert len(result) == 1
    problem = result[0]
    # we do not know which of the two links we get returned through the graph diagnostics
    # it is either one of those two which form the circle
    circle_options = [
        "Class: circular-onto:Class1 / Property: circular-onto:linkToClass2",
        "Class: circular-onto:Class2 / Property: circular-onto:linkToClass1",
    ]
    assert problem.problems[0].problematic_object in circle_options
    assert problem.problems[0].problem == InputProblemType.MIN_CARDINALITY_ONE_WITH_CIRCLE


def test_duplicate_list_error():
    result = parse_and_validate_project(Path("testdata/invalid-testdata/json-project/duplicate-listnames.json"), SERVER)
    assert isinstance(result, list)
    assert len(result) == 1
    problem = result[0]
    assert problem.problems[0].problematic_object == "first node of testlist"
    assert problem.problems[0].problem == InputProblemType.DUPLICATE_LIST_NAME


def test_check_for_undefined_cardinalities(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_cardinality_file = "testdata/invalid-testdata/json-project/nonexisting-cardinality.json"
    with open(tp_nonexisting_cardinality_file, encoding="utf-8") as json_file:
        tp_nonexisting_cardinality: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_cardinalities(tp_systematic) is None

    problems = _check_for_undefined_cardinalities(tp_nonexisting_cardinality)
    assert problems
    assert len(problems.problems) == 1
    assert problems.problems[0].problem == InputProblemType.UNDEFINED_PROPERTY_IN_CARDINALITY
    assert "nonexisting-cardinality-onto:TestThing" in problems.problems[0].problematic_object
    assert ":CardinalityThatWasNotDefinedInPropertiesSection" in problems.problems[0].problematic_object


def test_check_for_undefined_super_property(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_super_property_file = "testdata/invalid-testdata/json-project/nonexisting-super-property.json"
    with open(tp_nonexisting_super_property_file, encoding="utf-8") as json_file:
        tp_nonexisting_super_property: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_super_property(tp_systematic) is None

    problems = _check_for_undefined_super_property(tp_nonexisting_super_property)
    assert isinstance(problems, CollectedProblems)
    assert len(problems.problems) == 1
    assert problems.problems[0].problem == InputProblemType.UNDEFINED_SUPER_PROPERTY
    assert "nonexisting-super-property-onto:hasSimpleText" in problems.problems[0].problematic_object
    assert ":SuperPropertyThatWasNotDefined" in problems.problems[0].problematic_object


def test_check_for_undefined_super_class(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_super_resource_file = "testdata/invalid-testdata/json-project/nonexisting-super-resource.json"
    with open(tp_nonexisting_super_resource_file, encoding="utf-8") as json_file:
        tp_nonexisting_super_resource: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_super_class(tp_systematic) is None

    problems = _check_for_undefined_super_class(tp_nonexisting_super_resource)
    assert isinstance(problems, CollectedProblems)
    assert len(problems.problems) == 1
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
    tp_duplicate_resource_file = "testdata/invalid-testdata/json-project/duplicate-resource.json"
    with open(tp_duplicate_resource_file, encoding="utf-8") as json_file:
        tp_duplicate_resource: dict[str, Any] = json.load(json_file)

    result = _check_for_duplicate_res_and_props(tp_duplicate_resource)
    assert len(result) == 1
    problem = result[0]
    assert problem.problems[0].problematic_object == "testonto:minimalResource"
    assert problem.problems[0].problem == InputProblemType.DUPLICATE_CLASS_NAME


def test_check_for_duplicate_properties() -> None:
    tp_duplicate_property_file = "testdata/invalid-testdata/json-project/duplicate-property.json"
    with open(tp_duplicate_property_file, encoding="utf-8") as json_file:
        tp_duplicate_property: dict[str, Any] = json.load(json_file)
    result = _check_for_duplicate_res_and_props(tp_duplicate_property)
    assert len(result) == 1
    problem = result[0]
    assert problem.problems[0].problematic_object == "testonto:hasInt"
    assert problem.problems[0].problem == InputProblemType.DUPLICATE_PROPERTY_NAME


if __name__ == "__main__":
    pytest.main([__file__])
