# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest
import regex

from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import assert_is_string
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import assert_is_tuple
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_boolean
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_date
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_decimal
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_geometry
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_integer
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_interval
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_simpletext
from dsp_tools.error.exceptions import InputError


def test_assert_is_string_good():
    result = assert_is_string("string")
    assert isinstance(result, str)
    assert result == "string"


@pytest.mark.parametrize(
    ("in_val", "expected"),
    [
        ("     ", r"sdf"),
        (("1", 2), r"dsf"),
    ],
)
def test_assert_is_string_raises(in_val, expected):
    with pytest.raises(InputError, match=regex.escape(expected)):
        assert_is_string(in_val)


def test_assert_is_tuple_good():
    result = assert_is_tuple(("1", "2"))
    assert isinstance(result, tuple)
    assert result == ("1", "2")


@pytest.mark.parametrize(("in_val", "expected"), [(("1", "2", "3"), r"dfsa"), ("string", r"sdf")])
def test_assert_is_tuple_raises(in_val, expected):
    with pytest.raises(InputError, match=regex.escape(expected)):
        assert_is_tuple(in_val)


@pytest.mark.parametrize(
    ("in_val", "expected"),
    [
        ("true", True),
        ("1", True),
        ("True", True),
        (1, True),
        ("false", False),
        ("False", False),
        ("0", False),
        (0, False),
    ],
)
def test_transform_boolean_good(in_val, expected):
    assert transform_boolean(in_val) == expected


def test_transform_boolean_raises():
    msg = regex.escape(r"")
    with pytest.raises(InputError, match=msg):
        transform_boolean("other")


def test_transform_date_good():
    result = transform_date("JULIAN:BC:1:AD:200")
    assert not result


@pytest.mark.parametrize(
    ("in_val", "expected"),
    [
        ("1", 1.0),
        ("1.88", 1.88),
    ],
)
def test_transform_decimal_good(in_val, expected):
    assert transform_decimal(in_val) == expected


def test_transform_integer_good():
    assert transform_integer("1") == 1


@pytest.mark.parametrize(
    ("in_val", "start", "end"),
    [
        (("0", "1"), 0.0, 1.0),
        (("0.3", "1.3"), 0.3, 1.3),
    ],
)
def test_transform_interval_good(in_val, start, end):
    result = transform_interval(in_val)
    assert result.start == start
    assert result.end == end


def test_transform_interval_raises():
    msg = regex.escape(r"")
    with pytest.raises(InputError, match=msg):
        transform_interval(("", "1"))


def test_transform_geometry_good():
    geom_str = """
                {
                    "status": "active",
                    "type": "polygon",
                    "lineWidth": 5,
                    "points": [{"x": 0.4, "y": 0.6},
                               {"x": 0.5, "y": 0.9},
                               {"x": 0.8, "y": 0.9},
                               {"x": 0.7, "y": 0.6}]
                }
                """
    expected = "sadf"
    assert transform_geometry(geom_str) == expected


def test_transform_geometry_raises():
    msg = regex.escape(r"")
    with pytest.raises(InputError, match=msg):
        transform_geometry("not valid")


def test_transform_simpletext_good():
    text = """
    Text line 1

            line 2  
    Third line ...
    
    """
    expected = """fdsadfsa"""
    assert transform_simpletext(text) == expected


def test_transform_simpletext_raises():
    msg = regex.escape(r"")
    with pytest.raises(InputError, match=msg):
        transform_simpletext("      ")
