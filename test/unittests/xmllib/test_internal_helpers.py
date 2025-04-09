import pytest

from dsp_tools.xmllib.internal_helpers import is_nonempty_value_internal


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (" \u200b ", False),  # zero-width space
        (" \ufeff ", False),  # Zero-Width No-Break Space
        ("", False),
        (" ", False),
        (" \t ", False),
        (" \n ", False),
        (" \r ", False),
        (" \v ", False),  # vertical tab
        (" \u00a0 ", False),  # non-breaking space
        (" \f\r\t\n\v \u00a0 ", False),
    ],
)
def test_is_nonempty_value_internal(text: str, expected: bool) -> None:
    assert is_nonempty_value_internal(text) == expected
