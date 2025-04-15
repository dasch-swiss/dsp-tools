from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.xml_schema_validation import validate_xml_with_schema


def parse_and_clean_xml_file(input_file: Path) -> etree._Element:
    root = _parse_xml_file(input_file)
    root = remove_comments_from_element_tree(root)
    validate_xml_with_schema(root)
    print("The XML file is syntactically correct.")
    return transform_into_localnames(root)


def parse_and_validate_xml_file(input_file: Path | str) -> bool:
    root = _parse_xml_file(input_file)
    data_xml = remove_comments_from_element_tree(root)
    return validate_xml_with_schema(data_xml)


def _parse_xml_file(input_file: str | Path) -> etree._Element:
    parser = etree.XMLParser(remove_comments=True, remove_pis=True)
    try:
        return etree.parse(source=input_file, parser=parser).getroot()
    except etree.XMLSyntaxError as err:
        logger.error(f"The XML file contains the following syntax error: {err.msg}")
        raise InputError(f"The XML file contains the following syntax error: {err.msg}") from None


def transform_into_localnames(root: etree._Element) -> etree._Element:
    """Removes the namespace of the tags."""
    tree = deepcopy(root)
    for elem in tree.iter():
        elem.tag = etree.QName(elem).localname
    return tree


def remove_comments_from_element_tree(input_tree: etree._Element) -> etree._Element:
    """Removes comments and processing instructions."""
    root = deepcopy(input_tree)
    for c in root.xpath("//comment()"):
        c.getparent().remove(c)
    for c in root.xpath("//processing-instruction()"):
        c.getparent().remove(c)
    return root
