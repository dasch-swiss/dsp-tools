# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest

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
