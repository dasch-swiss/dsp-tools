import pytest

from dsp_tools.xmllib.internal_helpers import is_nonempty_value_internal


@pytest.mark.parametrize(
    ("text", "expected"),
    [
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
    ],
)
def test_is_nonempty_value_internal(text: str, expected: bool) -> None:
    assert is_nonempty_value_internal(text) == expected
