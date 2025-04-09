import pytest

from dsp_tools.xmllib.internal_helpers import like_string


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (" \u200B ", True),  # zero-width space
        (" \uFEFF ", True),  # Zero-Width No-Break Space
        ("", False),
        (" ", False),
        (" \t ", False),
        (" \n ", False),
        (" \r ", False),
        (" \v ", False),  # vertical tab
        (" \u00A0 ", False),  # non-breaking space
        (" \f\r\t\n\v \u00A0 ", False),
    ],
)
def test_like_string(text: str, expected: bool) -> None:
    assert like_string(text) == expected
