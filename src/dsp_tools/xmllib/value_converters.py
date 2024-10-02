from typing import Any

from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.value_converter_enums import NewlineReplacementTags


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


def replace_newlines_with_tags(text: str, converter_option: NewlineReplacementTags) -> str:
    """
    Converts the newlines in a string to XML tags.
    The type of tags is specified through the converter_option enum.

    Args:
        text: string to convert
        converter_option: tag options

    Returns:
        string with replaced values
    """
    match converter_option:
        case NewlineReplacementTags.none:
            return text
        case NewlineReplacementTags.newline:
            return replace_newlines_with_br_tags(text)
        case NewlineReplacementTags.paragraph:
            return replace_newlines_with_paragraph_tags(text)
        case _:
            raise InputError(f"The conversion option for the text does not exist: {converter_option}.")


def replace_newlines_with_paragraph_tags(text: str) -> str:
    """Replaces '\n' with <p>text</p>"""
    splt = [x for x in text.split("\n") if x != ""]
    formatted = [f"<p>{x}</p>" for x in splt]
    return "".join(formatted)


def replace_newlines_with_br_tags(text: str) -> str:
    """Replaces '\n' with <br/>"""
    return text.replace("\n", "<br/>")
