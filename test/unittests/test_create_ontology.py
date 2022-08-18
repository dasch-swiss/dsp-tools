"""unit tests for ontology creation"""
import unittest
import json
from typing import Any

from knora.dsplib.utils.onto_create_ontology import _sort_resources, _sort_prop_classes
from knora.dsplib.utils.onto_validate import _collect_link_properties, _identify_problematic_cardinalities


class TestOntoCreation(unittest.TestCase):
    with open('testdata/test-project-systematic.json', 'r') as json_file:
        project: dict[str, Any] = json.load(json_file)
        ontology: dict[str, Any] = project['project']['ontologies'][0]
    with open('testdata/test-project-circular-ontology.json', 'r') as json_file:
        circular_onto: dict[str, Any] = json.load(json_file)

    def test_sort_resources(self) -> None:
        """
        The 'resources' section of an onto is a list of dictionaries. The safest way to test
        that the sorted list contains the same dicts is to sort both lists according to the
        same criteria, and then test for list equality.
        """
        onto_name: str = self.ontology['name']
        unsorted_resources: list[dict[str, Any]] = self.ontology['resources']
        sorted_resources = _sort_resources(unsorted_resources, onto_name)

        unsorted_resources = sorted(unsorted_resources, key=lambda a: str(a['name']))
        sorted_resources = sorted(sorted_resources, key=lambda a: str(a['name']))

        self.assertListEqual(unsorted_resources, sorted_resources)

    def test_sort_prop_classes(self) -> None:
        """
        The 'properties' section of an onto is a list of dictionaries. The safest way to test
        that the sorted list contains the same dicts is to sort both lists according to the
        same criteria, and then test for list equality.
        """
        onto_name: str = self.ontology['name']
        unsorted_props: list[dict[str, Any]] = self.ontology['resources']
        sorted_props = _sort_prop_classes(unsorted_props, onto_name)

        unsorted_props = sorted(unsorted_props, key=lambda a: str(a['name']))
        sorted_props = sorted(sorted_props, key=lambda a: str(a['name']))

        self.assertListEqual(unsorted_props, sorted_props)


    def test_circular_references_in_onto(self) -> None:
        link_properties = _collect_link_properties(self.circular_onto)
        errors = _identify_problematic_cardinalities(self.circular_onto, link_properties)
        expected_errors = [
            ('testonto:AnyResource', 'testonto:linkToTestThing1'),
            ('testonto:TestThing3', 'testonto:linkToResource')
        ]
        self.assertListEqual(sorted(errors), sorted(expected_errors))


if __name__ == '__main__':
    unittest.main()
