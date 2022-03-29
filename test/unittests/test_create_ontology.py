"""unit tests for ontology creation"""
import unittest
import json
from typing import Any

from knora.dsplib.utils.onto_create_ontology import *


class TestOntoCreation(unittest.TestCase):
    with open('testdata/test-onto.json', 'r') as json_file:
        json_onto = json.loads(json_file.read())
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


if __name__ == '__main__':
    unittest.main()
