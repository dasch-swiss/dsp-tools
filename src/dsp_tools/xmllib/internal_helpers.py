from __future__ import annotations

import warnings
from html.entities import html5
from typing import Any

import pandas as pd
import regex

from dsp_tools.error.exceptions import InputError
from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_info
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.value_converters import replace_newlines_with_tags

# These named entities are defined by the XML specification and are always expanded during parsing,
# regardless of parser options.
# Numeric character references (e.g., `&#34;` or `&#x22;`) are also always resolved
PREDEFINED_XML_ENTITIES = ["&amp;", "&lt;", "&gt;", "&quot;", "&apos;"]


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
    *, value: Any, res_id: str, expected: str, prop_name: str | None = None, field: str | None = None
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
            message=f"Your input is empty. Please enter a valid {expected}.",
            resource_id=res_id,
            prop_name=prop_name,
            field=field,
        )
        emit_xmllib_input_warning(msg_info)
    else:
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


def check_and_create_richtext_string(
    value: Any,
    prop_name: str,
    newline_replacement: NewlineReplacement,
    res_id: str,
) -> str:
    """
    Creates a RichtextValue with checks and optional conversions

    Args:
        value: richtext value
        prop_name: name of the property
        newline_replacement: the replacement for the newlines in the string
        res_id: id of the calling resource

    Returns:
        A richtext value

    Raises:
        Input Error if the input is a dictionary
    """
    # Because of the richtext conversions, the input value is cast to a string.
    # Values such as str(`pd.NA`) result in a non-empy string.
    # Therefore, a check must occur before the casting takes place.
    check_and_warn_potentially_empty_string(value=value, res_id=res_id, expected="string", prop_name=prop_name)
    return replace_newlines_with_tags(str(value), newline_replacement)


def check_richtext_before_conversion(value: Any, prop_name: str, res_id: str) -> None:
    """
    Checks if the input which is expected to be richtext is a string.

    Args:
        value: Input value
        prop_name: Property name
        res_id: Resource ID
    """
    if not is_nonempty_value_internal(value):
        msg = f"Resource '{res_id}' has a richtext value that is not a string: Value: {value} | Property: {prop_name}"
        warnings.warn(XmllibInputWarning(msg))


def check_and_fix_collection_input(value: Any, prop_name: str, res_id: str) -> list[Any]:
    """
    To allow varied input but ensure consistent typing internally, collections are converted.
    If a collection is empty, a warning is emitted for the user.

    Args:
        value: Input value
        prop_name: Property name
        res_id: Resource ID

    Returns:
        The input as a list

    Raises:
        InputError: if the input is a dictionary
    """
    msg = f"The input value of the resource with the ID '{res_id}' and the property '{prop_name}' "
    match value:
        case set() | list() | tuple():
            if len(value) == 0:
                msg += "is empty. Please note that no values will be added to the resource."
                warnings.warn(XmllibInputInfo(msg))
            return list(value)
        case dict():
            msg += "is a dictionary. Only collections (list, set, tuple) are permissible."
            raise InputError(msg)
        case _:
            return [value]


def unescape_reserved_xml_chars(richtext: str) -> str:
    """
    This function unescapes characters that are reserved in an XML.

    Args:
        richtext: Text to be escaped

    Returns:
        Escaped string
    """
    richtext = regex.sub(r"&lt;", "<", richtext or "")
    richtext = regex.sub(r"&gt;", ">", richtext)
    richtext = regex.sub(r"&amp;", "&", richtext)
    return richtext


def numeric_entities(text: str) -> str:
    """
    Make a string suitable to be written to an XML file,
    by replacing all named HTML entities by their decimal numeric counterparts,
    except the ones that are predefined in the XML specification.
    Numeric HTML entities remain untouched.
    Unescaped special characters remain untouched.

    Args:
        text: original text

    Returns:
        text with all named entities replaced

    Examples:
        ```python
        result = xmllib.numeric_entities('&nbsp; &quot;')
        # result == '&#160; &quot;'
        ```
    """
    replacements: dict[str, str] = {}
    for match in regex.findall(r"&[0-9A-Za-z]+;", text):
        if match in PREDEFINED_XML_ENTITIES:
            continue
        char = html5[match[1:]]
        replacements[match] = f"&#{ord(char)};"
    text = regex.sub(
        r"&[0-9A-Za-z]+;",
        lambda x: replacements[x.group()] if x.group() not in PREDEFINED_XML_ENTITIES else x.group(),
        text,
    )
    return text
