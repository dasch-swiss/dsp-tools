from __future__ import annotations

import importlib.resources
from copy import deepcopy
from pathlib import Path

import pandas as pd
import regex
from loguru import logger
from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.error.exceptions import UserFilepathNotFoundError
from dsp_tools.error.xsd_validation_error_msg import XSDValidationMessage
from dsp_tools.error.xsd_validation_error_msg import get_xsd_validation_message_str
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT

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
    if not Path(input_file).exists():
        raise UserFilepathNotFoundError(input_file)
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
    if errors := _validate_xml_tree_against_schema(xml):
        problem_msg = _get_validation_error_print_out(errors)
        logger.error(problem_msg)
        raise InputError(problem_msg)
    return True


def _validate_xml_tree_against_schema(data_xml: etree._Element) -> etree.XMLSchema | None:
    schema_res = importlib.resources.files("dsp_tools").joinpath("resources/schema/data.xsd")
    with schema_res.open(encoding="utf-8") as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    if not xmlschema.validate(data_xml):
        return xmlschema
    return None


def _get_validation_error_print_out(xmlschema: etree.XMLSchema) -> str:
    error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
    for error in xmlschema.error_log:
        error_msg += f"{separator}Line {error.line}: {_beautify_err_msg(error.message)}"
    return error_msg


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


def validate_root_emit_user_message(root: etree._Element, save_path: Path) -> None:
    validation_errors = _validate_root_get_validation_messages(root)
    if validation_errors:
        _emit_validation_errors(validation_errors, save_path)


def _validate_root_get_validation_messages(data_xml: etree._Element) -> list[XSDValidationMessage] | None:
    if errors := _validate_xml_tree_against_schema(data_xml):
        return _reformat_validation_errors(errors.error_log)
    return None


def _emit_validation_errors(validation_errors: list[XSDValidationMessage], save_path: Path) -> None:
    header_msg = f"During the XSD Schema validation the following {len(validation_errors)} error(s) were found: "
    print(BACKGROUND_BOLD_RED, header_msg, RESET_TO_DEFAULT)
    logger.error(header_msg)
    if len(validation_errors) > 50:
        save_path = save_path / "xsd_validation_errors.csv"
        message_dicts = [vars(x) for x in validation_errors]
        df = pd.DataFrame.from_records(message_dicts)
        df.to_csv(save_path, index=False)
        msg = f"Due to the large number of errors they are saved in the file '{save_path}'."
        print(BOLD_RED + msg, RESET_TO_DEFAULT)
        logger.error(msg)
    else:
        for one_msg in validation_errors:
            msg_str = get_xsd_validation_message_str(one_msg)
            print(BOLD_RED, msg_str, RESET_TO_DEFAULT)
            logger.error(msg_str)


def _reformat_validation_errors(log: etree._ListErrorLog) -> list[XSDValidationMessage]:
    return [_reformat_error_message_str(err.message, err.line) for err in log]


def _reformat_error_message_str(msg: str, line_number: int) -> XSDValidationMessage:
    element, attrib = None, None
    msg = msg.replace("{https://dasch.swiss/schema}", "")
    first, message = msg.split(":", maxsplit=1)
    if ele_found := regex.search(r"Element '(.*?)'", first):
        element = ele_found.group(1)
    if attrib_found := regex.search(r"attribute '(.*?)'", first):
        attrib = attrib_found.group(1)
    if " is not a valid value of the atomic type 'xs:ID'." in message:
        if found := regex.search(r"'.*?'", message):
            id_ = found.group(0)
        else:
            id_ = ""
        message = f"The provided resource id {id_} is either not a valid xsd:ID or not unique in the file."
    else:
        message = regex.sub(r"\[facet .+\] ", "", message)
        message = regex.sub(r"pattern ('.+')", "pattern for this value", message).strip()
    return XSDValidationMessage(line_number=line_number, element=element, attribute=attrib, message=message)
