"""unit tests for ontology creation"""
import unittest
import json
from typing import Any
import jsonpath_ng.ext

from knora.dsplib.utils.onto_create_ontology import sort_resources, sort_prop_classes
from knora.dsplib.utils.onto_validate import collect_link_properties, identify_problematic_cardinalities


class TestOntoCreation(unittest.TestCase):
    with open('testdata/test-onto.json', 'r') as json_file:
        project: dict[str, Any] = json.load(json_file)
        ontology: dict[str, Any] = project['project']['ontologies'][0]

    circular_onto = {
        "project": {
            "shortcode": "1233",
            "shortname": "test",
            "longname": "test",
            "descriptions": {"en": "test"},
            "ontologies": [
                {
                    "name": "testonto",
                    "label": "Test ontology",
                    "properties": [
                        {
                            "name": "linkToResource",
                            "super": ["hasLinkTo"],
                            "object": "Resource",
                            "labels": {"en": "has region"},
                            "gui_element": "Searchbox"
                        },
                        {
                            "name": "linkToTestThing1",
                            "super": ["foaf:fantasy", "isPartOf"],
                            "object": ":TestThing1",
                            "labels": {"en": "has region"},
                            "gui_element": "Searchbox"
                        },
                        {
                            "name": "linkToTestThing2",
                            "super": ["isAnnotationOf", "foaf:fantasy"],
                            "object": ":TestThing2",
                            "labels": {"en": "has region"},
                            "gui_element": "Searchbox"
                        },
                        {
                            "name": "linkToTestThing3",
                            "super": ["isRegionOf"],
                            "object": ":TestThing3",
                            "labels": {"en": "has region"},
                            "gui_element": "Searchbox"
                        }
                    ],
                    "resources": [
                        {
                            "name": "TestThing1",
                            "super": "Resource",
                            "labels": {"en": "TestThing1"},
                            "cardinalities": [
                                {"propname": ":linkToTestThing2", "cardinality": "0-1"}
                            ]
                        },
                        {
                            "name": "TestThing2",
                            "super": "Resource",
                            "labels": {"en": "TestThing2"},
                            "cardinalities": [
                                {"propname": ":linkToTestThing3", "cardinality": "0-n"}
                            ]
                        },
                        {
                            "name": "TestThing3",
                            "super": "Resource",
                            "labels": {"en": "TestThing3"},
                            "cardinalities": [
                                {"propname": ":linkToResource", "cardinality": "1"}
                            ]
                        },
                        {
                            "name": "AnyResource",
                            "super": "Resource",
                            "labels": {"en": "AnyResource"},
                            "cardinalities": [
                                {"propname": ":linkToTestThing1", "cardinality": "1-n"},
                            ]
                        }
                    ]
                }
            ]
        }
    }

    def test_sort_resources(self) -> None:
        """
        The 'resources' section of an onto is a list of dictionaries. The safest way to test
        that the sorted list contains the same dicts is to sort both lists according to the
        same criteria, and then test for list equality.
        """
        onto_name: str = self.ontology['name']
        unsorted_resources: list[dict[str, Any]] = self.ontology['resources']
        sorted_resources = sort_resources(unsorted_resources, onto_name)

        unsorted_resources = sorted(unsorted_resources, key=lambda a: a['name'])
        sorted_resources = sorted(sorted_resources, key=lambda a: a['name'])

        self.assertListEqual(unsorted_resources, sorted_resources)


    def test_sort_prop_classes(self) -> None:
        """
        The 'properties' section of an onto is a list of dictionaries. The safest way to test
        that the sorted list contains the same dicts is to sort both lists according to the
        same criteria, and then test for list equality.
        """
        onto_name: str = self.ontology['name']
        unsorted_props: list[dict[str, Any]] = self.ontology['resources']
        sorted_props = sort_prop_classes(unsorted_props, onto_name)

        unsorted_props = sorted(unsorted_props, key=lambda a: a['name'])
        sorted_props = sorted(sorted_props, key=lambda a: a['name'])

        self.assertListEqual(unsorted_props, sorted_props)


    def test_circular_references_in_onto(self) -> None:
        link_properties = collect_link_properties(self.circular_onto)
        errors = identify_problematic_cardinalities(self.circular_onto, link_properties)
        expected_errors = [
            ('testonto:AnyResource', 'testonto:linkToTestThing1'),
            ('testonto:TestThing3', 'testonto:linkToResource')
        ]
        self.assertListEqual(sorted(errors), sorted(expected_errors))


if __name__ == '__main__':
    unittest.main()
