from __future__ import annotations

import importlib.resources

from loguru import logger
from lxml import etree

from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_and_transform_file import remove_namespaces_from_xml

separator = "\n    "
list_separator = "\n    - "
medium_separator = "\n----------------------------\n"
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
    xml_no_namespace = remove_namespaces_from_xml(xml)
    problems = _validate_xml_against_schema(xml_no_namespace)
    if problems:
        logger.opt(exception=True).error(problems)
        raise InputError(problems)
    return True


def _validate_xml_against_schema(data_xml: etree._Element) -> str | None:
    schema_res = importlib.resources.files("dsp_tools").joinpath("resources/schema/data.xsd")
    with schema_res.open(encoding="utf-8") as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    if not xmlschema.validate(data_xml):
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = f"{error_msg}{separator}Line {error.line}: {error.message}"
        return error_msg.replace("{https://dasch.swiss/schema}", "")
    return None
