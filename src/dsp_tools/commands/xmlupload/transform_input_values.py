from __future__ import annotations

import json
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Callable
from typing import TypeAlias
from typing import Union
from typing import assert_never

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValueTypes
from dsp_tools.commands.xmlupload.models.intermediary.values import IntervalFloats
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.date_util import Date
from dsp_tools.utils.date_util import parse_date_string

InputTypes: TypeAlias = Union[str, FormattedTextValue]


@dataclass
class TypeTransformerMapper:
    val_type: type[IntermediaryValue]
    val_transformer: Callable[[InputTypes], IntermediaryValueTypes]


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
    """Transform a sting input into an interval object."""
    val = assert_is_string(input_value)
    split_val = [res for x in val.split(":", 1) if (res := x.strip())]
    if not len(split_val) == 2:
        raise InputError(f"Could not parse interval: {val}")
    try:
        return IntervalFloats(float(split_val[0]), float(split_val[1]))
    except ValueError:
        raise InputError(f"Could not parse interval: {val}") from None


def transform_geometry(value: InputTypes) -> str:
    """Transform a value into a geometry string"""
    str_val = assert_is_string(value)
    try:
        return json.dumps(json.loads(str_val))
    except JSONDecodeError:
        raise InputError(f"Could not parse json value: {value}") from None


def assert_is_string(value: str | FormattedTextValue) -> str:
    """Assert a value is a string."""
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise InputError(f"Expected string value, but got XML value: {xml.as_xml()}")
        case _:
            assert_never(value)
