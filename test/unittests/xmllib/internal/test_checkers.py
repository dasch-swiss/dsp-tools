# mypy: disable-error-code="method-assign,no-untyped-def"

import warnings

import numpy as np
import pandas as pd
import pytest
import regex

from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.internal.checkers import check_and_inform_about_angular_brackets
from dsp_tools.xmllib.internal.checkers import check_and_warn_potentially_empty_string


@pytest.mark.parametrize("in_val", ["string", 2, False])
def test_check_and_warn_potentially_empty_string_good(in_val):
    with warnings.catch_warnings(record=True) as caught_warnings:
        check_and_warn_potentially_empty_string(value=in_val, res_id="res", expected="input")
    assert len(caught_warnings) == 0


@pytest.mark.parametrize("in_val", ["  ", pd.NA, None])
def test_check_and_warn_potentially_empty_string_empty(in_val):
    expected = regex.escape(rf"Your input '{in_val}' is empty. Please enter a valid input.")
    with pytest.warns(XmllibInputWarning, match=expected):
        check_and_warn_potentially_empty_string(value=in_val, res_id="res", expected="input")


@pytest.mark.parametrize(
    ("in_val", "type_for_message"), [(str(pd.NA), "pd.NA"), (str(np.nan), "np.nan"), (str(None), "None")]
)
def test_check_and_warn_potentially_empty_string_potentially_empty(in_val, type_for_message):
    expected = regex.escape(
        rf"Your input '{in_val}' is a string but may be the result of `str({type_for_message})`. "
        r"Please verify that the input is as expected."
    )
    with pytest.warns(XmllibInputInfo, match=expected):
        check_and_warn_potentially_empty_string(value=in_val, res_id="res", expected="input")


@pytest.mark.parametrize(
    "allowed_values",
    [
        "(<2cm) (>10cm)",
        "text < text/>",
        "text < text> & text",
        "text <text text > text",
        'text < text text="text"> text',
        'text <text text="text" > text',
    ],
)
def test_check_and_inform_about_angular_brackets_good(allowed_values, recwarn: pytest.WarningsRecorder):
    check_and_inform_about_angular_brackets(allowed_values, "id", "prp")
    assert len(recwarn) == 0


@pytest.mark.parametrize("in_val", ["text <tag> text", "text <p>paragraph</p> text"])
def test_check_and_inform_about_angular_brackets_informs(in_val):
    expected = regex.escape(
        rf"Your input '{in_val}' contains angular brackets. "
        r"Since this is a simpletext, please note that these will not be recognised as formatting "
        r"in the text field, but will be displayed as-is."
    )
    with pytest.warns(XmllibInputInfo, match=expected):
        check_and_inform_about_angular_brackets(in_val, "id", "prp")
