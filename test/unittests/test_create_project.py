"""unit tests for ontology creation"""

# pylint: disable=missing-class-docstring,missing-function-docstring

import json
import unittest
from pathlib import Path
from typing import Any

import pytest

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.project_create import _sort_prop_classes, _sort_resources
from dsp_tools.utils.project_validate import (
    _check_for_duplicate_names,
    _check_for_undefined_cardinalities,
    _check_for_undefined_super_property,
    _check_for_undefined_super_resource,
    _collect_link_properties,
    _identify_problematic_cardinalities,
    validate_project
)
from dsp_tools.utils.shared import parse_json_input


class TestProjectCreation(unittest.TestCase):
    
    test_project_systematic_file = "testdata/json-project/test-project-systematic.json"
    with open(test_project_systematic_file, encoding="utf-8") as json_file:
        test_project_systematic: dict[str, Any] = json.load(json_file)
        test_project_systematic_ontology: dict[str, Any] = test_project_systematic["project"]["ontologies"][0]
    
    test_project_circular_ontology_file = "testdata/invalid-testdata/json-project/circular-ontology.json"
    with open(test_project_circular_ontology_file, encoding="utf-8") as json_file:
        test_project_circular_ontology: dict[str, Any] = json.load(json_file)
    
    test_project_nonexisting_cardinality_file = "testdata/invalid-testdata/json-project/nonexisting-cardinality.json"
    with open(test_project_nonexisting_cardinality_file, encoding="utf-8") as json_file:
        test_project_nonexisting_cardinality: dict[str, Any] = json.load(json_file)
    
    test_project_nonexisting_super_property_file = "testdata/invalid-testdata/json-project/nonexisting-super-property.json"
    with open(test_project_nonexisting_super_property_file, encoding="utf-8") as json_file:
        test_project_nonexisting_super_property: dict[str, Any] = json.load(json_file)
    
    test_project_nonexisting_super_resource_file = "testdata/invalid-testdata/json-project/nonexisting-super-resource.json"
    with open(test_project_nonexisting_super_resource_file, encoding="utf-8") as json_file:
        test_project_nonexisting_super_resource: dict[str, Any] = json.load(json_file)
    
    test_project_duplicate_property_file = "testdata/invalid-testdata/json-project/duplicate-property.json"
    with open(test_project_duplicate_property_file, encoding="utf-8") as json_file:
        test_project_duplicate_property: dict[str, Any] = json.load(json_file)

    test_project_duplicate_resource_file = "testdata/invalid-testdata/json-project/duplicate-resource.json"
    with open(test_project_duplicate_resource_file, encoding="utf-8") as json_file:
        test_project_duplicate_resource: dict[str, Any] = json.load(json_file)
    

    def test_parse_json_input(self) -> None:
        parsed_proj_from_str_path = parse_json_input(project_file_as_path_or_parsed=self.test_project_systematic_file)
        parsed_proj_from_path_path = parse_json_input(project_file_as_path_or_parsed=Path(self.test_project_systematic_file))
        parsed_proj_from_json_obj = parse_json_input(project_file_as_path_or_parsed=self.test_project_systematic)
        self.assertDictEqual(parsed_proj_from_str_path, parsed_proj_from_path_path)
        self.assertDictEqual(parsed_proj_from_str_path, parsed_proj_from_json_obj)

        invalid = [
            ("foo/bar", r"The input must be a path to a JSON file or a parsed JSON object"), 
            ("testdata/xml-data/test-data-systematic.xml", r"cannot be parsed to a JSON object"),
        ]
        for inv, err_msg in invalid:
            with self.assertRaisesRegex(BaseError, err_msg):
                parse_json_input(inv)


    def test_sort_resources(self) -> None:
        """
        The "resources" section of an onto is a list of dictionaries. The safest way to test
        that the sorted list contains the same dicts is to sort both lists according to the
        same criteria, and then test for list equality.
        """
        onto_name: str = self.test_project_systematic_ontology["name"]
        unsorted_resources: list[dict[str, Any]] = self.test_project_systematic_ontology["resources"]
        sorted_resources = _sort_resources(unsorted_resources, onto_name)

        unsorted_resources = sorted(unsorted_resources, key=lambda a: str(a["name"]))
        sorted_resources = sorted(sorted_resources, key=lambda a: str(a["name"]))

        self.assertListEqual(unsorted_resources, sorted_resources)


    def test_sort_prop_classes(self) -> None:
        """
        The "properties" section of an onto is a list of dictionaries. The safest way to test
        that the sorted list contains the same dicts is to sort both lists according to the
        same criteria, and then test for list equality.
        """
        onto_name: str = self.test_project_systematic_ontology["name"]
        unsorted_props: list[dict[str, Any]] = self.test_project_systematic_ontology["resources"]
        sorted_props = _sort_prop_classes(unsorted_props, onto_name)

        unsorted_props = sorted(unsorted_props, key=lambda a: str(a["name"]))
        sorted_props = sorted(sorted_props, key=lambda a: str(a["name"]))

        self.assertListEqual(unsorted_props, sorted_props)


    def test_validate_project(self) -> None:
        self.assertTrue(validate_project(self.test_project_systematic_file))
        self.assertTrue(validate_project(self.test_project_systematic))
        with self.assertRaisesRegex(BaseError, r"Input 'fantasy.xyz' is neither a file path nor a JSON object."):
            validate_project("fantasy.xyz")
        with self.assertRaisesRegex(BaseError, r"validation error: 'hasColor' does not match"):
            validate_project("testdata/invalid-testdata/json-project/invalid-super-property.json")
        with self.assertRaisesRegex(BaseError, r"ERROR: Your ontology contains properties derived from 'hasLinkTo'"):
            validate_project(self.test_project_circular_ontology)


    def test_check_for_duplicate_names(self) -> None:
        with self.assertRaisesRegex(
            BaseError, 
            r"Resource names and property names must be unique inside every ontology\.\n"
            r"Resource 'anotherResource' appears multiple times in the ontology 'testonto'\.\n"
            r"Resource 'minimalResource' appears multiple times in the ontology 'testonto'\.\n"
        ):
            _check_for_duplicate_names(self.test_project_duplicate_resource)
        with self.assertRaisesRegex(
            BaseError, 
            r"Resource names and property names must be unique inside every ontology\.\n"
            r"Property 'hasInt' appears multiple times in the ontology 'testonto'\.\n"
            r"Property 'hasText' appears multiple times in the ontology 'testonto'\.\n"
        ):
            _check_for_duplicate_names(self.test_project_duplicate_property)


    def test_circular_references_in_onto(self) -> None:
        link_properties = _collect_link_properties(self.test_project_circular_ontology)
        errors = _identify_problematic_cardinalities(self.test_project_circular_ontology, link_properties)
        expected_errors = [
            ("circular-onto:AnyResource", "circular-onto:linkToTestThing1"),
            ("circular-onto:TestThing3", "circular-onto:linkToResource")
        ]
        self.assertListEqual(sorted(errors), sorted(expected_errors))


    def test_check_for_undefined_cardinalities(self) -> None:
        self.assertTrue(_check_for_undefined_cardinalities(self.test_project_systematic))
        with self.assertRaisesRegex(
            BaseError, 
            r"Your data model contains cardinalities with invalid propnames:\n"
            r" - Ontology 'nonexisting-cardinality-onto', resource 'TestThing': \[':CardinalityThatWasNotDefinedInPropertiesSection'\]"
        ):
            _check_for_undefined_cardinalities(self.test_project_nonexisting_cardinality)


    def test_check_for_undefined_super_property(self) -> None:
        self.assertTrue(_check_for_undefined_super_property(self.test_project_systematic))
        with self.assertRaisesRegex(
            BaseError, 
            r"Your data model contains properties that are derived from an invalid super-property:\n"
            r" - Ontology 'nonexisting-super-property-onto', property 'hasSimpleText': \[':SuperPropertyThatWasNotDefined'\]"
        ):
            _check_for_undefined_super_property(self.test_project_nonexisting_super_property)


    def test_check_for_undefined_super_resource(self) -> None:
        self.assertTrue(_check_for_undefined_super_resource(self.test_project_systematic))
        with self.assertRaisesRegex(
            BaseError, 
            r"Your data model contains resources that are derived from an invalid super-resource:\n"
            r" - Ontology 'nonexisting-super-resource-onto', resource 'TestThing2': \[':SuperResourceThatWasNotDefined'\]"
        ):
            _check_for_undefined_super_resource(self.test_project_nonexisting_super_resource)


if __name__ == "__main__":
    pytest.main([__file__])
