from typing import Any

import pytest
import regex
from rdflib import XSD
from rdflib import Literal

from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_geometry
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_interval
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_boolean
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_decimal
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_integer
from dsp_tools.commands.xmlupload.models.rdf_models import Interval
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


def test_transform_geometry_success() -> None:
    test_geom = """
    {
        "status": "active",
        "type": "polygon",
        "lineWidth": 5,
        "points": []
    }
    """
    result = transform_geometry(test_geom)
    expected = '{"status": "active", "type": "polygon", "lineWidth": 5, "points": []}'
    assert result == Literal(expected, datatype=XSD.string)


def test_transform_geometry_raises() -> None:
    value = ' { "status": "active",'
    msg = regex.escape(f"Could not parse json value: {value}")
    with pytest.raises(BaseError, match=msg):
        transform_geometry(value)
