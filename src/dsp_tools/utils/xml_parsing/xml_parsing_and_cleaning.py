from __future__ import annotations

import copy
from copy import deepcopy
from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.commands.validate_data.constants import KNORA_API_STR
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_parsing.models.data_deserialised import XMLProject
from dsp_tools.utils.xml_parsing.xml_schema_validation import validate_xml_with_schema


def parse_and_clean_xml_file(input_file: Path) -> etree._Element:
    """
    Parse an XML file with DSP-conform data,
    remove namespace URI from the elements' names,
    and transform the special tags `<region>`, `<link>`, `<video-segment>`, `<audio-segment>`
    to their technically correct form
    `<resource restype="Region">`, `<resource restype="LinkObj">`,
    `<resource restype="VideoSegment">`, `<resource restype="AudioSegment">`.

    Args:
        input_file: path to the XML file

    Returns:
        the root element of the parsed XML file

    Raises:
        InputError: if the input is not of either the expected types
    """
    root = parse_xml_file(input_file)
    root = remove_comments_from_element_tree(root)
    return transform_special_tags_make_localname(root)


def transform_special_tags_make_localname(input_tree: etree._Element) -> etree._Element:
    """
    This function removes the namespace URIs from the elements' names
    and transforms the special tags `<region>`, `<link>`, `<video-segment>`, `<audio-segment>`
    to their technically correct form
    `<resource restype="Region">`, `<resource restype="LinkObj">`,
    `<resource restype="VideoSegment">`, `<resource restype="AudioSegment">`.

    Args:
        input_tree: unclean tree

    Returns:
        cleaned tree
    """
    tree = transform_into_localnames(input_tree)
    return _transform_special_tags(tree)


def _transform_special_tags(tree: etree._Element) -> etree._Element:
    tree = deepcopy(tree)
    for elem in tree.iter():
        if elem.tag == "link":
            elem.attrib["restype"] = "LinkObj"
            elem.tag = "resource"
        elif elem.tag == "region":
            elem.attrib["restype"] = "Region"
            elem.tag = "resource"
        elif elem.tag == "video-segment":
            elem.attrib["restype"] = "VideoSegment"
            _correct_is_segment_of_property(elem, "VideoSegment")
            elem.tag = "resource"
        elif elem.tag == "audio-segment":
            elem.attrib["restype"] = "AudioSegment"
            _correct_is_segment_of_property(elem, "AudioSegment")
            elem.tag = "resource"
    return tree


def _correct_is_segment_of_property(segment: etree._Element, restype: str) -> None:
    for child in segment.iterchildren():
        if child.tag == "isSegmentOf":
            child.tag = f"is{restype}Of"
            break


def transform_into_localnames(root: etree._Element) -> etree._Element:
    """
    This function removes the namespace URIs from the elements' names

    Args:
        root: unclean tree

    Returns:
        cleaned tree
    """
    tree = deepcopy(root)
    for elem in tree.iter():
        elem.tag = etree.QName(elem).localname
    return tree


def remove_comments_from_element_tree(input_tree: etree._Element) -> etree._Element:
    """
    This function removes comments and processing instructions.
    Commented out properties break the XMLProperty constructor.

    Args:
        input_tree: etree root that will be cleaned

    Returns:
        clean xml
    """
    root = copy.deepcopy(input_tree)
    for c in root.xpath("//comment()"):
        c.getparent().remove(c)
    for c in root.xpath("//processing-instruction()"):
        c.getparent().remove(c)
    return root


def parse_xml_file(input_file: str | Path) -> etree._Element:
    """
    This function parses an XML file and returns an Element Tree

    Args:
        input_file: path to the input file

    Returns:
        element tree

    Raises:
        InputError: if the file contains a syntax error
    """
    parser = etree.XMLParser(remove_comments=True, remove_pis=True)
    try:
        return etree.parse(source=input_file, parser=parser).getroot()
    except etree.XMLSyntaxError as err:
        logger.opt(exception=True).error(f"The XML file contains the following syntax error: {err.msg}")
        raise InputError(f"The XML file contains the following syntax error: {err.msg}") from None


def remove_namespaces_from_xml(data_xml: etree._Element) -> etree._Element:
    """
    This function removes all the namespaces from an XML element tree.

    Args:
        data_xml: xml with namespaces

    Returns:
        the XMl without the namespaces
    """
    xml_no_namespace = copy.deepcopy(data_xml)
    for elem in xml_no_namespace.iter():
        if not isinstance(elem, (etree._Comment, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname
    return xml_no_namespace


def get_xml_project(file: Path, api_url: str) -> XMLProject:
    """
    Parses, cleans and does some basic transformaton of the file and creates the XMLProject.

    Args:
        file: file path
        api_url: API URL to resolve prefixes into namespaces

    Returns:
        Project Information and cleaned root
    """
    root = parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml_with_schema(root)
    root = transform_special_tags_make_localname(root)
    return _replace_namespaces(root, api_url)


def _replace_namespaces(root: etree._Element, api_url: str) -> XMLProject:
    new_root = deepcopy(root)
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    namespace_lookup = _make_namespace_lookup(api_url, shortcode, default_ontology)
    for ele in new_root.iterdescendants():
        if (found := ele.attrib.get("restype")) or (found := ele.attrib.get("name")):
            split_found = found.split(":")
            if len(split_found) == 1:
                ele.set("restype" if "restype" in ele.attrib else "name", f"{KNORA_API_STR}{found}")
            elif len(split_found) == 2:
                if len(split_found[0]) == 0:
                    found_namespace = namespace_lookup[default_ontology]
                elif not (namespace := namespace_lookup.get(split_found[0])):
                    found_namespace = _construct_namespace(api_url, shortcode, split_found[0])
                    namespace_lookup[split_found[0]] = found_namespace
                else:
                    found_namespace = namespace
                ele.set("restype" if "restype" in ele.attrib else "name", f"{found_namespace}{split_found[1]}")
            else:
                raise InputError(
                    f"It is not permissible to have a colon in a property or resource class name. "
                    f"Please correct the following: {found}"
                )
    return XMLProject(
        shortcode=shortcode,
        root=new_root,
        used_ontologies=set(namespace_lookup.values()),
    )


def _make_namespace_lookup(api_url: str, shortcode: str, default_onto: str) -> dict[str, str]:
    return {default_onto: _construct_namespace(api_url, shortcode, default_onto), "knora-api": KNORA_API_STR}


def _construct_namespace(api_url: str, shortcode: str, onto_name: str) -> str:
    return f"{api_url}/ontology/{shortcode}/{onto_name}/v2#"
