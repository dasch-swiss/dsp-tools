from typing import Any

import pytest

from dsp_tools.commands.project.create.project_create_ontologies import _sort_prop_classes
from dsp_tools.commands.project.create.project_create_ontologies import _sort_resources


def test_sort_resources(tp_systematic_ontology: dict[str, Any]) -> None:
    onto_name: str = tp_systematic_ontology["name"]
    unsorted_resources: list[dict[str, Any]] = tp_systematic_ontology["resources"]
    sorted_resources = _sort_resources(unsorted_resources, onto_name)

    unsorted_resources = sorted(unsorted_resources, key=lambda a: str(a["name"]))
    sorted_resources = sorted(sorted_resources, key=lambda a: str(a["name"]))

    assert unsorted_resources == sorted_resources


def test_sort_prop_classes(tp_systematic_ontology: dict[str, Any]) -> None:
    onto_name: str = tp_systematic_ontology["name"]
    unsorted_props: list[dict[str, Any]] = tp_systematic_ontology["resources"]
    sorted_props = _sort_prop_classes(unsorted_props, onto_name)

    unsorted_props = sorted(unsorted_props, key=lambda a: str(a["name"]))
    sorted_props = sorted(sorted_props, key=lambda a: str(a["name"]))

    assert unsorted_props == sorted_props


if __name__ == "__main__":
    pytest.main([__file__])
