from typing import Callable
from typing import Sequence
from typing import cast

from lxml import etree

from dsp_tools.commands.validate_data.constants import AUDIO_SEGMENT_RESOURCE
from dsp_tools.commands.validate_data.constants import REGION_RESOURCE
from dsp_tools.commands.validate_data.constants import VIDEO_SEGMENT_RESOURCE
from dsp_tools.commands.validate_data.models.data_deserialised import AbstractFileValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BitstreamDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DataDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IIIFUriDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ProjectDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ProjectInformation
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import UriValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ValueDeserialised


def deserialise_xml(root: etree._Element) -> ProjectDeserialised:
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
    project_info = ProjectInformation(shortcode, default_ontology)
    data_deserialised = _deserialise_all_resources(root)
    return ProjectDeserialised(project_info, data_deserialised)


def _deserialise_all_resources(root: etree._Element) -> DataDeserialised:
    all_res: list[ResourceDeserialised] = []
    for res in root.iterdescendants(tag="resource"):
        res_id = res.attrib["id"]
        lbl = cast(str, res.attrib.get("label"))
        dsp_type = None
        res_type = res.attrib["restype"]
        if res_type == REGION_RESOURCE:
            dsp_type = REGION_RESOURCE
        elif res_type == VIDEO_SEGMENT_RESOURCE:
            dsp_type = VIDEO_SEGMENT_RESOURCE
        elif res_type == AUDIO_SEGMENT_RESOURCE:
            dsp_type = AUDIO_SEGMENT_RESOURCE
        if dsp_type:
            all_res.append(ResourceDeserialised(res_id, lbl, dsp_type, []))
        else:
            all_res.append(_deserialise_one_resource(res))
    file_values = _deserialise_file_value(root)
    return DataDeserialised(all_res, file_values)


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
                all_vals.append(SimpleTextDeserialised(prop_name, _get_text_as_string(val)))
            case "xml":
                all_vals.append(RichtextDeserialised(prop_name, _get_text_as_string(val)))
    return all_vals


def _get_text_as_string(value: etree._Element) -> str | None:
    if len(value):
        text_list = []
        if found := value.text:
            text_list = [found]
        text_list.extend([etree.tostring(child, encoding="unicode", method="xml") for child in value])
        return "".join(text_list).strip()
    else:
        return value.text


def _deserialise_file_value(root: etree._Element) -> list[AbstractFileValueDeserialised]:
    file_values: list[AbstractFileValueDeserialised] = []
    for res in root.iterchildren(tag="resource"):
        res_id = res.attrib["id"]
        if (bitstream := res.find("bitstream")) is not None:
            file_values.append(BitstreamDeserialised(res_id, bitstream.text))
        elif (iiif_uri := res.find("iiif-uri")) is not None:
            file_values.append(IIIFUriDeserialised(res_id, iiif_uri.text))
    return file_values
