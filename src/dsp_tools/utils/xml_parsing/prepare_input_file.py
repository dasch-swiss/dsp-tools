from pathlib import Path

from lxml import etree

from dsp_tools.utils.xml_parsing.parse_and_clean import parse_and_basic_cleaning
from dsp_tools.utils.xml_parsing.schema_validation import validate_xml_with_schema
from dsp_tools.utils.xml_parsing.transformations import transform_special_resource_tags


def prepare_file_for_deserialisation(file: Path) -> etree._Element:
    """Reads, cleans, validates the file and transforms special tags."""
    tree = parse_and_basic_cleaning(file)
    validate_xml_with_schema(tree)
    return transform_special_resource_tags(tree)
