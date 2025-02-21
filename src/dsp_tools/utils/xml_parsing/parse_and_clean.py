from __future__ import annotations

import copy
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


def make_localnames_and_remove_comments(data_xml: etree._Element) -> etree._Element:
    """
    This function removes all the namespaces from the XML tags, comments, and processing instructions.
    This type of cleaning is a prerequisite for many other functions dealing with the tree.
    """
    xml_no_namespace = copy.deepcopy(data_xml)
    for elem in xml_no_namespace.iter():
        if not isinstance(elem, (etree._Comment, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname
    return xml_no_namespace
