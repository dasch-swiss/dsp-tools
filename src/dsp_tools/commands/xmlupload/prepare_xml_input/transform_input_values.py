from __future__ import annotations

import json
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Callable
from typing import TypeAlias
from typing import Union
from typing import assert_never

import regex

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValueTypes
from dsp_tools.commands.xmlupload.models.intermediary.values import IntervalFloats
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.data_formats.date_util import Date
from dsp_tools.utils.data_formats.date_util import parse_date_string

InputTypes: TypeAlias = Union[str, FormattedTextValue, tuple[str | None, str | None] | None]


@dataclass
class TypeTransformerMapper:
    val_type: type[IntermediaryValue]
    val_transformer: Callable[[InputTypes], IntermediaryValueTypes]


def assert_is_string(value: InputTypes) -> str:
    """Assert a value is a string."""
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise InputError(f"Expected string value, but got XML value: {xml.as_xml()}")
        case tuple():
            raise InputError(f"Expected string value, but got tuple value: {value}")
        case None:
            raise InputError("Expected string value, but got None")
        case _:
            assert_never(value)


def assert_is_tuple(value: InputTypes) -> tuple[str, str]:
    """Assert a value is a tuple."""
    match value:
        case tuple() as t:
            if not len(t) == 2:
                raise InputError(f"Expected tuple with two elements but got {value}")
            return t
        case FormattedTextValue() as xml:
            raise InputError(f"Expected tuple value, but got XML value: {xml.as_xml()}")
        case str():
            raise InputError(f"Expected tuple value, but got string value: {value}")
        case None:
            raise InputError("Expected tuple value, but got None")
        case _:
            assert_never(value)


def transform_boolean(value: InputTypes) -> bool:
    """Transform the value into a boolean"""
    match value:
        case "True" | "true" | "1" | 1 | True:
            return True
        case "False" | "false" | "0" | 0 | False:
            return False
        case _:
            raise InputError(f"Could not parse boolean value: {value}")


def transform_date(input_value: InputTypes) -> Date:
    """Transform a date string into a date object."""
    val = assert_is_string(input_value)
    return parse_date_string(val)


def transform_decimal(value: InputTypes) -> float:
    """Transform a value into a float"""
    str_val = assert_is_string(value)
    return float(str_val)


def transform_integer(value: InputTypes) -> int:
    """Transform a value into an integer"""
    str_val = assert_is_string(value)
    return int(str_val)


def transform_interval(input_value: InputTypes) -> IntervalFloats:
    """Transform a string input into an interval object."""
    val = assert_is_tuple(input_value)
    try:
        return IntervalFloats(float(val[0]), float(val[1]))
    except ValueError:
        raise InputError(f"Could not parse interval: {val}") from None


def transform_geometry(value: InputTypes) -> str:
    """Transform a value into a geometry string"""
    str_val = assert_is_string(value)
    try:
        return json.dumps(json.loads(str_val))
    except JSONDecodeError:
        raise InputError(f"Could not parse json value: {value}") from None


def transform_simpletext(value: InputTypes) -> str:
    str_val = assert_is_string(value)
    # replace multiple spaces or tabstops by a single space
    str_val = regex.sub(r" {2,}|\t+", " ", str_val)
    # remove leading and trailing spaces (of every line, but also of the entire string)
    str_val = "\n".join([s.strip() for s in str_val.split("\n")])
    result = str_val.strip()
    if len(result) == 0:
        raise InputError("After removing redundant whitespaces and newlines the input string is empty.")
    return result


def transform_richtext(value: InputTypes) -> FormattedTextValue:
    str_val = assert_is_string(value)
    result = cleanup_formatted_text(str_val)
    if len(result) == 0:
        raise InputError("After removing redundant whitespaces and newlines the input string is empty.")
    return FormattedTextValue(result)


def cleanup_formatted_text(xmlstr_orig: str) -> str:
    """
    In a xml-encoded text value from the XML file,
    there may be non-text characters that must be removed.
    This function:
        - replaces (multiple) line breaks by a space
        - replaces multiple spaces or tabstops by a single space (except within `<code>` or `<pre>` tags)

    Args:
        xmlstr_orig: content of the tag from the XML file, in serialized form

    Returns:
        purged string, suitable to be sent to DSP-API
    """
    # replace (multiple) line breaks by a space
    xmlstr = regex.sub("\n+", " ", xmlstr_orig)
    # replace multiple spaces or tabstops by a single space (except within <code> or <pre> tags)
    # the regex selects all spaces/tabstops not followed by </xyz> without <xyz in between.
    # credits: https://stackoverflow.com/a/46937770/14414188
    xmlstr = regex.sub("( {2,}|\t+)(?!(.(?!<(code|pre)))*</(code|pre)>)", " ", xmlstr)
    # remove spaces after <br/> tags (except within <code> tags)
    xmlstr = regex.sub("((?<=<br/?>) )(?!(.(?!<code))*</code>)", "", xmlstr)
    # remove leading and trailing spaces
    xmlstr = xmlstr.strip()
    return xmlstr
