from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from typing import TypeAlias
from typing import Union
from typing import assert_never

from rdflib import XSD
from rdflib import Literal

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import Interval
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseDate
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseInterval
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import ValueSerialiser
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.date_util import Date
from dsp_tools.utils.date_util import parse_date_string

InputTypes: TypeAlias = Union[str, FormattedTextValue]
OutputTypes: TypeAlias = Union[str, Date, Interval]
ValueTransformer: TypeAlias = Callable[[InputTypes], OutputTypes]


@dataclass
class TransformationSteps:
    serialiser: ValueSerialiser
    transformer: ValueTransformer


def transform_boolean(s: str | int | bool) -> bool:
    """Takes an input value and transforms it into a boolean."""
    match s:
        case "True" | "true" | "1" | 1 | True:
            return True
        case "False" | "false" | "0" | 0 | False:
            return False
        case _:
            raise BaseError(f"Could not parse boolean value: {s}")


def transform_date(input_value: InputTypes) -> Date:
    """Transform a date string into a date object."""
    val = assert_is_string(input_value)
    return parse_date_string(val)


def transform_interval(input_value: InputTypes) -> Interval:
    """Transform a sting input into an interval object."""
    val = assert_is_string(input_value)
    match val.split(":", 1):
        case [start, end]:
            return Interval(start, end)
        case _:
            raise BaseError(f"Could not parse interval value: {input_value}")


def transform_string(input_value: InputTypes) -> str:
    """Assert that an input is of type string."""
    return assert_is_string(input_value)


def assert_is_string(value: str | FormattedTextValue) -> str:
    """Assert a value is a string."""
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise BaseError(f"Expected string value, but got XML value: {xml.as_xml()}")
        case _:
            assert_never(value)


value_to_transformations_mapper: dict[str, TransformationSteps] = {
    "date": TransformationSteps(SerialiseDate, transform_date),
    "interval": TransformationSteps(SerialiseInterval, transform_interval),
}


def transform_xsd_string(value: InputTypes):
    str_val = assert_is_string(value)
    return Literal(str_val, datatype=XSD.string)


def transform_xsd_decimal(value: InputTypes):
    str_val = assert_is_string(value)
    return Literal(str(float(str_val)), datatype=XSD.decimal)


def transform_xsd_boolean(value: InputTypes):
    match value:
        case "True" | "true" | "1" | 1 | True:
            return Literal(True, datatype=XSD.boolean)
        case "False" | "false" | "0" | 0 | False:
            return Literal(False, datatype=XSD.boolean)
        case _:
            raise BaseError(f"Could not parse boolean value: {value}")


def transform_xsd_integer(value: InputTypes):
    str_val = assert_is_string(value)
    return Literal(str_val, datatype=XSD.integer)


def transform_xsd_date_time(value: InputTypes):
    str_val = assert_is_string(value)
    return Literal(str_val, datatype=XSD.dateTimeStamp)


def transform_xsd_any_uri(value: InputTypes):
    str_val = assert_is_string(value)
    return Literal(str_val, datatype=XSD.anyURI)


def transform_geometry(value: InputTypes):
    str_val = assert_is_string(value)
    str_val = json.dumps(json.loads(str_val))
    return Literal(str_val, datatype=XSD.string)


rdf_literal_transformer = {
    "boolean": transform_xsd_boolean,
    "color": transform_xsd_string,
    "decimal": transform_xsd_decimal,
    "geometry": transform_geometry,
    "geoname": transform_xsd_string,
    "integer": transform_xsd_integer,
    "time": transform_xsd_date_time,
    "uri": transform_xsd_any_uri,
}
