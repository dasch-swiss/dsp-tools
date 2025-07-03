# mypy: disable-error-code="method-assign,no-untyped-def"
import warnings

import numpy as np
import pandas as pd
import pytest

from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.internal.input_converters import check_and_fix_is_non_empty_string
from dsp_tools.xmllib.internal.input_converters import numeric_entities


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


@pytest.mark.parametrize(
    ("original", "expected"),
    [("Text", "Text"), (1, "1")],
)
def test_check_and_fix_is_non_empty_string_good(original: str, expected: str):
    with warnings.catch_warnings(record=True) as caught_warnings:
        result = check_and_fix_is_non_empty_string(original)
    assert len(caught_warnings) == 0
    assert result == expected


@pytest.mark.parametrize("original", [str(pd.NA), str(None)])
def test_check_and_fix_is_non_empty_string_info(original: str):
    with pytest.warns(XmllibInputInfo):
        result = check_and_fix_is_non_empty_string(original)
    assert result == original


@pytest.mark.parametrize("original", [pd.NA, np.nan, None, " ", ""])
def test_check_and_fix_is_non_empty_string_warns(original: str):
    with pytest.warns(XmllibInputWarning):
        result = check_and_fix_is_non_empty_string(original)
    assert result == ""
