from __future__ import annotations

from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_xml import parse_xml_file
from dsp_tools.utils.xml_parsing.transform import remove_comments_from_element_tree
from dsp_tools.utils.xml_parsing.transform import transform_into_localnames
from dsp_tools.utils.xml_parsing.transform import transform_special_tags_make_localname
from dsp_tools.utils.xml_parsing.xml_schema_validation import validate_xml_against_schema


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


def get_root_for_deserialisation(input_file: Path) -> etree._Element:
    root = parse_xml_file(input_file)
    root = remove_comments_from_element_tree(root)
    problem_msg = validate_xml_against_schema(root)
    if problem_msg:
        logger.error(problem_msg)
        raise InputError(problem_msg)
    print("The XML file is syntactically correct.")
    return transform_into_localnames(root)
