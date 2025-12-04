import json
from pathlib import Path
from typing import Any

import pytest
import regex

from dsp_tools.commands.create.project_validate import _check_for_duplicate_res_and_props
from dsp_tools.commands.create.project_validate import _check_for_undefined_cardinalities
from dsp_tools.commands.create.project_validate import _check_for_undefined_super_property
from dsp_tools.commands.create.project_validate import _check_for_undefined_super_resource
from dsp_tools.commands.create.project_validate import _collect_link_properties
from dsp_tools.commands.create.project_validate import _identify_problematic_cardinalities
from dsp_tools.commands.create.project_validate import parse_and_validate_project
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.error.exceptions import JSONFileParsingError
from dsp_tools.error.exceptions import UserFilepathNotFoundError
from dsp_tools.utils.json_parsing import parse_json_input


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


def test_validate_project(tp_systematic: dict[str, Any], tp_circular_ontology: dict[str, Any]) -> None:
    assert parse_and_validate_project(tp_systematic) is True

    with pytest.raises(BaseError, match=regex.escape("Input 'fantasy.xyz' is neither a file path nor a JSON object.")):
        parse_and_validate_project("fantasy.xyz")

    with pytest.raises(BaseError, match=regex.escape("validation error: 'hasColor' does not match")):
        parse_and_validate_project("testdata/invalid-testdata/json-project/invalid-super-property.json")

    with pytest.raises(BaseError, match=regex.escape("Your ontology contains properties derived from 'hasLinkTo'")):
        parse_and_validate_project(tp_circular_ontology)

    with pytest.raises(InputError, match=regex.escape("Listnode names must be unique across all lists")):
        parse_and_validate_project("testdata/invalid-testdata/json-project/duplicate-listnames.json")


def test_check_for_undefined_cardinalities(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_cardinality_file = "testdata/invalid-testdata/json-project/nonexisting-cardinality.json"
    with open(tp_nonexisting_cardinality_file, encoding="utf-8") as json_file:
        tp_nonexisting_cardinality: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_cardinalities(tp_systematic) is True

    with pytest.raises(
        BaseError,
        match=r"Your data model contains cardinalities with invalid propnames:\n"
        r" - Ontology 'nonexisting-cardinality-onto', resource 'TestThing': "
        r"\[':CardinalityThatWasNotDefinedInPropertiesSection'\]",
    ):
        _check_for_undefined_cardinalities(tp_nonexisting_cardinality)


def test_check_for_undefined_super_property(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_super_property_file = "testdata/invalid-testdata/json-project/nonexisting-super-property.json"
    with open(tp_nonexisting_super_property_file, encoding="utf-8") as json_file:
        tp_nonexisting_super_property: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_super_property(tp_systematic) is True

    with pytest.raises(
        BaseError,
        match=r"Your data model contains properties that are derived from an invalid super-property:\n"
        r" - Ontology 'nonexisting-super-property-onto', property 'hasSimpleText': "
        r"\[':SuperPropertyThatWasNotDefined'\]",
    ):
        _check_for_undefined_super_property(tp_nonexisting_super_property)


def test_check_for_undefined_super_resource(tp_systematic: dict[str, Any]) -> None:
    tp_nonexisting_super_resource_file = "testdata/invalid-testdata/json-project/nonexisting-super-resource.json"
    with open(tp_nonexisting_super_resource_file, encoding="utf-8") as json_file:
        tp_nonexisting_super_resource: dict[str, Any] = json.load(json_file)

    assert _check_for_undefined_super_resource(tp_systematic) is True

    with pytest.raises(
        BaseError,
        match=r"Your data model contains resources that are derived from an invalid super-resource:\n"
        r" - Ontology 'nonexisting-super-resource-onto', resource 'TestThing2': "
        r"\[':SuperResourceThatWasNotDefined'\]",
    ):
        _check_for_undefined_super_resource(tp_nonexisting_super_resource)


def test_circular_references_in_onto(tp_circular_ontology: dict[str, Any]) -> None:
    link_properties = _collect_link_properties(tp_circular_ontology)
    errors = _identify_problematic_cardinalities(tp_circular_ontology, link_properties)
    expected_errors = [
        ("circular-onto:AnyResource", "circular-onto:linkToTestThing1"),
        ("circular-onto:TestThing3", "circular-onto:linkToResource"),
    ]
    assert sorted(errors) == sorted(expected_errors)


def test_parse_json_input_file_not_found() -> None:
    err_msg = regex.escape("The provided filepath does not exist: foo/bar")
    with pytest.raises(UserFilepathNotFoundError, match=err_msg):
        parse_json_input(Path("foo/bar"))


def test_parse_json_input_invalid_file() -> None:
    err_msg = regex.escape(
        "The input file 'testdata/xml-data/test-data-systematic-4123.xml' cannot be parsed to a JSON object."
    )
    with pytest.raises(JSONFileParsingError, match=err_msg):
        parse_json_input("testdata/xml-data/test-data-systematic-4123.xml")


def test_check_for_duplicate_resources() -> None:
    tp_duplicate_resource_file = "testdata/invalid-testdata/json-project/duplicate-resource.json"
    with open(tp_duplicate_resource_file, encoding="utf-8") as json_file:
        tp_duplicate_resource: dict[str, Any] = json.load(json_file)

    with pytest.raises(
        BaseError,
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
        BaseError,
        match=r"Resource names and property names must be unique inside every ontology\.\n"
        r"Property 'hasInt' appears multiple times in the ontology 'testonto'\.\n"
        r"Property 'hasText' appears multiple times in the ontology 'testonto'\.\n",
    ):
        _check_for_duplicate_res_and_props(tp_duplicate_property)


if __name__ == "__main__":
    pytest.main([__file__])
