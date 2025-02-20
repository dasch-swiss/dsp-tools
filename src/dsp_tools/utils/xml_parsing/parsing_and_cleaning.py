from __future__ import annotations

from pathlib import Path

from dsp_tools.utils.xml_parsing.parse_and_clean import _parse_xml_file
from dsp_tools.utils.xml_parsing.parse_and_transform_file import remove_comments_from_element_tree
from dsp_tools.utils.xml_parsing.schema_validation import validate_xml_with_schema


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
