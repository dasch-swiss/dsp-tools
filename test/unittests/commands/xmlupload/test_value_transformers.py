from typing import Any

import pytest
from rdflib import XSD
from rdflib import Literal

from dsp_tools.commands.xmlupload.models.serialise.serialise_rdf_value import Interval
from dsp_tools.commands.xmlupload.value_transformers import transform_interval
from dsp_tools.commands.xmlupload.value_transformers import transform_xsd_boolean
from dsp_tools.commands.xmlupload.value_transformers import transform_xsd_decimal
from dsp_tools.commands.xmlupload.value_transformers import transform_xsd_integer
from dsp_tools.models.exceptions import BaseError


@pytest.mark.parametrize(
    ("input_bool", "out_bool"),
    [
        ("true", True),
        ("True", True),
        ("1", True),
        (1, True),
        (True, True),
        ("false", False),
        ("False", False),
        ("0", False),
        (0, False),
        (False, False),
    ],
)
def test_transform_boolean_success(input_bool: Any, out_bool: bool) -> None:
    result = transform_xsd_boolean(input_bool)
    assert result == Literal(out_bool, datatype=XSD.boolean)


def test_transform_boolean_raises_string() -> None:
    with pytest.raises(BaseError):
        transform_xsd_boolean("foo")


def test_transform_boolean_raises_int() -> None:
    with pytest.raises(BaseError):
        transform_xsd_boolean(2)  # type: ignore[arg-type]


def test_transform_xsd_decimal_int() -> None:
    result = transform_xsd_decimal("1")
    assert result == Literal("1.0", datatype=XSD.decimal)


def test_transform_xsd_decimal_decimal() -> None:
    result = transform_xsd_decimal("1.1")
    assert result == Literal("1.1", datatype=XSD.decimal)


def test_transform_interval_success() -> None:
    result = transform_interval("1:2")
    assert isinstance(result, Interval)
    assert result.start == Literal("1.0", datatype=XSD.decimal)
    assert result.end == Literal("2.0", datatype=XSD.decimal)


def test_transform_interval_success_with_space() -> None:
    result = transform_interval("1:2.1 ")
    assert isinstance(result, Interval)
    assert result.start == Literal("1.0", datatype=XSD.decimal)
    assert result.end == Literal("2.1", datatype=XSD.decimal)


def test_transform_xsd_integer_success() -> None:
    result = transform_xsd_integer("1")
    assert result == Literal(1, datatype=XSD.integer)
