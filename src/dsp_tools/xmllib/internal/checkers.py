from __future__ import annotations

from typing import Any

import pandas as pd
import regex

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_info
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning


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


def is_date_internal(value: Any) -> bool:
    """
    Is it a valid dsp-date.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    calendar_optional = r"(?:(GREGORIAN|JULIAN|ISLAMIC):)?"
    first_era_optional = r"(?:(CE|BCE|BC|AD):)?"
    second_area_optional = r"(?::(CE|BCE|BC|AD))?"
    date = r"\d{1,4}(?:-\d{1,2}){0,2}"
    date_mandatory = rf"({date})"
    date_optional = rf"(:{date})?"
    full_date_pattern = (
        rf"^{calendar_optional}{first_era_optional}{date_mandatory}{second_area_optional}{date_optional}$"
    )
    found = regex.search(full_date_pattern, str(value))
    if not found:
        return False
    if found.group(1) == "ISLAMIC" and (found.group(2) or found.group(4)):
        # eras are not supported yet for the islamic calendar
        return False
    return True


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


def check_and_inform_about_angular_brackets(value: Any, res_id: str | None, prop_name: str | None = None) -> None:
    """
    Checks if a string value contains angular brackets.

    Args:
        value: String value
        res_id: resource id
        prop_name: property name
    """
    if bool(regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(value))):
        msg_info = MessageInfo(
            message=(
                f"Your input '{value}' contains angular brackets. "
                f"Since this is a simpletext, please note that these will not be recognised as formatting "
                f"in the text field, but will be displayed as-is."
            ),
            resource_id=res_id,
            prop_name=prop_name,
        )
        emit_xmllib_input_info(msg_info)
