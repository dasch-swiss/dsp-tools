from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from typing import TypeAlias
from typing import Union
from typing import assert_never

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import ValueSerialiser
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.date_util import Date
from dsp_tools.utils.date_util import parse_date_string

InputTypes: TypeAlias = Union[str, FormattedTextValue]
OutputTypes: TypeAlias = Union[str, Date]
ValueTransformer: TypeAlias = Callable[[InputTypes], OutputTypes]


@dataclass
class TransformationSteps:
    serialiser: ValueSerialiser
    transformer: ValueTransformer


def transform_date(input_value: InputTypes) -> Date:
    """Transform a date string into a date object."""
    val = _assert_is_string(input_value)
    return parse_date_string(val)


def transform_decimal(input_value: InputTypes) -> str:
    """Transform an input into a decimal in string format."""
    val = _assert_is_string(input_value)
    return str(float(val))


def transform_geometry(input_value: InputTypes) -> str:
    """Transform a geometry input into a string."""
    val = _assert_is_string(input_value)
    return json.dumps(json.loads(val))


def transform_string(input_value: InputTypes) -> str:
    """Assert that an input is of type string."""
    return _assert_is_string(input_value)


def _assert_is_string(value: str | FormattedTextValue) -> str:
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise BaseError(f"Expected string value, but got XML value: {xml.as_xml()}")
        case _:
            assert_never(value)
