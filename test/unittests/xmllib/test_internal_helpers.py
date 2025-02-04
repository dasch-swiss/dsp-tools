
import pytest

from dsp_tools.xmllib.internal_helpers import escape_reserved_xml_chars


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        ("Text no escape", "Text no escape"),
        ("allowed tag <allowed>content</allowed>", "allowed tag <allowed>content</allowed>"),
        ("Ampersand &", "Ampersand &amp;"),
        ("Unknow tags <unknonw></unknonw>", "Unknow tags &lt;unknonw&gt;&lt;/unknonw&gt;"),
        ("<text om brackets>", "&lt;text in brackets&gt;"),
    ],
)
def test_escape_reserved_xml_chars(input_val: str, expected: str) -> None:
    result = escape_reserved_xml_chars(input_val, ["allowed"])
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
