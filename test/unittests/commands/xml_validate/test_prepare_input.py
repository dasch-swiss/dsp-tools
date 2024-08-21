import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.models.deserialised import LinkValueDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ListValueDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import SimpleTextDeserialised
from dsp_tools.commands.xml_validate.models.xml_deserialised import ResourceXML
from dsp_tools.commands.xml_validate.prepare_input import _deserialise_list_prop
from dsp_tools.commands.xml_validate.prepare_input import _deserialise_one_resource
from dsp_tools.commands.xml_validate.prepare_input import _deserialise_resptr_prop
from dsp_tools.commands.xml_validate.prepare_input import _deserialise_text_prop
from dsp_tools.commands.xml_validate.prepare_input import _transform_into_xml_deserialised


def test_transform_into_xml_deserialised(parsed_xml: etree._Element) -> None:
    result = _transform_into_xml_deserialised(parsed_xml)
    assert result.shortcode == "9999"
    assert result.default_onto == "onto"
    assert len(result.xml_resources) == 1
    resource = result.xml_resources[0]
    assert resource.res_attrib == {"label": "Label", "restype": ":Class", "id": "class-id"}
    assert len(resource.values) == 2


def test_deserialise_one_resource(resource_xml: ResourceXML) -> None:
    result = _deserialise_one_resource(resource_xml)
    assert result.res_id == "class-id"
    assert result.label == "Label"
    assert len(result.values) == 3


def test_deserialise_list_prop(list_prop: etree._Element) -> None:
    result = _deserialise_list_prop(list_prop)
    assert len(result) == 1
    deserialised = result[0]
    assert isinstance(deserialised, ListValueDeserialised)
    assert deserialised.prop_name == ":listProp"
    assert deserialised.prop_value == "listNode"
    assert deserialised.list_name == "onlyList"
    assert not deserialised.comments


def test_deserialise_text_prop(text_prop: etree._Element) -> None:
    result = _deserialise_text_prop(text_prop)
    assert len(result) == 2
    sorted_res = sorted(result, key=lambda x: x.prop_value)
    one = sorted_res[0]
    assert isinstance(one, SimpleTextDeserialised)
    assert one.prop_name == ":hasSimpleText"
    assert one.prop_value == "text content"
    assert not one.comments
    two = sorted_res[1]
    assert isinstance(two, SimpleTextDeserialised)
    assert two.prop_name == ":hasSimpleText"
    assert two.prop_value == "text content 2"
    assert two.comments == "Comment"


def test_deserialise_resptr_prop(resptr_prop: etree._Element) -> None:
    result = _deserialise_resptr_prop(resptr_prop)
    assert len(result) == 1
    deserialised = result[0]
    assert isinstance(deserialised, LinkValueDeserialised)
    assert deserialised.prop_name == ":linkProp"
    assert deserialised.prop_value == "link-id"
    assert not deserialised.comments


if __name__ == "__main__":
    pytest.main([__file__])
