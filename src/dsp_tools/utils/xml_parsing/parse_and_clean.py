from __future__ import annotations

import copy
from copy import deepcopy
from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.models.exceptions import InputError


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


def remove_namespaces_and_comments(data_xml: etree._Element) -> etree._Element:
    """
    This function removes all the namespaces from an XML element tree.

    Args:
        data_xml: xml with namespaces

    Returns:
        the XMl without the namespaces
    """
    xml_no_namespace = remove_comments_from_element_tree(data_xml)
    return _transform_into_localnames(xml_no_namespace)


def _transform_into_localnames(root: etree._Element) -> etree._Element:
    tree = deepcopy(root)
    for elem in tree.iter():
        elem.tag = etree.QName(elem).localname
    return tree


def remove_comments_from_element_tree(input_tree: etree._Element) -> etree._Element:
    """Removes comments and processing instructions."""
    root = copy.deepcopy(input_tree)
    for c in root.xpath("//comment()"):
        c.getparent().remove(c)
    for c in root.xpath("//processing-instruction()"):
        c.getparent().remove(c)
    return root
