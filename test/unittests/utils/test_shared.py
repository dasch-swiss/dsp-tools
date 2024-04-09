from typing import Union

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2xml.propertyelement import PropertyElement
from dsp_tools.utils import shared


def test_prepare_dataframe() -> None:
    original_df = pd.DataFrame(
        {
            "  TitLE of Column 1 ": ["1", " 0-1 ", "1-n ", pd.NA, "    ", " ", "", " 0-n ", pd.NA],
            " Title of Column 2 ": [None, "1", 1, "text", "text", "text", "text", "text", "text"],
            "Title of Column 3": ["", pd.NA, None, "text", "text", "text", "text", pd.NA, "text"],
        }
    )
    expected_df = pd.DataFrame(
        {
            "title of column 1": ["0-1", "1-n", "0-n"],
            "title of column 2": ["1", "1", "text"],
            "title of column 3": [pd.NA, pd.NA, pd.NA],
        },
        index=[1, 2, 7],
    )
    returned_df = shared.prepare_dataframe(
        df=original_df, required_columns=["  TitLE of Column 1 ", " Title of Column 2 "], location_of_sheet=""
    )
    assert_frame_equal(returned_df, expected_df)


def test_check_notna_good() -> None:
    na_values = [
        None,
        pd.NA,
        pd.NA,
        "",
        "  ",
        "-",
        ",",
        ".",
        "*",
        " ⳰",
        " ῀ ",  # noqa: RUF001 (ambiguous-unicode-character-string)
        " ῾ ",  # noqa: RUF001 (ambiguous-unicode-character-string)
        " \n\t ",
        "N/A",
        "n/a",
        "<NA>",
        "None",
        ["a", "b"],
        pd.array(["a", "b"]),
        np.array([0, 1]),
    ]
    for na_value in na_values:
        assert not shared.check_notna(na_value), f"Failed na_value: {na_value}"


def test_check_notna_problem() -> None:
    notna_values_orig: list[Union[str, int, float, bool]] = [
        1,
        0.1,
        True,
        False,
        "True",
        "False",
        r" \n\t ",
        "0",
        "_",
        "Ὅμηρος",
        "!",
        "?",
    ]
    notna_values_as_propelem = [PropertyElement(x) for x in notna_values_orig]
    for notna_value in notna_values_orig + notna_values_as_propelem:
        assert shared.check_notna(notna_value), f"Failed notna_value: {notna_value}"


if __name__ == "__main__":
    pytest.main([__file__])
