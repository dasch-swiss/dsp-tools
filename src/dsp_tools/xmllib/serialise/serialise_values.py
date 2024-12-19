from collections import defaultdict

from lxml import etree

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

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


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
    Richtext: "xml",
    SimpleText: "utf8",
}


def serialise_values(values: list[Value]) -> list[etree._Element]:
    """
    Serialise a list of values for a resource.

    Args:
        values: List of Values

    Returns:
        list of serialised values
    """
    prop_groups, type_lookup = _group_properties(values)
    serialised = []
    for prop_name, prop_values in prop_groups.items():
        prop_type = type_lookup[prop_name]
        match prop_type:
            case "list":
                serialised.append(_make_complete_list_prop(prop_values, prop_name))
            case "xml" | "utf8":
                serialised.append(_make_complete_text_prop(values, prop_name, prop_type))
            case _:
                serialised.append(_make_complete_generic_prop(values, prop_name, prop_type))
    return serialised


def _group_properties(values: list[Value]) -> tuple[dict[str, list[Value]], dict[str, str]]:
    grouped = defaultdict(list)
    name_type_lookup = {}
    for val in values:
        grouped[val.prop_name].append(val)
        name_type_lookup[val.prop_name] = PROP_TYPE_LOOKUP[type(val)]
    return grouped, name_type_lookup


def _make_complete_generic_prop(values: list[ListValue], prop_name: str, prop_type: str) -> etree._Element:
    prop = _make_generic_prop(prop_name, prop_type)
    for val in values:
        val_ele = _make_generic_element(val, prop_type)
        prop.append(val_ele)
    return prop


def _make_generic_prop(prop_name: str, prop_type: str) -> etree._Element:
    return etree.Element(f"{DASCH_SCHEMA}{prop_type}-prop", name=prop_name, nsmap=XML_NAMESPACE_MAP)


def _make_complete_list_prop(values: list[ListValue], prop_name: str) -> etree._Element:
    list_name = next(iter(values)).list_name
    prop = etree.Element(f"{DASCH_SCHEMA}list-prop", name=prop_name, list=list_name, nsmap=XML_NAMESPACE_MAP)
    for val in values:
        prop.append(_make_generic_element(val, "list"))
    return prop


def _make_complete_text_prop(values: list[Richtext | SimpleText], prop_name: str, text_encoding: str) -> etree._Element:
    prop = _make_generic_prop(prop_name, "text")
    for val in values:
        val_ele = _make_generic_element(val, "text")
        val_ele.attrib["encoding"] = text_encoding
        prop.append(val_ele)
    return prop


def _make_generic_element(value: Value, prop_type: str) -> etree._Element:
    attribs = {}
    if value.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
        attribs["permissions"] = value.permissions.value
    if value.comment is not None:
        attribs["comment"] = str(value.comment)
    ele = etree.Element(f"{DASCH_SCHEMA}{prop_type}", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
    ele.text = str(value.value)
    return ele
