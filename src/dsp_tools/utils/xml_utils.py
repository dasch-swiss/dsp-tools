from __future__ import annotations

import copy
from pathlib import Path
from typing import Any
from typing import Union

from lxml import etree

from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def parse_and_clean_xml_file(input_file: Union[str, Path, etree._ElementTree[Any]]) -> etree._Element:
    """
    Parse an XML file with DSP-conform data,
    remove namespace URI from the elements' names,
    and transform the special tags <annotation>, <region>, and <link>
    to their technically correct form
    <resource restype="Annotation">, <resource restype="Region">, and <resource restype="LinkObj">.

    Args:
        input_file: path to the XML file, or parsed ElementTree

    Returns:
        the root element of the parsed XML file

    Raises:
        InputError: if the input is not of either the expected types
    """

    tree = parse_and_remove_comments_from_xml_file(input_file)
    return _remove_qnames_and_transform_special_tags(tree)


def parse_and_remove_comments_from_xml_file(
    input_file: Union[str, Path, etree._ElementTree[Any]],
) -> etree._Element:
    """
    Parse an XML file with DSP-conform data,
    and remove the comments and processing instructions
    (commented out properties break the XMLProperty constructor)

    Args:
        input_file: path to the XML file, or parsed ElementTree

    Returns:
        the root element of the parsed XML file

    Raises:
        InputError: if the input is not of either the expected types
    """

    if isinstance(input_file, (str, Path)):
        tree = _parse_xml_file(input_file)
    else:
        tree = input_file
    tree = remove_comments_from_element_tree(tree)

    return tree.getroot()


def _remove_qnames_and_transform_special_tags(
    input_tree: etree._Element,
) -> etree._Element:
    """
    This function removes the namespace URIs from the elements' names
    and transforms the special tags <annotation>, <region>, and <link>
    to their technically correct form
    <resource restype="Annotation">, <resource restype="Region">, and <resource restype="LinkObj">.

    Args:
        input_tree: unclean tree

    Returns:
        cleaned tree
    """
    for elem in input_tree.iter():
        elem.tag = etree.QName(elem).localname
        if elem.tag == "annotation":
            elem.attrib["restype"] = "Annotation"
            elem.tag = "resource"
        elif elem.tag == "link":
            elem.attrib["restype"] = "LinkObj"
            elem.tag = "resource"
        elif elem.tag == "region":
            elem.attrib["restype"] = "Region"
            elem.tag = "resource"
    return input_tree


def remove_comments_from_element_tree(
    input_tree: etree._ElementTree[etree._Element],
) -> etree._ElementTree[etree._Element]:
    """
    This function removes comments and processing instructions.
    Commented out properties break the XMLProperty constructor.

    Args:
        input_tree: etree that will be cleaned

    Returns:
        clean etree
    """
    tree = copy.deepcopy(input_tree)
    for c in tree.xpath("//comment()"):
        c.getparent().remove(c)
    for c in tree.xpath("//processing-instruction()"):
        c.getparent().remove(c)
    return tree


def _parse_xml_file(input_file: Union[str, Path]) -> etree._ElementTree[etree._Element]:
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
        return etree.parse(source=input_file, parser=parser)
    except etree.XMLSyntaxError as err:
        logger.error(f"The XML file contains the following syntax error: {err.msg}", exc_info=True)
        raise InputError(f"The XML file contains the following syntax error: {err.msg}") from None


def remove_namespaces_from_xml(
    data_xml: etree._Element,
) -> etree._Element:
    """
    This function removes all the namespaces from an XML file.

    Args:
        data_xml: file with namespaces

    Returns:
        the XMl file without the namespaces
    """
    xml_no_namespace = copy.deepcopy(data_xml)
    for elem in xml_no_namespace.iter():
        if not isinstance(elem, (etree._Comment, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname
    return xml_no_namespace
