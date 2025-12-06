# mypy: disable-error-code="no-untyped-def"
import json
from pathlib import Path
from typing import Any

import pytest
import regex

from dsp_tools.commands.create.exceptions import DuplicateClassAndPropertiesError
from dsp_tools.commands.create.exceptions import DuplicateListNamesError
from dsp_tools.commands.create.exceptions import MinCardinalityOneWithCircleError
from dsp_tools.commands.create.exceptions import ProjectJsonSchemaValidationError
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.project_validate import _check_for_duplicate_res_and_props
from dsp_tools.commands.create.project_validate import _check_for_undefined_cardinalities
from dsp_tools.commands.create.project_validate import _check_for_undefined_super_class
from dsp_tools.commands.create.project_validate import _check_for_undefined_super_property
from dsp_tools.commands.create.project_validate import _collect_link_properties
from dsp_tools.commands.create.project_validate import _identify_problematic_cardinalities
from dsp_tools.commands.create.project_validate import _validate_parsed_project
from dsp_tools.commands.create.project_validate import parse_and_validate_project
from dsp_tools.error.exceptions import JSONFileParsingError
from dsp_tools.utils.json_parsing import parse_json_file


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
    assert _validate_parsed_project(tp_systematic) is True


def test_json_schema_validation_error():
    with pytest.raises(
        ProjectJsonSchemaValidationError, match=regex.escape("validation error: 'hasColor' does not match")
    ):
        parse_and_validate_project(Path("testdata/invalid-testdata/json-project/invalid-super-property.json"))


def test_circular_reference_error(tp_circular_ontology):
    with pytest.raises(
        MinCardinalityOneWithCircleError,
        match=regex.escape("Your ontology contains properties derived from 'hasLinkTo'"),
    ):
        _validate_parsed_project(tp_circular_ontology)


def test_duplicate_list_error():
    with pytest.raises(DuplicateListNamesError, match=regex.escape("Listnode names must be unique across all lists")):
        parse_and_validate_project(Path("testdata/invalid-testdata/json-project/duplicate-listnames.json"))


def test_check_for_undefined_cardinalities(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_cardinality_file = "testdata/invalid-testdata/json-project/nonexisting-cardinality.json"
    with open(tp_nonexisting_cardinality_file, encoding="utf-8") as json_file:
        tp_nonexisting_cardinality: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_cardinalities(tp_systematic) == []

    problems = _check_for_undefined_cardinalities(tp_nonexisting_cardinality)
    assert problems
    assert len(problems) == 1
    assert problems[0].problem == InputProblemType.UNDEFINED_PROPERTY_IN_CARDINALITY
    assert "nonexisting-cardinality-onto:TestThing" in problems[0].problematic_object
    assert ":CardinalityThatWasNotDefinedInPropertiesSection" in problems[0].problematic_object


def test_check_for_undefined_super_property(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_super_property_file = "testdata/invalid-testdata/json-project/nonexisting-super-property.json"
    with open(tp_nonexisting_super_property_file, encoding="utf-8") as json_file:
        tp_nonexisting_super_property: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_super_property(tp_systematic) == []

    problems = _check_for_undefined_super_property(tp_nonexisting_super_property)
    assert problems
    assert len(problems) == 1
    assert problems[0].problem == InputProblemType.UNDEFINED_SUPER_PROPERTY
    assert "nonexisting-super-property-onto:hasSimpleText" in problems[0].problematic_object
    assert ":SuperPropertyThatWasNotDefined" in problems[0].problematic_object


def test_check_for_undefined_super_class(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_super_resource_file = "testdata/invalid-testdata/json-project/nonexisting-super-resource.json"
    with open(tp_nonexisting_super_resource_file, encoding="utf-8") as json_file:
        tp_nonexisting_super_resource: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_super_class(tp_systematic) == []

    problems = _check_for_undefined_super_class(tp_nonexisting_super_resource)
    assert problems
    assert len(problems) == 1
    assert problems[0].problem == InputProblemType.UNDEFINED_SUPER_CLASS
    assert "nonexisting-super-resource-onto:TestThing2" in problems[0].problematic_object
    assert ":SuperResourceThatWasNotDefined" in problems[0].problematic_object


def test_circular_references_in_onto(tp_circular_ontology: dict[str, Any]) -> None:
    link_properties = _collect_link_properties(tp_circular_ontology)
    errors = _identify_problematic_cardinalities(tp_circular_ontology, link_properties)
    expected_errors = [
        ("circular-onto:AnyResource", "circular-onto:linkToTestThing1"),
        ("circular-onto:TestThing3", "circular-onto:linkToResource"),
    ]
    assert sorted(errors) == sorted(expected_errors)


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

    with pytest.raises(
        DuplicateClassAndPropertiesError,
        match=r"Resource names and property names must be unique inside every ontology\.\n"
        r"Resource 'anotherResource' appears multiple times in the ontology 'testonto'\.\n"
        r"Resource 'minimalResource' appears multiple times in the ontology 'testonto'\.\n",
    ):
        _check_for_duplicate_res_and_props(tp_duplicate_resource)


def test_check_for_duplicate_properties() -> None:
    tp_duplicate_property_file = "testdata/invalid-testdata/json-project/duplicate-property.json"
    with open(tp_duplicate_property_file, encoding="utf-8") as json_file:
        tp_duplicate_property: dict[str, Any] = json.load(json_file)
    with pytest.raises(
        DuplicateClassAndPropertiesError,
        match=r"Resource names and property names must be unique inside every ontology\.\n"
        r"Property 'hasInt' appears multiple times in the ontology 'testonto'\.\n"
        r"Property 'hasText' appears multiple times in the ontology 'testonto'\.\n",
    ):
        _check_for_duplicate_res_and_props(tp_duplicate_property)


if __name__ == "__main__":
    pytest.main([__file__])
