"""unit tests for ontology creation"""
import unittest
import json
from typing import Any
import jsonpath_ng.ext

from knora.dsplib.utils.onto_create_ontology import sort_resources, sort_prop_classes
from knora.dsplib.utils.onto_validate import collect_link_properties, identify_problematic_cardinalities


class TestOntoCreation(unittest.TestCase):
    with open('testdata/test-onto.json', 'r') as json_file:
        json_onto: dict[str, Any] = json.load(json_file)
    ontology: dict[str, Any] = json_onto['project']['ontologies'][0]

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
        self.ontology['properties'].extend([
            {
                "name": "hasLinkToResource",
                "super": ["hasLinkTo"],
                "object": "Resource",
                "labels": {"en": "has region"},
                "gui_element": "Searchbox"
            },
            {
                "name": "hasLinkToAudioThing",
                "super": ["hasLinkTo"],
                "object": ":AudioThing",
                "labels": {"en": "hasLinkToAudioThing"},
                "gui_element": "Searchbox"
            }
        ])

        TestThing_hasTestThing2 = jsonpath_ng.ext.parse(
            '$.resources[?name="TestThing"].cardinalities[?propname=":hasTestThing2"]').find(self.ontology)[0].value
        TestThing_hasTestThing2['cardinality'] = '1-n'
        TestThing2_hasTestThing = jsonpath_ng.ext.parse(
            '$.resources[?name="TestThing2"].cardinalities[?propname=":hasTestThing"]').find(self.ontology)[0].value
        TestThing2_hasTestThing['cardinality'] = '1-n'
        TestThing2_cards = jsonpath_ng.ext.parse(
            '$.resources[?name="TestThing2"].cardinalities').find(self.ontology)[0].value
        TestThing2_cards.append({
            "propname": ":hasLinkToAudioThing",
            "cardinality": "1"
        })
        AudioThing_cards = jsonpath_ng.ext.parse('$.resources[?name="AudioThing"].cardinalities').find(self.ontology)[0].value
        AudioThing_cards.append({
            "propname": ":hasTestThing",
            "cardinality": "1"
        })

        link_properties = collect_link_properties(self.project)
        errors = identify_problematic_cardinalities(self.project, link_properties)
        expected_errors = {''}
        self.assertSetEqual(errors, expected_errors)


if __name__ == '__main__':
    unittest.main()
