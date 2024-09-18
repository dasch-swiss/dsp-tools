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


def _deserialise_one_property(prop_ele: etree._Element) -> list[ValueData]:  # noqa: PLR0911 (too-many-branches, return statements)
    match prop_ele.tag:
        case "boolean-prop":
            return _deserialise_boolean_prop(prop_ele)
        case "color-prop":
            return _deserialise_color_prop(prop_ele)
        case "date-prop":
            return _deserialise_date_prop(prop_ele)
        case "decimal-prop":
            return _deserialise_decimal_prop(prop_ele)
        case "geoname-prop":
            return _deserialise_geoname_prop(prop_ele)
        case "list-prop":
            return _deserialise_list_prop(prop_ele)
        case "integer-prop":
            return _deserialise_int_prop(prop_ele)
        case "resptr-prop":
            return _deserialise_resptr_prop(prop_ele)
        case "text-prop":
            return _deserialise_text_prop(prop_ele)
        case "time-prop":
            return _deserialise_time_prop(prop_ele)
        case "uri-prop":
            return _deserialise_uri_prop(prop_ele)
        case _:
            return []


def _deserialise_boolean_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(BooleanValueData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_color_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(ColorValueData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_date_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(DateValueData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_decimal_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(DecimalValueData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_geoname_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(GeonameValueData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_list_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    list_name = prop.attrib["list"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(ListValueData(prop_name=prop_name, prop_value=txt, list_name=list_name))
    return all_vals


def _deserialise_int_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(IntValueData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_resptr_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(LinkValueData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_text_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        match val.attrib["encoding"]:
            case "utf8":
                all_vals.append(SimpleTextData(prop_name=prop_name, prop_value=txt))
            case "xml":
                all_vals.append(RichtextData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_time_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(TimeValueData(prop_name=prop_name, prop_value=txt))
    return all_vals


def _deserialise_uri_prop(prop: etree._Element) -> list[ValueData]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueData] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(UriValueData(prop_name=prop_name, prop_value=txt))
    return all_vals
