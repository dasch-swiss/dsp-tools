from __future__ import annotations

import copy
from copy import deepcopy
from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.models.exceptions import InputError


def parse_and_clean_xml_file(input_file: Path) -> etree._Element:
    """
    Parse an XML file with DSP-conform data,
    remove namespace URI from the elements' names,
    and transform the special tags `<annotation>`, `<region>`, `<link>`, `<video-segment>`, `<audio-segment>`
    to their technically correct form
    `<resource restype="Annotation">`, `<resource restype="Region">`, `<resource restype="LinkObj">`,
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
    and transforms the special tags `<annotation>`, `<region>`, `<link>`, `<video-segment>`, `<audio-segment>`
    to their technically correct form
    `<resource restype="Annotation">`, `<resource restype="Region">`, `<resource restype="LinkObj">`,
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
        if elem.tag == "annotation":
            elem.attrib["restype"] = "Annotation"
            elem.tag = "resource"
        elif elem.tag == "link":
            elem.attrib["restype"] = "LinkObj"
            elem.tag = "resource"
        elif elem.tag == "region":
            elem.attrib["restype"] = "Region"
            elem.tag = "resource"
        elif elem.tag == "video-segment":
            elem.attrib["restype"] = "VideoSegment"
            elem.tag = "resource"
        elif elem.tag == "audio-segment":
            elem.attrib["restype"] = "AudioSegment"
            elem.tag = "resource"
    return tree


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
