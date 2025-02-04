from typing import Any

import pandas as pd
import pytest

from dsp_tools.xmllib.internal_helpers import is_string_like


@pytest.mark.parametrize("val", ["a", "None", "-", "1", "\n1", "עִבְרִית", "اَلْعَرَبِيَّةُ", "hello world"])
def test_is_string_correct(val: Any) -> None:
    assert is_string_like(val)


@pytest.mark.parametrize("val", [None, pd.NA, "", " ", "\t \n"])
def test_is_string_wrong(val: Any) -> None:
    assert not is_string_like(val)
