import warnings

import numpy as np
import pandas as pd
import pytest

from dsp_tools.xmllib.internal.exceptions import XmllibInputError
from dsp_tools.xmllib.internal.input_converters import check_and_fix_default_resource_authorship_input
from dsp_tools.xmllib.internal.input_converters import check_and_fix_is_non_empty_string
from dsp_tools.xmllib.internal.input_converters import check_and_fix_value_order
from dsp_tools.xmllib.internal.input_converters import numeric_entities
from dsp_tools.xmllib.internal.xmllib_warnings import XmllibInputInfo
from dsp_tools.xmllib.internal.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.models.config_options import ResourceAuthorshipDefault


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


class TestCheckAndFixInputOrder:
    def test_none_returns_none(self) -> None:
        assert check_and_fix_value_order(None, "prop", "res") is None

    @pytest.mark.parametrize(
        ("input_order", "expected"),
        [
            (1, 1),
            (42, 42),
            ("1", 1),
            ("42", 42),
        ],
    )
    def test_valid_inputs_return_int(self, input_order: int | float | str, expected: int) -> None:
        assert check_and_fix_value_order(input_order, "prop", "res") == expected

    @pytest.mark.parametrize(
        "input_order",
        [
            pd.NA,
            np.nan,
            True,
            False,
            "abc",
            "1.5",
            1.9,
        ],
    )
    def test_invalid_inputs_raise_error(self, input_order: object) -> None:
        with pytest.raises(XmllibInputError, match=type(input_order).__name__):
            check_and_fix_value_order(input_order, "prop", "res")


class TestCheckAndFixDefaultResourceAuthorship:
    def test_none_returns_none(self) -> None:
        assert check_and_fix_default_resource_authorship_input(None) is None

    def test_enum_member_returned_unchanged(self) -> None:
        result = check_and_fix_default_resource_authorship_input(ResourceAuthorshipDefault.PROJECT_DEFAULT)
        assert result is ResourceAuthorshipDefault.PROJECT_DEFAULT

    @pytest.mark.parametrize(
        ("authorship", "expected"),
        [
            (["Donald Duck", "Daisy Duck"], {"Daisy Duck", "Donald Duck"}),
            (("Donald Duck",), {"Donald Duck"}),
            ({"Donald Duck", "Daisy Duck"}, {"Daisy Duck", "Donald Duck"}),
            ("Donald Duck", {"Donald Duck"}),
        ],
    )
    def test_collection_of_strings_normalised(self, authorship: object, expected: set[str]) -> None:
        assert set(check_and_fix_default_resource_authorship_input(authorship)) == expected  # type: ignore[arg-type]

    def test_enum_class_raises(self) -> None:
        with pytest.raises(XmllibInputError, match="PROJECT_DEFAULT"):
            check_and_fix_default_resource_authorship_input(ResourceAuthorshipDefault)

    @pytest.mark.parametrize("authorship", [1, True, 1.5, {"key": "value"}])
    def test_invalid_type_raises(self, authorship: object) -> None:
        with pytest.raises(XmllibInputError, match=type(authorship).__name__):
            check_and_fix_default_resource_authorship_input(authorship)
