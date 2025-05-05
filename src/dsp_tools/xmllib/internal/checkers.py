from __future__ import annotations

from typing import Any

import pandas as pd
import regex
from lxml import etree

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_info
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.xmllib.helpers import escape_reserved_xml_characters
from dsp_tools.xmllib.internal.input_converters import numeric_entities


def is_nonempty_value_internal(value: Any) -> bool:
    """
    This is a duplicate of value_checkers.is_nonempty_value(), to avoid circular imports.

    Check if a value is not None-like
    or that its string representation contains at least one of the following characters:

    - ``\\p{S}`` = symbols and special characters
    - ``\\p{P}`` = punctuation
    - ``\\w`` = all Unicode letters, numbers, and _

    Args:
        value: value of any type

    Returns:
        True if the value is not None-like and contains at least one of the above-mentioned characters
    """
    if pd.isna(value):
        return False
    if regex.search(r"[\p{S}\p{P}\w]", str(value), flags=regex.UNICODE):
        return True
    return False


def check_and_warn_potentially_empty_string(
    *, value: Any, res_id: str | None, expected: str, prop_name: str | None = None, field: str | None = None
) -> None:
    """
    If a user str() casts an input before using it in the xmllib we may get `None` values that are not recognised
    as potentially empty.
    This is to be used if the potentially erroneous input is not detectable through any other check.
    For example a color or date value has its specific regex and it is not possible for such a value to slip through.

    Args:
        value: user input
        res_id: Resource ID
        expected: the type of value that is expected
        prop_name: property name if used to check a property
        field: if used to check a non-property field, for example a comment on a value

    Warnings:
        XmllibInputWarning: if it is an empty value or a string only with whitespaces
        XmllibInputInfo: if it is a string containing a string value
            that may be the result of str() casting an empty value
    """
    if not is_nonempty_value_internal(value):
        msg_info = MessageInfo(
            message=f"Your input '{value}' is empty. Please enter a valid {expected}.",
            resource_id=res_id,
            prop_name=prop_name,
            field=field,
        )
        emit_xmllib_input_warning(msg_info)
    else:
        check_and_warn_if_a_string_contains_a_potentially_empty_value(
            value=value, res_id=res_id, prop_name=prop_name, field=field
        )


def check_and_warn_if_a_string_contains_a_potentially_empty_value(
    *, value: Any, res_id: str | None, prop_name: str | None = None, field: str | None = None
) -> None:
    """
    If a user str() casts an input before using it in the xmllib we may get `None` values that are not recognised
    as potentially empty.
    This is to be used if the potentially erroneous input is not detectable through any other check.

    Args:
        value: user input
        res_id: Resource ID
        prop_name: property name if used to check a property
        field: if used to check a non-property field, for example a comment on a value

    Warnings:
        XmllibInputInfo: if it is a string containing a string value
            that may be the result of str() casting an empty value
    """
    empty_val_string = r"^(<NA>|nan|None)$"
    if bool(regex.search(empty_val_string, str(value))):
        type_lookup = {"<NA>": "pd.NA", "nan": "np.nan", "None": "None"}
        msg = (
            f"Your input '{value}' is a string but may be the result of `str({type_lookup[str(value)]})`. "
            f"Please verify that the input is as expected."
        )
        msg_info = MessageInfo(
            message=msg,
            resource_id=res_id,
            prop_name=prop_name,
            field=field,
        )
        emit_xmllib_input_info(msg_info)


def parse_richtext_as_xml(
    input_str: str, resource_id: str | None = None, prop_name: str | None = None
) -> etree._Element | MessageInfo:
    """
    Parses an input string as XML. If it contains a syntax error a MessageInfo is returned.
    Else it returns the XML as etree

    Args:
        input_str: Richtext string
        resource_id: ID of the resource for improved error message
        prop_name: Property name for improved error message

    Returns:
        Parsed string or information for the user message.
    """
    escaped_text = escape_reserved_xml_characters(input_str)
    num_ent = numeric_entities(escaped_text)
    pseudo_xml = f"<ignore-this>{num_ent}</ignore-this>"
    try:
        return etree.fromstring(pseudo_xml)
    except etree.XMLSyntaxError as err:
        msg_str = (
            f"The entered richtext value could not be converted to a valid XML.\n"
            f"Original error message: {err.msg}\n"
            f"Potential line/column numbers are relative to this text: {pseudo_xml}"
        )
        return MessageInfo(resource_id=resource_id, prop_name=prop_name, message=msg_str)
