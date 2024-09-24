from typing import Callable
from typing import Sequence

from lxml import etree

from dsp_tools.commands.xml_validate.models.data_deserialised import AbstractResource
from dsp_tools.commands.xml_validate.models.data_deserialised import AnnotationDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import AudioSegmentDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import LinkObjDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ProjectDataDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import RegionDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import UriValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import VideoSegmentDeserialised


def deserialise_xml(root: etree._Element) -> ProjectDataDeserialised:
    """
    Takes the root of an XML
    Extracts the data of the project and transforms all its resources.

    Args:
        root: root of an xml with qnames and comments removed

    Returns:
        Class instance with the information reformatted
    """
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    resources = _deserialise_all_resources(root)
    return ProjectDataDeserialised(shortcode=shortcode, default_onto=default_ontology, resources=resources)


def _deserialise_all_resources(root: etree._Element) -> list[AbstractResource]:
    all_res: list[AbstractResource] = []
    for res in root.iterchildren():
        res_id = res.attrib["id"]
        match res.tag:
            case "resource":
                all_res.append(_deserialise_one_resource(res))
            case "annotation":
                all_res.append(AnnotationDeserialised(res_id))
            case "region":
                all_res.append(RegionDeserialised(res_id))
            case "link":
                all_res.append(LinkObjDeserialised(res_id))
            case "video-segment":
                all_res.append(VideoSegmentDeserialised(res_id))
            case "audio-segment":
                all_res.append(AudioSegmentDeserialised(res_id))
            case _:
                pass
    return all_res


def _deserialise_one_resource(resource: etree._Element) -> ResourceDeserialised:
    values: list[ValueDeserialised] = []
    for val in resource.iterchildren():
        values.extend(_deserialise_one_property(val))
    return ResourceDeserialised(
        res_id=resource.attrib["id"],
        res_class=resource.attrib["restype"],
        label=resource.attrib["label"],
        values=values,
    )


def _deserialise_one_property(prop_ele: etree._Element) -> Sequence[ValueDeserialised]:  # noqa: PLR0911 (too-many-branches, return statements)
    match prop_ele.tag:
        case "boolean-prop":
            return _deserialise_one_value(prop_ele, BooleanValueDeserialised)
        case "color-prop":
            return _deserialise_one_value(prop_ele, ColorValueDeserialised)
        case "date-prop":
            return _deserialise_one_value(prop_ele, DateValueDeserialised)
        case "decimal-prop":
            return _deserialise_one_value(prop_ele, DecimalValueDeserialised)
        case "geoname-prop":
            return _deserialise_one_value(prop_ele, GeonameValueDeserialised)
        case "list-prop":
            return _deserialise_list_prop(prop_ele)
        case "integer-prop":
            return _deserialise_one_value(prop_ele, IntValueDeserialised)
        case "resptr-prop":
            return _deserialise_one_value(prop_ele, LinkValueDeserialised)
        case "text-prop":
            return _deserialise_text_prop(prop_ele)
        case "time-prop":
            return _deserialise_one_value(prop_ele, TimeValueDeserialised)
        case "uri-prop":
            return _deserialise_one_value(prop_ele, UriValueDeserialised)
        case _:
            return []


def _deserialise_one_value(
    prop: etree._Element, func: Callable[[str, str | None], ValueDeserialised]
) -> Sequence[ValueDeserialised]:
    prop_name = prop.attrib["name"]
    return [func(prop_name, x.text) for x in prop.iterchildren()]


def _deserialise_list_prop(prop: etree._Element) -> list[ListValueDeserialised]:
    prop_name = prop.attrib["name"]
    list_name = prop.attrib["list"]
    return [ListValueDeserialised(prop_name, x.text, list_name) for x in prop.iterchildren()]


def _deserialise_text_prop(prop: etree._Element) -> list[SimpleTextDeserialised | RichtextDeserialised]:
    prop_name = prop.attrib["name"]
    all_vals: list[SimpleTextDeserialised | RichtextDeserialised] = []
    for val in prop.iterchildren():
        match val.attrib["encoding"]:
            case "utf8":
                all_vals.append(SimpleTextDeserialised(prop_name, val.text))
            case "xml":
                all_vals.append(RichtextDeserialised(prop_name, val.text))
    return all_vals
