from pathlib import Path
from typing import cast

from lxml import etree

from dsp_tools.commands.xml_validate.models.deserialised import LinkValueDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ListValueDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ResourceDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import RichtextDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import SimpleTextDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ValueDeserialised
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file
from dsp_tools.utils.xml_validation import validate_xml


def parse_file(file: Path) -> ProjectDeserialised:
    """Returns an object which follows the structure of the XML closely"""
    root = _parse_file_validate_with_schema(file)
    return _transform_into_project_deserialised(root)


def _parse_file_validate_with_schema(file: Path) -> etree._Element:
    root = parse_and_clean_xml_file(file)
    validate_xml(root)
    return root


def _transform_into_project_deserialised(root: etree._Element) -> ProjectDeserialised:
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    resources = [_deserialise_one_resource(x) for x in root.iterdescendants(tag="resource")]
    return ProjectDeserialised(shortcode=shortcode, default_onto=default_ontology, resources=resources)


def _deserialise_one_resource(resource: etree._Element) -> ResourceDeserialised:
    res_id = resource.attrib["id"]
    values: list[ValueDeserialised] = []
    for val in resource.iterchildren():
        values.extend(_deserialise_one_property(val))
    return ResourceDeserialised(
        res_id=res_id,
        res_class=resource.attrib["restype"],
        label=resource.attrib["label"],
        values=values,
    )


def _deserialise_one_property(prop_ele: etree._Element) -> list[ValueDeserialised]:
    match prop_ele.tag:
        case "text-prop":
            return _deserialise_text_prop(prop_ele)
        case "list-prop":
            return _deserialise_list_prop(prop_ele)
        case "resptr-prop":
            return _deserialise_resptr_prop(prop_ele)
        case _:
            return []


def _deserialise_text_prop(prop: etree._Element) -> list[ValueDeserialised]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueDeserialised] = []
    for child in prop.iterchildren():
        comments = child.attrib.get("comment")
        val = cast(str, child.text)
        match child.attrib["encoding"]:
            case "utf8":
                all_vals.append(SimpleTextDeserialised(prop_name=prop_name, prop_value=val, comments=comments))
            case "xml":
                all_vals.append(RichtextDeserialised(prop_name=prop_name, prop_value=val, comments=comments))
    return all_vals


def _deserialise_list_prop(prop: etree._Element) -> list[ValueDeserialised]:
    prop_name = prop.attrib["name"]
    list_name = prop.attrib["list"]
    all_vals: list[ValueDeserialised] = []
    for val in prop.iterchildren():
        txt = cast(str, val.text)
        all_vals.append(
            ListValueDeserialised(
                prop_name=prop_name,
                prop_value=txt,
                list_name=list_name,
                comments=val.attrib.get("comment"),
            )
        )
    return all_vals


def _deserialise_resptr_prop(prop: etree._Element) -> list[ValueDeserialised]:
    prop_name = prop.attrib["name"]
    all_links: list[ValueDeserialised] = []
    for val in prop.iterchildren():
        txt = cast(str, val.text)
        all_links.append(
            LinkValueDeserialised(
                prop_name=prop_name,
                prop_value=txt,
                comments=val.attrib.get("comment"),
            )
        )
    return all_links
