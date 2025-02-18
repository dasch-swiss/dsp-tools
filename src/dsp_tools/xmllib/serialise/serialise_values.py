from collections import defaultdict
from copy import deepcopy
from typing import cast

from lxml import etree
from namedentities.core import numeric_entities  # type: ignore[import-untyped]

from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.constants import DASCH_SCHEMA
from dsp_tools.xmllib.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.helpers import escape_reserved_xml_characters
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.values import BooleanValue
from dsp_tools.xmllib.models.values import ColorValue
from dsp_tools.xmllib.models.values import DateValue
from dsp_tools.xmllib.models.values import DecimalValue
from dsp_tools.xmllib.models.values import GeonameValue
from dsp_tools.xmllib.models.values import IntValue
from dsp_tools.xmllib.models.values import LinkValue
from dsp_tools.xmllib.models.values import ListValue
from dsp_tools.xmllib.models.values import Richtext
from dsp_tools.xmllib.models.values import SimpleText
from dsp_tools.xmllib.models.values import TimeValue
from dsp_tools.xmllib.models.values import UriValue
from dsp_tools.xmllib.models.values import Value

PROP_TYPE_LOOKUP = {
    BooleanValue: "boolean",
    ColorValue: "color",
    DateValue: "date",
    DecimalValue: "decimal",
    GeonameValue: "geoname",
    IntValue: "integer",
    LinkValue: "resptr",
    ListValue: "list",
    TimeValue: "time",
    UriValue: "uri",
    Richtext: "richtext",
    SimpleText: "simpletext",
}


def serialise_values(all_values: list[Value]) -> list[etree._Element]:
    """
    Serialise a list of values for a resource.

    Args:
        all_values: List of Values

    Returns:
        list of serialised values
    """
    prop_groups, type_lookup = _group_properties(all_values)
    serialised = []
    for prop_name, prop_values in prop_groups.items():
        prop_type = type_lookup[prop_name]
        match prop_type:
            case "list":
                serialised.append(_serialise_complete_list_prop(cast(list[ListValue], prop_values), prop_name))
            case "simpletext":
                serialised.append(_serialise_complete_simple_text_prop(cast(list[SimpleText], prop_values), prop_name))
            case "richtext":
                serialised.append(_serialise_complete_richtext_prop(cast(list[Richtext], prop_values), prop_name))
            case _:
                serialised.append(_serialise_complete_generic_prop(prop_values, prop_name, prop_type))
    return serialised


def _group_properties(values: list[Value]) -> tuple[dict[str, list[Value]], dict[str, str]]:
    grouped = defaultdict(list)
    name_type_lookup = {}
    for val in values:
        grouped[val.prop_name].append(val)
        name_type_lookup[val.prop_name] = PROP_TYPE_LOOKUP[type(val)]
    return grouped, name_type_lookup


def _serialise_complete_generic_prop(values: list[Value], prop_name: str, prop_type: str) -> etree._Element:
    prop = _serialise_generic_prop(prop_name, prop_type)
    for val in values:
        val_ele = _serialise_generic_element(val, prop_type)
        prop.append(val_ele)
    return prop


def _serialise_generic_prop(prop_name: str, prop_type: str) -> etree._Element:
    return etree.Element(f"{DASCH_SCHEMA}{prop_type}-prop", name=prop_name, nsmap=XML_NAMESPACE_MAP)


def _serialise_generic_element(value: Value, prop_type: str) -> etree._Element:
    attribs = {}
    if value.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
        attribs["permissions"] = value.permissions.value
    if value.comment is not None:
        attribs["comment"] = str(value.comment)
    ele = etree.Element(f"{DASCH_SCHEMA}{prop_type}", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
    ele.text = str(value.value)
    return ele


def _serialise_complete_list_prop(values: list[ListValue], prop_name: str) -> etree._Element:
    list_name = next(iter(values)).list_name
    prop = etree.Element(f"{DASCH_SCHEMA}list-prop", name=prop_name, list=list_name, nsmap=XML_NAMESPACE_MAP)
    for val in values:
        prop.append(_serialise_generic_element(val, "list"))
    return prop


def _serialise_complete_simple_text_prop(values: list[SimpleText], prop_name: str) -> etree._Element:
    prop = _serialise_generic_prop(prop_name, "text")
    for val in values:
        val_ele = _serialise_generic_element(val, "text")
        val_ele.attrib["encoding"] = "utf8"
        prop.append(val_ele)
    return prop


def _serialise_complete_richtext_prop(values: list[Richtext], prop_name: str) -> etree._Element:
    prop = _serialise_generic_prop(prop_name, "text")
    for val in values:
        val_ele = _serialise_generic_element(val, "text")  # produces wrong text content
        val_ele.attrib["encoding"] = "xml"
        prop.append(_create_richtext_elements_from_string(val, val_ele))  # overwrite the wrong text content
    return prop


def _create_richtext_elements_from_string(value: Richtext, text_element: etree._Element) -> etree._Element:
    new_element = deepcopy(text_element)
    escaped_text = escape_reserved_xml_characters(value.value)
    # transform named entities (=character references) to numeric entities, e.g. &nbsp; -> &#160;
    num_ent = numeric_entities(escaped_text)
    pseudo_xml = f"<ignore-this>{num_ent}</ignore-this>"
    try:
        parsed = etree.fromstring(pseudo_xml)
    except etree.XMLSyntaxError as err:
        msg = (
            f"The resource with the ID '{value.resource_id}' and the property '{value.prop_name}' "
            f"contains richtext which is not in correct XML syntax."
        )
        msg += f"\nOriginal error message: {err.msg}"
        msg += f"\nPotential line/column numbers are relative to this text: {pseudo_xml}"
        raise InputError(msg) from None
    new_element.text = parsed.text  # everything before the first child tag
    new_element.extend(list(parsed))  # all (nested) children of the pseudo-xml
    return new_element
