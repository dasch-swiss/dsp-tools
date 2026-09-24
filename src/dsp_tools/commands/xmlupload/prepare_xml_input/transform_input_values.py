from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Union
from typing import assert_never
from typing import cast

from loguru import logger

from dsp_tools.commands.xmlupload.exceptions import XmlInputConversionError
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.processed.values import IntervalFloats
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedValue
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedValueTypes
from dsp_tools.utils.data_formats.date_util import Date
from dsp_tools.utils.data_formats.date_util import parse_date_string
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedGeolocation
from dsp_tools.xmllib.internal.geolocation import compose_geolocation_literal_from_ordinates
from dsp_tools.xmllib.internal.geolocation import get_geolocation_problem

type InputTypes = Union[str, FormattedTextValue, tuple[str | None, str | None], ParsedGeolocation | None]


@dataclass
class TypeTransformerMapper:
    val_type: type[ProcessedValue]
    val_transformer: Callable[[InputTypes], ProcessedValueTypes]


def assert_is_string(value: InputTypes) -> str:
    """Assert a value is a string."""
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise XmlInputConversionError(f"Expected string value, but got XML value: {xml.xmlstr}")
        case tuple():
            raise XmlInputConversionError(f"Expected string value, but got tuple value: {value}")
        case ParsedGeolocation():
            raise XmlInputConversionError(f"Expected string value, but got geolocation value: {value}")
        case None:
            raise XmlInputConversionError("Expected string value, but got None")
        case _:
            assert_never(value)


def assert_is_tuple(value: InputTypes) -> tuple[str, str]:
    """Assert a value is a tuple."""
    match value:
        case tuple() as t:
            if len(t) == 2 and isinstance(t[0], str) and isinstance(t[1], str):
                return cast(tuple[str, str], t)
            raise XmlInputConversionError(f"Expected tuple with two elements but got {value}")
        case FormattedTextValue() as xml:
            raise XmlInputConversionError(f"Expected tuple value, but got XML value: {xml.xmlstr}")
        case str():
            raise XmlInputConversionError(f"Expected tuple value, but got string value: {value}")
        case ParsedGeolocation():
            raise XmlInputConversionError(f"Expected tuple value, but got geolocation value: {value}")
        case None:
            raise XmlInputConversionError("Expected tuple value, but got None")
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
            raise XmlInputConversionError(f"Could not parse boolean value: {value}")


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
        msg = f"Could not parse interval: {val}"
        logger.exception(msg)
        raise XmlInputConversionError(msg) from None


def transform_geolocation(input_value: InputTypes) -> str:
    """Check a geolocation against its CRS and compose its literal."""
    # The check also runs in validate-data, but repeating it here means that
    # an invalid coordinate is rejected even when the upload skips validation.
    if not isinstance(input_value, ParsedGeolocation):
        raise XmlInputConversionError(f"Expected a geolocation value, but got {input_value}")
    if problem := get_geolocation_problem(input_value.crs, input_value.ordinates):
        raise XmlInputConversionError(problem)
    literal = compose_geolocation_literal_from_ordinates(input_value.crs, input_value.ordinates)
    if literal is None:
        raise XmlInputConversionError(f"Could not compose geolocation: {input_value}")
    return literal


def transform_geometry(value: InputTypes) -> str:
    """Transform a value into a geometry string"""
    str_val = assert_is_string(value)
    try:
        return json.dumps(json.loads(str_val))
    except JSONDecodeError:
        msg = f"Could not parse json value: {value}"
        logger.exception(msg)
        raise XmlInputConversionError(msg) from None


def transform_simpletext(value: InputTypes) -> str:
    str_val = assert_is_string(value)
    if len(str_val) == 0:
        raise XmlInputConversionError("After removing redundant whitespaces and newlines the input string is empty.")
    return str_val


def transform_richtext(value: InputTypes) -> FormattedTextValue:
    str_val = assert_is_string(value)
    if len(str_val) == 0:
        raise XmlInputConversionError("After removing redundant whitespaces and newlines the input string is empty.")
    return FormattedTextValue(str_val)
