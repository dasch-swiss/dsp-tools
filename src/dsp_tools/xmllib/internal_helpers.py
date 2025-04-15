from __future__ import annotations

import warnings
from html.entities import html5
from typing import Any

import pandas as pd
import regex

from dsp_tools.error.custom_warnings import DspToolsUserInfo
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import InputError
from dsp_tools.xmllib.constants import KNOWN_XML_TAG_REGEXES
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.value_converters import replace_newlines_with_tags


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
    if not is_nonempty_value_internal(value):
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


def unescape_standoff_tags(xml_str: str) -> str:
    """
    Unescape `&lt;` and `&gt;` in DSP standard standoff tags.
    Inside richtext values, the tags are escaped, because lxml doesn't treat elem.text as XML.
    Before writing such an XML string to a file, the tags must be unescaped, otherwise they won't be recognized.

    Args:
        xml_str: a serialised XML string

    Returns:
        string ready to be written to a file
    """
    contained_xml_tags = filter(lambda x: regex.search(x, xml_str), KNOWN_XML_TAG_REGEXES)
    for tag in contained_xml_tags:
        tag_opening_corrected = regex.sub(r"[^a-zA-Z0-9]", "", tag)
        tag_closing_corrected = tag_opening_corrected
        if match := regex.search(f"&lt;{tag}&gt;", xml_str):
            if groups := match.groups():
                tag_opening_corrected = f"{tag_opening_corrected}{groups[0]}"
        xml_str = regex.sub(f"&lt;{tag}&gt;", f"<{tag_opening_corrected}>", xml_str)
        xml_str = regex.sub(f"&lt;/{tag}&gt;", f"</{tag_closing_corrected}>", xml_str)
    return xml_str


def numeric_entities(text: str) -> str:
    """
    Replace all named HTML entities by their decimal numeric counterparts.
    Hex numeric HTML entities remain untouched.
    Unescaped special characters remain untouched.

    Args:
        text: original text

    Returns:
        text with all named entities replaced

    Examples:
        ```python
        result = xmllib.numeric_entities('text &quot; &#x22; " text')
        # result == 'Text &#34; &#x22; " text'
        ```
    """
    named_ent_ok = ["&amp;", "&lt;", "&gt;", "&quot;", "&apos;"]  # these named entities are supported in XML
    replacements: dict[str, str] = {}
    for match in regex.findall(r"&[0-9A-Za-z]+;", text):
        if match in named_ent_ok:
            continue
        char = html5[match[1:]]
        replacements[match] = f"&#{ord(char)};"
    text = regex.sub(
        r"&[0-9A-Za-z]+;", lambda x: replacements[x.group()] if x.group() not in named_ent_ok else x.group(), text
    )
    return text
