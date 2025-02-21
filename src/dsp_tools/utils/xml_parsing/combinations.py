from __future__ import annotations

from pathlib import Path

from lxml import etree

from dsp_tools.utils.xml_parsing.parse_and_clean import parse_xml_file
from dsp_tools.utils.xml_parsing.transform import transform_special_tags
from dsp_tools.utils.xml_parsing.xx_parse_and_transform_file import remove_comments_from_element_tree
from dsp_tools.utils.xml_parsing.xx_parse_and_transform_file import transform_into_localnames
from dsp_tools.utils.xml_parsing.xx_xml_schema_validation import validate_xml_with_schema


def parse_and_validate_xml_file(input_file: Path | str) -> bool:
    """
    Validates an XML file against the DSP XSD schema.

    Args:
        input_file: path to the XML file to be validated, or parsed ElementTree

    Raises:
        InputError: if the XML file is invalid

    Returns:
        True if the XML file is valid
    """
    root = parse_xml_file(input_file)
    data_xml = remove_comments_from_element_tree(root)
    return validate_xml_with_schema(data_xml)


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
    return transform_special_tags(tree)
