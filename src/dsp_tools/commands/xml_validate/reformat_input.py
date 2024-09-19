from typing import Callable
from typing import Sequence

from lxml import etree

from dsp_tools.commands.xml_validate.models.data_deserialised import BooleanValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ColorValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import DataDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import DateValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import DecimalValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import GeonameValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import IntValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import LinkValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ListValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ResourceData
from dsp_tools.commands.xml_validate.models.data_deserialised import RichtextData
from dsp_tools.commands.xml_validate.models.data_deserialised import SimpleTextData
from dsp_tools.commands.xml_validate.models.data_deserialised import TimeValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import UriValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ValueData


def transform_into_project_deserialised(root: etree._Element) -> DataDeserialised:
    """
    Takes the root of an XML
    Extracts the metadata of the project and transforms all its resources.

    Args:
        root: root of an xml with qnames and comments removed

    Returns:
        Class instance with the information reformatted
    """
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    resources = _deserialise_all_resources(root)
    return DataDeserialised(shortcode=shortcode, default_onto=default_ontology, resources=resources)


def _deserialise_all_resources(root: etree._Element) -> list[ResourceData]:
    all_res = []
    for res in root.iterchildren():
        match res.tag:
            case "resource":
                all_res.append(_deserialise_one_resource(res))
            case "annotation" | "region" | "link" | "video-segment" | "audio-segment":
                all_res.append(_deserialise_dsp_base_resource(res))
            case _:
                pass
    return all_res


def _deserialise_dsp_base_resource(resource: etree._Element) -> ResourceData:
    return ResourceData(
        res_id=resource.attrib["id"],
        res_class=resource.attrib["restype"],
        label=resource.attrib["label"],
        values=[],
    )


def _deserialise_one_resource(resource: etree._Element) -> ResourceData:
    res_id = resource.attrib["id"]
    values: list[ValueData] = []
    for val in resource.iterchildren():
        values.extend(_deserialise_one_property(val))
    return ResourceData(
        res_id=res_id,
        res_class=resource.attrib["restype"],
        label=resource.attrib["label"],
        values=values,
    )


def _deserialise_one_property(prop_ele: etree._Element) -> Sequence[ValueData]:  # noqa: PLR0911 (too-many-branches, return statements)
    match prop_ele.tag:
        case "boolean-prop":
            return _deserialise_value(prop_ele, BooleanValueData)
        case "color-prop":
            return _deserialise_value(prop_ele, ColorValueData)
        case "date-prop":
            return _deserialise_value(prop_ele, DateValueData)
        case "decimal-prop":
            return _deserialise_value(prop_ele, DecimalValueData)
        case "geoname-prop":
            return _deserialise_value(prop_ele, GeonameValueData)
        case "list-prop":
            return _deserialise_list_prop(prop_ele)
        case "integer-prop":
            return _deserialise_value(prop_ele, IntValueData)
        case "resptr-prop":
            return _deserialise_value(prop_ele, LinkValueData)
        case "text-prop":
            return _deserialise_text_prop(prop_ele)
        case "time-prop":
            return _deserialise_value(prop_ele, TimeValueData)
        case "uri-prop":
            return _deserialise_value(prop_ele, UriValueData)
        case _:
            return []


def _deserialise_value(prop: etree._Element, func: Callable[[str, str], ValueData]) -> Sequence[ValueData]:
    prop_name = prop.attrib["name"]
    return [func(prop_name, val.text if val.text is not None else "") for val in prop.iterchildren()]


def _deserialise_list_prop(prop: etree._Element) -> Sequence[ListValueData]:
    prop_name = prop.attrib["name"]
    list_name = prop.attrib["list"]
    all_vals: list[ListValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(ListValueData(prop_name=prop_name, prop_value=txt, list_name=list_name))
    return all_vals


def _deserialise_text_prop(prop: etree._Element) -> Sequence[SimpleTextData | RichtextData]:
    prop_name = prop.attrib["name"]
    all_vals: list[SimpleTextData | RichtextData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        match val.attrib["encoding"]:
            case "utf8":
                all_vals.append(SimpleTextData(prop_name, txt))
            case "xml":
                all_vals.append(RichtextData(prop_name, txt))
    return all_vals
