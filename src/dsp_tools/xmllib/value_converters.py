from typing import Any

import regex

from dsp_tools.xmllib.models.config_options import NewlineReplacement


def convert_to_bool_string(value: Any) -> str:
    """
    Turns a value into a bool string, suitable for an XML.
    It is case-insensitive, meaning that the words can also be capitalised.

    Accepted values:
         - `false`, `0`, `0.0`, `no`, `non`, `nein` -> `false`
         - `true`, `1`, `1.0`, `yes`, `oui`, `ja` -> `true`

    Args:
        value: value to transform

    Returns:
        `"true"` or `"false"` if it is an accepted value,
        else it returns the original value as a string.
    """
    str_val = str(value).lower().strip()
    if str_val in ("false", "0", "0.0", "no", "non", "nein"):
        return "false"
    elif str_val in ("true", "1", "1.0", "yes", "oui", "ja"):
        return "true"
    return str(value)


def escape_reserved_chars(text: str) -> str:
    """
    From richtext strings (encoding="xml"), escape the reserved characters <, > and &,
    but only if they are not part of a standard standoff tag or escape sequence.
    The standard standoff tags allowed by DSP-API are documented here:
    https://docs.dasch.swiss/2023.12.01/DSP-API/03-endpoints/api-v2/text/standard-standoff/

    Args:
        text: the richtext string to be escaped

    Returns:
        the escaped richtext string
    """
    allowed_tags = [
        "a( [^>]+)?",  # <a> is the only tag that can have attributes
        "p",
        "em",
        "strong",
        "u",
        "sub",
        "sup",
        "strike",
        "h1",
        "ol",
        "ul",
        "li",
        "tbody",
        "table",
        "tr",
        "td",
        "br",
        "hr",
        "pre",
        "cite",
        "blockquote",
        "code",
    ]
    allowed_tags_regex = "|".join(allowed_tags)
    lookahead = rf"(?!/?({allowed_tags_regex})/?>)"
    illegal_lt = rf"<{lookahead}"
    lookbehind = rf"(?<!</?({allowed_tags_regex})/?)"
    illegal_gt = rf"{lookbehind}>"
    illegal_amp = r"&(?![#a-zA-Z0-9]+;)"
    text = regex.sub(illegal_lt, "&lt;", text)
    text = regex.sub(illegal_gt, "&gt;", text)
    text = regex.sub(illegal_amp, "&amp;", text)
    return text


def replace_newlines_with_tags(text: str, converter_option: NewlineReplacement) -> str:
    """
    Converts the newlines in a string to XML tags.
    The type of tags is specified through the converter_option enum.

    Args:
        text: string to convert
        converter_option: tag options

    Returns:
        String with replaced values

    Raises:
        InputError: If an invalid conversion option is given
    """
    match converter_option:
        case NewlineReplacement.NONE:
            return text
        case NewlineReplacement.LINEBREAK:
            return replace_newlines_with_br_tags(text)
        case NewlineReplacement.PARAGRAPH:
            return replace_newlines_with_paragraph_tags(text)


def replace_newlines_with_paragraph_tags(text: str) -> str:
    """
    Replace `Start\\nEnd` with `<p>Start</p><p>End</p>`

    Multiple consecutive newlines will be treated as one newline:
    `Start\\nMiddle\\n\\nEnd` becomes `<p>Start</p><p>Middle</p><p>End</p>`

    Args:
        text: string to be formatted

    Returns:
        Formatted string with paragraph tags
    """
    splt = [x for x in text.split("\n") if x != ""]
    formatted = [f"<p>{x}</p>" for x in splt]
    return "".join(formatted)


def replace_newlines_with_br_tags(text: str) -> str:
    """
    Replaces `Start\\nEnd` with `Start<br/>End`

    Multiple consecutive newlines will be converted into multiple break-lines:
    `Start\\n\\nEnd` with `Start<br/><br/>End`

    Args:
        text: string to be formatted

    Returns:
        Formatted string with break-line tags
    """
    return text.replace("\n", "<br/>")
