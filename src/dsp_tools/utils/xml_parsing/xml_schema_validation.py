from __future__ import annotations

import importlib.resources
import warnings
from pathlib import Path

import regex
from loguru import logger
from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_xml import parse_xml_file
from dsp_tools.utils.xml_parsing.transform import remove_comments_from_element_tree
from dsp_tools.utils.xml_parsing.transform import transform_into_localnames

separator = "\n    "
list_separator = "\n    - "


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
    cleaned = transform_into_localnames(xml)
    cleaned = remove_comments_from_element_tree(cleaned)
    _warn_user_about_tags_in_simpletext(cleaned)
    problem_msg = _validate_xml_against_schema(xml)

    if problem_msg:
        logger.error(problem_msg)
        raise InputError(problem_msg)

    return True


def _validate_xml_against_schema(data_xml: etree._Element) -> str | None:
    schema_res = importlib.resources.files("dsp_tools").joinpath("resources/schema/data.xsd")
    with schema_res.open(encoding="utf-8") as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    if not xmlschema.validate(data_xml):
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = f"{error_msg}{separator}Line {error.line}: {error.message}"
        error_msg = error_msg.replace("{https://dasch.swiss/schema}", "")
        return error_msg
    return None


def _warn_user_about_tags_in_simpletext(xml_no_namespace: etree._Element) -> None:
    """
    Checks if there are angular brackets in simple text.
    It is possible that the user mistakenly added XML tags into a simple text field.
    But it is also possible that an angular bracket should be displayed.
    So that the user does not insert XML tags mistakenly into simple text fields,
    the user is warned, if there is any present.
    """
    resources_with_potential_xml_tags = []
    for text in xml_no_namespace.findall(path="resource/text-prop/text"):
        regex_finds_tags = bool(regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(text.text)))
        etree_finds_tags = bool(list(text.iterchildren()))
        has_tags = regex_finds_tags or etree_finds_tags
        if text.attrib["encoding"] == "utf8" and has_tags:
            sourceline = f"line {text.sourceline}: " if text.sourceline else " "
            propname = text.getparent().attrib["name"]  # type: ignore[union-attr]
            resname = text.getparent().getparent().attrib["id"]  # type: ignore[union-attr]
            resources_with_potential_xml_tags.append(f"{sourceline}resource '{resname}', property '{propname}'")
    if resources_with_potential_xml_tags:
        err_msg = (
            "Angular brackets in the format of <text> were found in text properties with encoding=utf8.\n"
            "Please note that these will not be recognised as formatting in the text field, "
            "but will be displayed as-is.\n"
            f"The following resources of your XML file contain angular brackets:{list_separator}"
            f"{list_separator.join(resources_with_potential_xml_tags)}"
        )
        warnings.warn(DspToolsUserWarning(err_msg))


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
