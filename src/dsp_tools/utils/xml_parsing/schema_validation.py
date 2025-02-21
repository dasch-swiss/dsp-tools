from loguru import logger
from lxml import etree

from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import find_mixed_encodings_in_text_tags
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_and_clean import remove_namespaces_and_comments_from_tree
from dsp_tools.utils.xml_parsing.validations import validate_xml_against_schema_raising

separator = "\n    "
grand_separator = "\n\n---------------------------------------\n\n"


def validate_xml_with_schema(xml: etree._Element) -> bool:
    """
    Validates an XML element tree against the DSP XSD schema.

    Args:
        xml: the XML element tree to be validated

    Raises:
        InputError: if the XML file is invalid

    Returns:
        True if the XML file is valid
    """
    xml_no_namespace = remove_namespaces_and_comments_from_tree(xml)

    problems = []

    problems.extend(validate_xml_against_schema_raising(xml))
    problems.extend(find_mixed_encodings_in_text_tags(xml_no_namespace))

    if problems:
        err_msg = grand_separator.join(problems)
        logger.opt(exception=True).error(err_msg)
        raise InputError(err_msg)

    return True
