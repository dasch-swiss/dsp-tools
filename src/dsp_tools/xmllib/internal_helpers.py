from __future__ import annotations

import warnings
from typing import Any

import pandas as pd
import regex

from dsp_tools.models.custom_warnings import DspToolsUserInfo
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.value_converters import replace_newlines_with_tags


def _like_string(value: Any) -> bool:
    if pd.isna(value):
        return False
    value = str(value).strip()
    if len(value) == 0:
        return False
    return bool(regex.search(r"\S", value, flags=regex.UNICODE))


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
    check_richtext_before_conversion(value, prop_name, res_id)
    return replace_newlines_with_tags(str(value), newline_replacement)


def check_richtext_before_conversion(value: Any, prop_name: str, res_id: str) -> None:
    """
    Checks if the input which is expected to be richtext is a string.

    Args:
        value: Input value
        prop_name: Property name
        res_id: Resource ID
    """
    if not _like_string(value):
        msg = f"Resource '{res_id}' has a richtext value that is not a string: Value: {value} | Property: {prop_name}"
        warnings.warn(DspToolsUserWarning(msg))


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
                warnings.warn(DspToolsUserInfo(msg))
            return list(value)
        case dict():
            msg += "is a dictionary. Only collections (list, set, tuple) are permissible."
            raise InputError(msg)
        case _:
            return [value]


def escape_reserved_xml_chars(richtext: str, known_tags: list[str]) -> str:
    """
    This function escapes characters that are reserved in an XML.
    The angular brackets around the known tags will not be escaped.

    Args:
        richtext: Text to be escaped
        known_tags: tags that should remain XML tags

    Returns:
        Escaped string
    """
    known_tags_regex = "|".join(known_tags)
    lookahead = rf"(?!/?({known_tags_regex})/?>)"
    illegal_lt = rf"<{lookahead}"
    lookbehind = rf"(?<!</?({known_tags_regex})/?)"
    illegal_gt = rf"{lookbehind}>"
    illegal_amp = r"&(?![#a-zA-Z0-9]+;)"
    richtext = regex.sub(illegal_lt, "&lt;", richtext or "")
    richtext = regex.sub(illegal_gt, "&gt;", richtext)
    richtext = regex.sub(illegal_amp, "&amp;", richtext)
    return richtext


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
