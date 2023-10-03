from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Union

from lxml import etree


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


def parse_and_clean_xml_file(
    input_file: Union[str, Path, etree._ElementTree[etree._Element]],
) -> etree._Element:
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

    if isinstance(input_file, (str, Path)):
        tree = _parse_xml_file(input_file=input_file)
    else:
        tree = _remove_comments_from_element_tree(input_tree=input_file)

    tree = _remove_qnames_and_transform_special_tags(input_tree=tree)

    return tree.getroot()
