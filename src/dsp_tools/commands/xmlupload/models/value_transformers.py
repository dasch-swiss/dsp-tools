from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from typing import TypeAlias

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseColor
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseDate
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseDecimal
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseGeometry
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseGeoname
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseTime
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseURI
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import ValueTypes
from dsp_tools.commands.xmlupload.resource_create_client import assert_is_string
from dsp_tools.utils.date_util import Date
from dsp_tools.utils.date_util import parse_date_string

InputTypes: TypeAlias = str | FormattedTextValue
OutputTypes: TypeAlias = str | Date
ValueSerialiser: TypeAlias = Callable[[ValueTypes, str | None, str | None], SerialiseValue]
ValueTransformer: TypeAlias = Callable[[InputTypes], OutputTypes]


@dataclass
class TransformationSteps:
    serialiser: ValueSerialiser
    transformer: ValueTransformer


def transform_date(input_value: InputTypes) -> OutputTypes:
    val = assert_is_string(input_value)
    return parse_date_string(val)


def transform_decimal(input_value: InputTypes) -> OutputTypes:
    val = assert_is_string(input_value)
    return str(float(val))


def transform_geometry(input_value: InputTypes) -> OutputTypes:
    val = assert_is_string(input_value)
    return json.dumps(json.loads(val))


def transform_string(input_value: InputTypes) -> OutputTypes:
    return assert_is_string(input_value)


str_value_to_transformation_steps_mapper = {
    "color": TransformationSteps(SerialiseColor, transform_string),
    "date": TransformationSteps(SerialiseDate, transform_date),
    "decimal": TransformationSteps(SerialiseDecimal, transform_decimal),
    "geometry": TransformationSteps(SerialiseGeometry, transform_geometry),
    "geoname": TransformationSteps(SerialiseGeoname, transform_string),
    "time": TransformationSteps(SerialiseTime, transform_string),
    "uri": TransformationSteps(SerialiseURI, transform_string),
}
