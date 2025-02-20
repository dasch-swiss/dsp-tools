from __future__ import annotations

from pathlib import Path

from lxml import etree

from dsp_tools.utils.xml_parsing.models.data_deserialised import XMLProject
from dsp_tools.utils.xml_parsing.parse_and_clean import parse_and_basic_cleaning
from dsp_tools.utils.xml_parsing.schema_validation import validate_xml_with_schema
from dsp_tools.utils.xml_parsing.transformations import resolve_prefixes_for_properties_and_resources
from dsp_tools.utils.xml_parsing.transformations import transform_special_resource_tags


def parse_clean_and_validate_xml(file: Path) -> etree._Element:
    """
    Parse an XML file with DSP-conform data,
    remove namespace URI from the elements' names,
    and transform the special tags `<region>`, `<link>`, `<video-segment>`, `<audio-segment>`
    to their technically correct form
    `<resource restype="Region">`, `<resource restype="LinkObj">`,
    `<resource restype="VideoSegment">`, `<resource restype="AudioSegment">`.
    """
    tree = parse_and_basic_cleaning(file)
    validate_xml_with_schema(tree)
    return transform_special_resource_tags(tree)


def parse_and_validate(file: Path) -> bool:
    """Parses and validates"""
    tree = parse_and_basic_cleaning(file)
    return validate_xml_with_schema(tree)


def get_xml_project(file: Path, api_url: str) -> XMLProject:
    """Parses, cleans and does some basic transformation of the file and creates the XMLProject."""
    root = parse_clean_and_validate_xml(file)
    return resolve_prefixes_for_properties_and_resources(root, api_url)
