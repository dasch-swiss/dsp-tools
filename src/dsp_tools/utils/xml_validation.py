from __future__ import annotations

import importlib.resources
from datetime import datetime
from pathlib import Path
from typing import Any, Union

import regex
from lxml import etree

from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xml_utils import parse_and_remove_comments_from_xml_file, remove_namespaces_from_xml

logger = get_logger(__name__)

separator = "\n    "
list_separator = "\n    - "
medium_separator = "\n----------------------------\n"
grand_separator = "\n\n---------------------------------------\n\n"


def validate_xml(input_file: Union[str, Path, etree._ElementTree[Any]]) -> bool:
    """
    Validates an XML file against the DSP XSD schema.

    Args:
        input_file: path to the XML file to be validated, or parsed ElementTree

    Raises:
        InputError: if the XML file is invalid

    Returns:
        True if the XML file is valid
    """
    data_xml, xmlschema = _parse_schema_and_data_files(input_file)

    problems = []

    all_good, msg = _validate_xml_against_schema(xmlschema, data_xml)
    if not all_good:
        problems.append(msg)

    xml_no_namespace = remove_namespaces_from_xml(data_xml)

    all_good, msg = _find_xml_tags_in_simple_text_elements(xml_no_namespace)
    if not all_good:
        problems.append(msg)

    if len(problems) > 0:
        err_msg = grand_separator.join(problems)
        logger.error(err_msg, exc_info=True)
        raise InputError(err_msg)

    logger.info("The XML file is syntactically correct and passed validation.")
    print(f"{datetime.now()}: The XML file is syntactically correct and passed validation.")
    return True


def _parse_schema_and_data_files(
    input_file: Union[str, Path, etree._ElementTree[Any]],
) -> tuple[Union[etree._ElementTree[etree._Element], etree._Element], etree.XMLSchema]:
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/data.xsd").open(
        encoding="utf-8"
    ) as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    data_xml = parse_and_remove_comments_from_xml_file(input_file)
    return data_xml, xmlschema


def _validate_xml_against_schema(
    xmlschema: etree.XMLSchema, data_xml: Union[etree._ElementTree[etree._Element], etree._Element]
) -> tuple[bool, str]:
    if not xmlschema.validate(data_xml):
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = error_msg + f"{separator}Line {error.line}: {error.message}"
        error_msg = error_msg.replace("{https://dasch.swiss/schema}", "")
        return False, error_msg
    return True, ""


def _find_xml_tags_in_simple_text_elements(
    xml_no_namespace: Union[etree._ElementTree[etree._Element], etree._Element],
) -> tuple[bool, str]:
    """
    Makes sure that there are no XML tags in simple texts.
    This can only be done with a regex,
    because even if the simple text contains some XML tags,
    the simple text itself is not valid XML that could be parsed.
    The extra challenge is that lxml transforms
    "pebble (&lt;2cm) and boulder (&gt;20cm)" into
    "pebble (<2cm) and boulder (>20cm)"
    (but only if &gt; follows &lt;).
    This forces us to write a regex that carefully distinguishes
    between a real tag (which is not allowed) and a false-positive-tag.

    Args:
        xml_no_namespace: parsed XML file with the namespaces removed

    Returns:
        True if there are no XML tags in the simple texts
    """
    resources_with_illegal_xml_tags = []
    for text in xml_no_namespace.findall(path="resource/text-prop/text"):
        regex_finds_tags = bool(regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(text.text)))
        etree_finds_tags = bool(list(text.iterchildren()))
        has_tags = regex_finds_tags or etree_finds_tags
        if text.attrib["encoding"] == "utf8" and has_tags:
            sourceline = f"line {text.sourceline}: " if text.sourceline else " "
            propname = text.getparent().attrib["name"]  # type: ignore[union-attr]
            resname = text.getparent().getparent().attrib["id"]  # type: ignore[union-attr]
            resources_with_illegal_xml_tags.append(f"{sourceline}resource '{resname}', property '{propname}'")
    if resources_with_illegal_xml_tags:
        err_msg = (
            "XML-tags are not allowed in text properties with encoding=utf8.\n"
            "The following resources of your XML file violate this rule:"
        )
        err_msg += list_separator + list_separator.join(resources_with_illegal_xml_tags)
        return False, err_msg
    return True, ""
