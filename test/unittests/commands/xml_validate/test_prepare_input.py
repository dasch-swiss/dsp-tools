import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.models.data_deserialised import LinkValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ListValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import SimpleTextData
from dsp_tools.commands.xml_validate.prepare_input import _deserialise_list_prop
from dsp_tools.commands.xml_validate.prepare_input import _deserialise_resptr_prop
from dsp_tools.commands.xml_validate.prepare_input import _deserialise_text_prop
from dsp_tools.commands.xml_validate.prepare_input import _transform_into_project_deserialised


def test_transform_into_xml_deserialised(parsed_xml: etree._Element) -> None:
    result = _transform_into_project_deserialised(parsed_xml)
    assert result.shortcode == "9999"
    assert result.default_onto == "onto"
    assert len(result.resources) == 1
    resource = result.resources[0]
    assert resource.res_id == "class-id"
    assert resource.res_class == ":Class"
    assert resource.label == "Label"
    assert len(resource.values) == 3


def test_deserialise_list_prop(xml_list_prop: etree._Element) -> None:
    result = _deserialise_list_prop(xml_list_prop)
    assert len(result) == 1
    deserialised = result[0]
    assert isinstance(deserialised, ListValueData)
    assert deserialised.prop_name == ":listProp"
    assert deserialised.prop_value == "listNode"
    assert deserialised.list_name == "onlyList"


def test_deserialise_text_prop(xml_text_prop: etree._Element) -> None:
    result = _deserialise_text_prop(xml_text_prop)
    assert len(result) == 2
    sorted_res = sorted(result, key=lambda x: x.prop_value)
    one = sorted_res[0]
    assert isinstance(one, SimpleTextData)
    assert one.prop_name == ":hasSimpleText"
    assert one.prop_value == "text content"
    two = sorted_res[1]
    assert isinstance(two, SimpleTextData)
    assert two.prop_name == ":hasSimpleText"
    assert two.prop_value == "text content 2"


def test_deserialise_resptr_prop(xml_resptr_prop: etree._Element) -> None:
    result = _deserialise_resptr_prop(xml_resptr_prop)
    assert len(result) == 1
    deserialised = result[0]
    assert isinstance(deserialised, LinkValueData)
    assert deserialised.prop_name == ":linkProp"
    assert deserialised.prop_value == "link-id"


if __name__ == "__main__":
    pytest.main([__file__])