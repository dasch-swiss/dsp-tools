from __future__ import annotations

import importlib.resources

from loguru import logger
from lxml import etree

from dsp_tools.models.exceptions import BaseError


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
    if problems := _validate_xml_against_schema(xml):
        logger.opt(exception=True).error(problems)
        raise BaseError(problems)
    return True


def _validate_xml_against_schema(data_xml: etree._Element) -> str | None:
    schema_res = importlib.resources.files("dsp_tools").joinpath("resources/schema/data.xsd")
    with schema_res.open(encoding="utf-8") as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    if not xmlschema.validate(data_xml):
        messages = ["The XML file cannot be uploaded due to the following validation error(s):"]
        for error in xmlschema.error_log:
            messages.append(f"Line {error.line}: {error.message}")
        msg = "\n    ".join(messages)
        return msg.replace("{https://dasch.swiss/schema}", "")
    return None
