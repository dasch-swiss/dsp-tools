"""unit tests for ontology creation"""
import json
import unittest
from typing import Any

from dsp_tools.models.helpers import BaseError
from dsp_tools.utils.project_create import _sort_resources, _sort_prop_classes
from dsp_tools.utils.project_validate import _collect_link_properties, _identify_problematic_cardinalities, \
    validate_project


class TestProjectCreation(unittest.TestCase):
    test_project_systematic_file = "testdata/test-project-systematic.json"
    with open(test_project_systematic_file, "r") as json_file:
        test_project_systematic: dict[str, Any] = json.load(json_file)
        test_project_systematic_ontology: dict[str, Any] = test_project_systematic["project"]["ontologies"][0]
    test_project_circular_ontology_file = "testdata/invalid_testdata/test-project-circular-ontology.json"
    with open(test_project_circular_ontology_file, "r") as json_file:
        test_project_circular_ontology: dict[str, Any] = json.load(json_file)


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
            validate_project("testdata/invalid_testdata/test-project-invalid-super-property.json")
        with self.assertRaisesRegex(BaseError, r"ERROR: Your ontology contains properties derived from 'hasLinkTo'"):
            validate_project(self.test_project_circular_ontology)


    def test_circular_references_in_onto(self) -> None:
        link_properties = _collect_link_properties(self.test_project_circular_ontology)
        errors = _identify_problematic_cardinalities(self.test_project_circular_ontology, link_properties)
        expected_errors = [
            ("testonto:AnyResource", "testonto:linkToTestThing1"),
            ("testonto:TestThing3", "testonto:linkToResource")
        ]
        self.assertListEqual(sorted(errors), sorted(expected_errors))


if __name__ == "__main__":
    unittest.main()
