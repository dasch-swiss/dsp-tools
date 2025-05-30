from __future__ import annotations

import importlib.resources
from copy import deepcopy
from pathlib import Path

import regex
from loguru import logger
from lxml import etree

from dsp_tools.error.exceptions import InputError

separator = "\n    "
list_separator = "\n    - "


def parse_and_clean_xml_file(input_file: Path) -> etree._Element:
    root = _parse_xml_file(input_file)
    root = _remove_comments_from_element_tree(root)
    _validate_xml_with_schema(root)
    print("The XML file is syntactically correct.")
    return _transform_into_localnames(root)


def parse_and_validate_xml_file(input_file: Path | str) -> bool:
    root = _parse_xml_file(input_file)
    data_xml = _remove_comments_from_element_tree(root)
    return _validate_xml_with_schema(data_xml)


def _parse_xml_file(input_file: str | Path) -> etree._Element:
    parser = etree.XMLParser(remove_comments=True, remove_pis=True)
    try:
        return etree.parse(source=input_file, parser=parser).getroot()
    except etree.XMLSyntaxError as err:
        logger.error(f"The XML file contains the following syntax error: {err.msg}")
        raise InputError(f"The XML file contains the following syntax error: {err.msg}") from None


def _transform_into_localnames(root: etree._Element) -> etree._Element:
    """Removes the namespace of the tags."""
    tree = deepcopy(root)
    for elem in tree.iter():
        elem.tag = etree.QName(elem).localname
    return tree


def _remove_comments_from_element_tree(input_tree: etree._Element) -> etree._Element:
    """Removes comments and processing instructions."""
    root = deepcopy(input_tree)
    for c in root.xpath("//comment()"):
        c.getparent().remove(c)
    for c in root.xpath("//processing-instruction()"):
        c.getparent().remove(c)
    return root


def _validate_xml_with_schema(xml: etree._Element) -> bool:
    """Requires a cleaned (no comments) XML, but with the namespaces."""
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
            error_msg += f"{separator}Line {error.line}: {_beautify_err_msg(error.message)}"
        return error_msg
    return None


def _beautify_err_msg(err_msg: str) -> str:
    err_msg = err_msg.replace("{https://dasch.swiss/schema}", "")
    new_msg_for_duplicate_res_id = (
        "The resource ID '\\1' is not valid. IDs must be unique across the entire file. "
        "The function make_xsd_compatible_id() assists you in creating IDs."
    )
    rgx_for_duplicate_res_id = (
        r"Element '(?:resource|link|video-segment|audio-segment|region)', attribute 'id': '(.+?)' "
        r"is not a valid value of the atomic type 'xs:ID'."
    )
    err_msg = regex.sub(rgx_for_duplicate_res_id, new_msg_for_duplicate_res_id, err_msg)
    return err_msg
