from pathlib import Path

from dsp_tools.commands.xml_validate.models.data_deserialised import DataDeserialised
from dsp_tools.commands.xml_validate.reformat_input import transform_into_project_deserialised
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file
from dsp_tools.utils.xml_validation import validate_xml


def _deserialise_file(file: Path) -> DataDeserialised:
    """Returns an object which follows the structure of the XML closely"""
    root = parse_and_clean_xml_file(file)
    validate_xml(root)
    return transform_into_project_deserialised(root)
