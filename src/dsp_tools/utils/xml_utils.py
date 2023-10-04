from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Union

from lxml import etree

from dsp_tools.models.exceptions import UserError
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
    """

    # remove comments and processing instructions (commented out properties break the XMLProperty constructor)

    match input_file:
        case str():
            tree = _parse_xml_file(input_file)
        case Path():
            tree = _parse_xml_file(input_file)
        case etree._ElementTree():
            tree = _remove_comments_from_element_tree(input_file)
        case _:
            message = (
                f"The input '{input_file}' is not valid. This function expects either a element tree or a filepath."
            )
            logger.error(msg=message, exc_info=True)
            raise UserError(message)

    _remove_qnames_and_transform_special_tags(tree)

    return tree.getroot()


def _remove_qnames_and_transform_special_tags(
    input_tree: etree._ElementTree[etree._Element],
) -> etree._ElementTree[etree._Element]:
    """
    This function removes namespace URI from the elements name
    And transform the special tags to their technically correct form

    Args:
        input_tree: unclean tree

    Returns:
        cleaned tree
    """
    for elem in input_tree.iter():
        elem.tag = etree.QName(elem).localname  # remove namespace URI in the element's name
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


def _remove_comments_from_element_tree(
    input_tree: etree._ElementTree[etree._Element],
) -> etree._ElementTree[etree._Element]:
    """
    This function comments and processing instructions
    Commented out properties break the XMLProperty constructor

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
    """
    parser = etree.XMLParser(remove_comments=True, remove_pis=True)
    return etree.parse(source=input_file, parser=parser)
