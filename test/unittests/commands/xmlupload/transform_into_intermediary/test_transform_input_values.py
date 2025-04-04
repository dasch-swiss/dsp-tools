import pytest
import regex

from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_boolean
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_date
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_decimal
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_geometry
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_integer
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_interval
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_simpletext
from dsp_tools.error.exceptions import InputError


@pytest.mark.parametrize(
    ("in_val", "expected"),
    [
        ("", ""),
    ],
)
def test_transform_boolean_good(in_val, expected):
    assert transform_boolean(in_val) == expected


def test_transform_boolean_raises():
    msg = regex.escape(r"")
    with pytest.raises(InputError, match=msg):
        pass


def test_transform_date_good(in_val, expected):
    assert transform_date(in_val) == expected


def test_transform_decimal_good(in_val, expected):
    assert transform_decimal(in_val) == expected


def test_transform_integer_good(in_val, expected):
    assert transform_integer(in_val) == expected


@pytest.mark.parametrize(
    ("in_val", "expected"),
    [
        ("", ""),
    ],
)
def test_transform_interval_good(in_val, expected):
    assert transform_interval(in_val) == expected


def test_transform_interval_raises():
    msg = regex.escape(r"")
    with pytest.raises(InputError, match=msg):
        pass


def test_transform_geometry_good(in_val, expected):
    assert transform_geometry(in_val) == expected


def test_transform_geometry_raises():
    msg = regex.escape(r"")
    with pytest.raises(InputError, match=msg):
        pass


@pytest.mark.parametrize(
    ("in_val", "expected"),
    [
        ("", ""),
    ],
)
def test_transform_simpletext_good(in_val, expected):
    assert transform_simpletext(in_val) == expected


def test_transform_simpletext_raises():
    msg = regex.escape(r"")
    with pytest.raises(InputError, match=msg):
        pass
