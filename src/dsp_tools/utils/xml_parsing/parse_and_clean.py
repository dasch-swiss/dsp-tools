from __future__ import annotations

import copy
from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.models.exceptions import InputError


def parse_and_basic_cleaning(input_file: str | Path) -> etree._Element:
    """
    This function removes all the processing instructions and comments.
    From the tags that remain, the namespace is removed, leaving the localname.
    """
    tree = _parse_xml_file(input_file)
    return _remove_namespaces_and_comments_from_tree(tree)


def _parse_xml_file(input_file: str | Path) -> etree._Element:
    parser = etree.XMLParser(remove_comments=True, remove_pis=True)
    try:
        return etree.parse(source=input_file, parser=parser).getroot()
    except etree.XMLSyntaxError as err:
        logger.opt(exception=True).error(f"The XML file contains the following syntax error: {err.msg}")
        raise InputError(f"The XML file contains the following syntax error: {err.msg}") from None


def _remove_namespaces_and_comments_from_tree(data_xml: etree._Element) -> etree._Element:
    xml_no_namespace = copy.deepcopy(data_xml)
    for elem in xml_no_namespace.iter():
        if not isinstance(elem, (etree._Comment, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname
    return xml_no_namespace
