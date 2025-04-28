# mypy: disable-error-code="method-assign,no-untyped-def"
import warnings

import numpy as np
import pandas as pd
import pytest
import regex

from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.internal_helpers import check_and_warn_potentially_empty_string
from dsp_tools.xmllib.internal_helpers import numeric_entities


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        ("a &nbsp; a", "a &#160; a"),
        ("a &#160; a", "a &#160; a"),
        ("a &#x22; a", "a &#x22; a"),
        ("a &quot; &amp; &apos; &lt; &gt; a", "a &quot; &amp; &apos; &lt; &gt; a"),
        ("aäö&;", "aäö&;"),
    ],
)
def test_numeric_entities(original: str, expected: str) -> None:
    assert numeric_entities(original) == expected


@pytest.mark.parametrize("in_val", ["string", 2, False])
def test_check_and_warn_potentially_empty_string_good(in_val):
    with warnings.catch_warnings(record=True) as caught_warnings:
        check_and_warn_potentially_empty_string(in_val, "res")
    assert len(caught_warnings) == 0


@pytest.mark.parametrize("in_val", ["  ", pd.NA, None])
def test_check_and_warn_potentially_empty_string_empty(in_val):
    expected = regex.escape("asdf")
    with pytest.warns(XmllibInputWarning, match=expected):
        check_and_warn_potentially_empty_string(in_val, "res")


@pytest.mark.parametrize("in_val", [str(pd.NA), str(np.nan), str(None)])
def test_check_and_warn_potentially_empty_string_potentially_empty(in_val):
    expected = regex.escape(rf"asdf {in_val}")
    with pytest.warns(XmllibInputInfo, match=expected):
        check_and_warn_potentially_empty_string(in_val, "res")
