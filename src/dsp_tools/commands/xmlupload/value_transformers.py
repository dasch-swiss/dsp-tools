from __future__ import annotations

import json
from json.decoder import JSONDecodeError
from typing import TypeAlias
from typing import Union
from typing import assert_never

from rdflib import XSD
from rdflib import Literal

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_rdf_value import Interval
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.date_util import Date
from dsp_tools.utils.date_util import parse_date_string

InputTypes: TypeAlias = Union[str, FormattedTextValue]


def transform_xsd_boolean(value: InputTypes) -> Literal:
    """Takes an input value and transforms it into an xsd:boolean."""
    match value:
        case "True" | "true" | "1" | 1 | True:
            return Literal(True, datatype=XSD.boolean)
        case "False" | "false" | "0" | 0 | False:
            return Literal(False, datatype=XSD.boolean)
        case _:
            raise BaseError(f"Could not parse boolean value: {value}")


def transform_date(input_value: InputTypes) -> Date:
    """Transform a date string into a date object."""
    val = assert_is_string(input_value)
    return parse_date_string(val)


def transform_interval(input_value: InputTypes) -> Interval:
    """Transform a sting input into an interval object."""
    val = assert_is_string(input_value)
    start, end = val.split(":", 1)
    return Interval(transform_xsd_decimal(start.strip()), transform_xsd_decimal(end.strip()))


def transform_xsd_string(value: InputTypes) -> Literal:
    """Transform a value into an rdflib Literal with datatype xsd:string"""
    str_val = assert_is_string(value)
    return Literal(str_val, datatype=XSD.string)


def transform_xsd_decimal(value: InputTypes) -> Literal:
    """Transform a value into an rdflib Literal with datatype xsd:decimal"""
    str_val = assert_is_string(value)
    return Literal(str(float(str_val)), datatype=XSD.decimal)


def transform_xsd_integer(value: InputTypes) -> Literal:
    """Transform a value into an rdflib Literal with datatype xsd:integer"""
    str_val = assert_is_string(value)
    return Literal(str_val, datatype=XSD.integer)


def transform_xsd_date_time(value: InputTypes) -> Literal:
    """Transform a value into an rdflib Literal with datatype xsd:dateTimeStamp"""
    str_val = assert_is_string(value)
    return Literal(str_val, datatype=XSD.dateTimeStamp)


def transform_xsd_any_uri(value: InputTypes) -> Literal:
    """Transform a value into an rdflib Literal with datatype xsd:anyURI"""
    str_val = assert_is_string(value)
    return Literal(str_val, datatype=XSD.anyURI)


def transform_geometry(value: InputTypes) -> Literal:
    """Transform a value into a geometry string rdflib Literal with datatype xsd:string"""
    str_val = assert_is_string(value)
    try:
        str_val = json.dumps(json.loads(str_val))
        return Literal(str_val, datatype=XSD.string)
    except JSONDecodeError:
        raise BaseError(f"Could not parse json value: {value}") from None


def assert_is_string(value: str | FormattedTextValue) -> str:
    """Assert a value is a string."""
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise BaseError(f"Expected string value, but got XML value: {xml.as_xml()}")
        case _:
            assert_never(value)


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
