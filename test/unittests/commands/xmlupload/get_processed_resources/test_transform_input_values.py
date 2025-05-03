# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest
import regex

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import assert_is_string
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import assert_is_tuple
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_boolean
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_date
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_decimal
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_geometry
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_integer
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_richtext
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_simpletext
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.data_formats.date_util import Calendar
from dsp_tools.utils.data_formats.date_util import Date
from dsp_tools.utils.data_formats.date_util import Era
from dsp_tools.utils.data_formats.date_util import SingleDate


def test_assert_is_string_good():
    result = assert_is_string("string")
    assert isinstance(result, str)
    assert result == "string"


def test_assert_is_string_raises():
    expected = r"Expected string value, but got tuple value: ('1', '2')"
    with pytest.raises(InputError, match=regex.escape(expected)):
        assert_is_string(("1", "2"))


def test_assert_is_tuple_good():
    result = assert_is_tuple(("1", "2"))
    assert isinstance(result, tuple)
    assert result == ("1", "2")


@pytest.mark.parametrize(
    ("in_val", "expected"),
    [
        (("1", "2", "3"), r"Expected tuple with two elements but got ('1', '2', '3')"),
        ("string", r"Expected tuple value, but got string value: string"),
    ],
)
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
    msg = regex.escape(r"Could not parse boolean value: other")
    with pytest.raises(InputError, match=msg):
        transform_boolean("other")


def test_transform_date_good():
    result = transform_date("2022")
    assert isinstance(result, Date)
    assert result.calendar == Calendar.GREGORIAN
    assert result.start.era == Era.CE
    assert result.start.year == 2022
    assert not result.start.month
    assert not result.start.day
    end_date = result.end
    assert isinstance(end_date, SingleDate)
    assert end_date.era == Era.CE
    assert end_date.year == 2022
    assert not end_date.month
    assert not end_date.day


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
    expected = (
        '{"status": "active", "type": "polygon", "lineWidth": 5, "points": '
        '[{"x": 0.4, "y": 0.6}, {"x": 0.5, "y": 0.9}, {"x": 0.8, "y": 0.9}, {"x": 0.7, "y": 0.6}]}'
    )
    assert transform_geometry(geom_str) == expected


def test_transform_geometry_raises():
    msg = regex.escape(r"Could not parse json value: not valid")
    with pytest.raises(InputError, match=msg):
        transform_geometry("not valid")


def test_transform_simpletext_good():
    assert transform_simpletext("text") == "text"


def test_transform_simpletext_raises():
    msg = regex.escape(r"After removing redundant whitespaces and newlines the input string is empty.")
    with pytest.raises(InputError, match=msg):
        transform_simpletext("")


def test_transform_richtext_good():
    expected = "This is <em>italicized and <strong>bold</strong></em> text!"
    result = transform_richtext(expected)
    assert isinstance(result, FormattedTextValue)
    assert result.xmlstr == expected


def test_transform_richtext_raises():
    msg = regex.escape(r"After removing redundant whitespaces and newlines the input string is empty.")
    with pytest.raises(InputError, match=msg):
        transform_richtext("")
