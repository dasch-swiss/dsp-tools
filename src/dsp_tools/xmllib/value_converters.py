from typing import Any

from dsp_tools.xmllib.models.user_enums import NewlineReplacement


def convert_to_bool_string(value: Any) -> str:
    """
    Turns a value into a bool string, suitable for an XML.

    Args:
        value: value to transform

    Returns:
        'true' or 'false' if it is a known value,
        else it returns the original value as a string.
    """
    str_val = str(value).lower().strip()
    if str_val in ("false", "0", "0.0", "no"):
        return "false"
    elif str_val in ("true", "1", "1.0", "yes"):
        return "true"
    return str(value)


def replace_newlines_with_tags(text: str, converter_option: NewlineReplacement) -> str:
    """
    Converts the newlines in a string to XML tags.
    The type of tags is specified through the converter_option enum.

    Args:
        text: string to convert
        converter_option: tag options

    Returns:
        string with replaced values

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
    Replaces '\\n' with `<p>text</p>`

    Args:
        text: string to be formatted

    Returns:
        formatted string with tags
    """
    splt = [x for x in text.split("\n") if x != ""]
    formatted = [f"<p>{x}</p>" for x in splt]
    return "".join(formatted)


def replace_newlines_with_br_tags(text: str) -> str:
    """
    Replaces '\\n' with `<br/>`

    Args:
        text: string to be formatted

    Returns:
        formatted string with tags
    """
    return text.replace("\n", "<br/>")
