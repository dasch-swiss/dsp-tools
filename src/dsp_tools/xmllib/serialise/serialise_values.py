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
    TimeValue: "time",
    UriValue: "uri",
}


def _group_properties(values: list[Value]) -> dict[str, list[Value]]:
    grouped = defaultdict(list)
    for val in values:
        grouped[val.prop_name].append(val)
    return grouped


def _make_generic_prop(prop_name: str, prop_type: str) -> etree._Element:
    return etree.Element(f"{DASCH_SCHEMA}{prop_type}-prop", name=prop_name, nsmap=XML_NAMESPACE_MAP)


def _make_list_prop(values: list[ListValue], prop_name: str) -> etree._Element:
    list_name = next(iter(values)).list_name
    prop = etree.Element(f"{DASCH_SCHEMA}list-prop", name=prop_name, list=list_name, nsmap=XML_NAMESPACE_MAP)
    for val in values:
        prop.append(_make_generic_element(val, "list"))
    return prop


def _make_text_prop(values: list[Richtext | SimpleText], prop_name: str, text_encoding: str) -> etree._Element:
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
