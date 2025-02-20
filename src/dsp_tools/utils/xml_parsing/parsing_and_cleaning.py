from __future__ import annotations

from pathlib import Path

from lxml import etree

from dsp_tools.utils.xml_parsing.models.data_deserialised import XMLProject
from dsp_tools.utils.xml_parsing.parse_and_clean import _parse_xml_file
from dsp_tools.utils.xml_parsing.parse_and_transform_file import remove_comments_from_element_tree
from dsp_tools.utils.xml_parsing.parse_and_transform_file import transform_special_tags_make_localname
from dsp_tools.utils.xml_parsing.schema_validation import validate_xml_with_schema
from dsp_tools.utils.xml_parsing.transformations import resolve_prefixes_for_properties_and_resources


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
    root = _parse_xml_file(input_file)
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
    root = _parse_xml_file(input_file)
    root = remove_comments_from_element_tree(root)
    return transform_special_tags_make_localname(root)


def get_xml_project(file: Path, api_url: str) -> XMLProject:
    """
    Parses, cleans and does some basic transformaton of the file and creates the XMLProject.

    Args:
        file: file path
        api_url: API URL to resolve prefixes into namespaces

    Returns:
        Project Information and cleaned root
    """
    root = _parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml_with_schema(root)
    root = transform_special_tags_make_localname(root)
    return resolve_prefixes_for_properties_and_resources(root, api_url)
