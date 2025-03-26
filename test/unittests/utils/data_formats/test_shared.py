from typing import Union

import numpy as np
import pandas as pd
import pytest

from dsp_tools.commands.excel2xml.propertyelement import PropertyElement
from dsp_tools.utils.data_formats import shared


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
