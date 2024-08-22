from typing import Any

import pytest

from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_one_list
from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_one_property
from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_one_resource
from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_restrictions
from dsp_tools.commands.xml_validate.deserialise_project import _extract_all_onto_properties
from dsp_tools.commands.xml_validate.deserialise_project import _extract_resources
from dsp_tools.commands.xml_validate.models.project_deserialised import ListDeserialised


def test_deserialise_lists(list_from_api: dict[str, Any]) -> None:
    res = _deserialise_one_list(list_from_api)
    assert res.list_name == "onlyList"
    assert set(res.nodes) == {"n1", "n1.1", "n1.1.1"}


class TestDeserialiseResource:
    def test_extract_resources(self, onto_json: dict[str, Any]) -> None:
        result = _extract_resources(onto_json)

    def test_deserialise_one_resource(self, one_res_class: dict[str, Any]) -> None:
        result = _deserialise_one_resource

    def test_deserialise_restrictions(self, one_res_class: dict[str, Any]) -> None:
        result = _deserialise_restrictions(one_res_class["rdfs:subClassOf"])


class TestDeserialiseProperties:
    def test_extract_all_onto_properties(self, onto_json: dict[str, Any], list_deserialised: ListDeserialised) -> None:
        result = _extract_all_onto_properties(onto_json, list_deserialised)

    def test_deserialise_one_property_list_prop(
        self, list_prop: dict[str, Any], list_deserialised: ListDeserialised
    ) -> None:
        result = _deserialise_one_property(list_prop, list_deserialised)

    def test_deserialise_one_property_link_prop(
        self, link_prop: dict[str, Any], list_deserialised: ListDeserialised
    ) -> None:
        result = _deserialise_one_property(link_prop, list_deserialised)

    def test_deserialise_one_property_simpletext_prop(
        self, simpletext_prop: dict[str, Any], list_deserialised: ListDeserialised
    ) -> None:
        result = _deserialise_one_property(simpletext_prop, list_deserialised)


if __name__ == "__main__":
    pytest.main([__file__])
