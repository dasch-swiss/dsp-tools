import numpy as np
import pandas as pd
import pytest

from dsp_tools.xmllib.internal_helpers import is_nonempty_value_internal


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (np.nan, False),
        (pd.NA, False),
        (None, False),
        ("", False),
        (" ", False),
        (" \t ", False),
        (" \n ", False),
        (" \r ", False),
        (" \v ", False),  # vertical tab
        (" \f ", False),
        (" \u00a0 ", False),  # non-breaking space
        (" \u200b ", False),  # zero-width space
        (" \ufeff ", False),  # Zero-Width No-Break Space
        (" \t\n\r\v\f \u00a0 \u200b \ufeff", False),
        ("a", True),
        (0, True),
        (1, True),
        ("0", True),
        ("1", True),
        (True, True),
        (False, True),
    ],
)
def test_is_nonempty_value_internal(text: str, expected: bool) -> None:
    assert is_nonempty_value_internal(text) == expected
