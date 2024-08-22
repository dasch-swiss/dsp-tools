from typing import Any

import pytest

from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_link_prop
from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_list_prop
from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_one_list
from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_one_resource
from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_other_property
from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_restrictions
from dsp_tools.commands.xml_validate.deserialise_project import _extract_all_onto_properties
from dsp_tools.commands.xml_validate.deserialise_project import _extract_resources
from dsp_tools.commands.xml_validate.models.project_deserialised import CardinalityOne
from dsp_tools.commands.xml_validate.models.project_deserialised import LinkProperty
from dsp_tools.commands.xml_validate.models.project_deserialised import ListDeserialised
from dsp_tools.commands.xml_validate.models.project_deserialised import ListProperty
from dsp_tools.commands.xml_validate.models.project_deserialised import SimpleTextProperty


def test_deserialise_lists(list_from_api: dict[str, Any]) -> None:
    res = _deserialise_one_list(list_from_api)
    assert res.list_name == "onlyList"
    assert set(res.nodes) == {"n1", "n1.1", "n1.1.1"}


class TestDeserialiseResource:
    def test_extract_resources(self, onto_json: dict[str, Any]) -> None:
        assert len(_extract_resources(onto_json)) == 3

    def test_deserialise_one_resource(self, one_res_class: dict[str, Any]) -> None:
        result = _deserialise_one_resource(one_res_class)
        assert result.cls_id == "onto:CardOneResource"
        assert result.subClassOf == ["knora-api:Resource"]
        assert len(result.restrictions) == 1

    def test_deserialise_restrictions(self, one_res_class: dict[str, Any]) -> None:
        result = _deserialise_restrictions(one_res_class["rdfs:subClassOf"])
        assert len(result) == 1
        restriction = result[0]
        assert isinstance(restriction, CardinalityOne)
        assert restriction.onProperty == "onto:hasSimpleText"


class TestDeserialiseProperties:
    def test_deserialise_other_property(self, simpletext_prop: dict[str, Any]) -> None:
        result = _deserialise_other_property(simpletext_prop)
        assert isinstance(result, SimpleTextProperty)
        assert result.prop_name == "onto:hasSimpleText"

    def test_deserialise_other_property_none(self, link_prop: dict[str, Any], list_prop: dict[str, Any]):
        assert not _deserialise_other_property(link_prop)
        assert not _deserialise_other_property(list_prop)

    def test_extract_all_onto_properties(self, onto_json: dict[str, Any]) -> None:
        result = _extract_all_onto_properties(
            onto_json,
        )
        assert len(result) == 3

    def test_deserialise_list_prop(self, list_prop: dict[str, Any], list_deserialised: ListDeserialised) -> None:
        result = _deserialise_list_prop(list_prop, list_deserialised)
        assert isinstance(result, ListProperty)
        assert result.prop_name == "onto:listProp"
        assert result.list_name == "onlyList"
        assert set(result.nodes) == {"n1", "n1.1", "n1.1.1"}

    def test_deserialise_link_prop(self, link_prop: dict[str, Any], list_deserialised: ListDeserialised) -> None:
        result = _deserialise_link_prop(
            link_prop,
        )
        assert isinstance(result, LinkProperty)
        assert result.prop_name == "onto:linkProp"
        assert result.objectType == {"onto:CardOneResource", "onto:SubClass"}


if __name__ == "__main__":
    pytest.main([__file__])
