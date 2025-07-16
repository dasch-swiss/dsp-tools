from __future__ import annotations

from html.entities import html5
from typing import Any

import regex

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_info
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_type_mismatch_warning
from dsp_tools.error.xmllib_warnings_util import raise_xmllib_input_error
from dsp_tools.xmllib.internal.checkers import check_and_warn_if_a_string_contains_a_potentially_empty_value
from dsp_tools.xmllib.internal.checkers import is_nonempty_value_internal
from dsp_tools.xmllib.internal.constants import PREDEFINED_XML_ENTITIES


def check_and_get_corrected_comment(comment: Any, res_id: str | None, prop_name: str | None) -> str | None:
    """The input of comments may also be pd.NA or such. In our models we only want a string or None."""
    if is_nonempty_value_internal(comment):
        check_and_warn_if_a_string_contains_a_potentially_empty_value(
            value=comment,
            res_id=res_id,
            prop_name=prop_name,
            field="comment on value",
        )
        return str(comment)
    return None


def check_and_fix_is_non_empty_string(
    value: Any, res_id: str | None = None, prop_name: str | None = None, value_field: str | None = None
) -> str:
    """
    Emits warnings if the string is or looks empty.
    Converts a non-empty input into a string.
    Returns an empty string if the input is empty (eg. pd.NA, None, etc.).

    Args:
        value: input to check
        res_id: resource ID
        prop_name: property name
        value_field: field if it is not a property

    Returns:
        The value as string, if it is empty an empty string.
    """
    if is_nonempty_value_internal(value):
        check_and_warn_if_a_string_contains_a_potentially_empty_value(
            value=value,
            res_id=res_id,
            prop_name=prop_name,
            field=value_field,
        )
        return str(value)
    else:
        emit_xmllib_input_type_mismatch_warning(
            expected_type="non empty string",
            value=value,
            res_id=res_id,
            prop_name=prop_name,
            value_field=value_field,
        )
        return ""


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
        XmllibInputError: if the input is a dictionary
    """
    match value:
        case set() | list() | tuple():
            if len(value) == 0:
                msg_info = MessageInfo(
                    message="The input is empty. Please note that no values will be added to the resource.",
                    resource_id=res_id,
                    prop_name=prop_name,
                )
                emit_xmllib_input_info(msg_info)
            return list(value)
        case dict():
            msg_info = MessageInfo(
                message="The input is a dictionary. Only collections (list, set, tuple) are permissible.",
                resource_id=res_id,
                prop_name=prop_name,
            )
            raise_xmllib_input_error(msg_info)
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
