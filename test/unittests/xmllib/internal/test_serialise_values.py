import pytest
from lxml import etree

from dsp_tools.xmllib.internal.serialise_values import serialise_values
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.internal.values import BooleanValue
from dsp_tools.xmllib.models.internal.values import ColorValue
from dsp_tools.xmllib.models.internal.values import DateValue
from dsp_tools.xmllib.models.internal.values import DecimalValue
from dsp_tools.xmllib.models.internal.values import GeonameValue
from dsp_tools.xmllib.models.internal.values import IntValue
from dsp_tools.xmllib.models.internal.values import LinkValue
from dsp_tools.xmllib.models.internal.values import ListValue
from dsp_tools.xmllib.models.internal.values import Richtext
from dsp_tools.xmllib.models.internal.values import SimpleText
from dsp_tools.xmllib.models.internal.values import TimeValue
from dsp_tools.xmllib.models.internal.values import UriValue
from dsp_tools.xmllib.models.internal.values import Value


def test_boolean() -> None:
    v: list[Value] = [
        BooleanValue.new("0", ":booleanProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)
    ]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<boolean-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":booleanProp">'
        b'<boolean permissions="open">false</boolean>'
        b"</boolean-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_color() -> None:
    v: list[Value] = [ColorValue("#000000", ":colorProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<color-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":colorProp">'
        b'<color permissions="open">#000000</color>'
        b"</color-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_date() -> None:
    v: list[Value] = [DateValue("2023-01-01", ":dateProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<date-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":dateProp">'
        b'<date permissions="open">2023-01-01</date>'
        b"</date-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_decimal() -> None:
    v: list[Value] = [DecimalValue("3.14", ":decimalProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<decimal-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":decimalProp">'
        b'<decimal permissions="open">3.14</decimal>'
        b"</decimal-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_geoname() -> None:
    v: list[Value] = [GeonameValue("99", ":geonameProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<geoname-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":geonameProp">'
        b'<geoname permissions="open">99</geoname>'
        b"</geoname-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_int() -> None:
    v: list[Value] = [IntValue("42", ":intProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<integer-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":intProp">'
        b'<integer permissions="open">42</integer>'
        b"</integer-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_link() -> None:
    v: list[Value] = [LinkValue("res_link", ":linkProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<resptr-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":linkProp">'
        b'<resptr permissions="open">res_link</resptr>'
        b"</resptr-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_list() -> None:
    v: list[Value] = [ListValue("item1", "listName", ":listProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<list-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":listProp" list="listName">'
        b'<list permissions="open">item1</list>'
        b"</list-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


@pytest.mark.parametrize(
    ("orig", "expected"),
    [
        (
            "<strong>standard standoff tag</strong><unsupported>Hello World</unsupported>",
            "<strong>standard standoff tag</strong>&lt;unsupported&gt;Hello World&lt;/unsupported&gt;",
        ),
        ("&amp; &lt; &gt;", "&amp; &lt; &gt;"),
        ("'uuas\\. 11` \\a\\ i! 1 ?7 Rinne   \\Rinne", "'uuas\\. 11` \\a\\ i! 1 ?7 Rinne   \\Rinne"),
        ("1 < 2 & 4 > 3", "1 &lt; 2 &amp; 4 &gt; 3"),
    ],
)
def test_richtext_tags(orig: str, expected: str) -> None:
    result = serialise_values([Richtext(orig, ":richtextProp")])
    assert len(result) == 1
    expected_xml = (
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":richtextProp">'
        f'<text encoding="xml">{expected}</text></text-prop>'
    )
    res_str = etree.tostring(result.pop(0), encoding="unicode")
    assert res_str == expected_xml


def test_simpletext() -> None:
    v: list[Value] = [SimpleText("Hello World", ":simpleTextProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<text-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":simpleTextProp">'
        b'<text permissions="open" encoding="utf8">Hello World</text>'
        b"</text-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_simpletext_escapes() -> None:
    original = "'uuas\\. 11` \\a\\ i! 1 ?7 Rinne   \\Rinne"
    expected = "'uuas\\. 11` \\a\\ i! 1 ?7 Rinne   \\Rinne"
    result = serialise_values([SimpleText(original, ":simpleTextProp")])
    assert len(result) == 1
    expected_xml = (
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":simpleTextProp">'
        f'<text encoding="utf8">{expected}</text></text-prop>'
    )
    res_str = str(etree.tostring(result.pop(0)), encoding="utf-8")
    assert res_str == expected_xml


def test_time() -> None:
    v: list[Value] = [TimeValue("2009-10-10T12:00:00-05:00", ":timeProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<time-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":timeProp">'
        b'<time permissions="open">2009-10-10T12:00:00-05:00</time>'
        b"</time-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_uri() -> None:
    v: list[Value] = [UriValue("https://example.com", ":uriProp", permissions=Permissions.OPEN)]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<uri-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":uriProp">'
        b'<uri permissions="open">https://example.com</uri>'
        b"</uri-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_value_with_default_permission() -> None:
    v: list[Value] = [BooleanValue("false", ":booleanProp")]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<boolean-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":booleanProp">'
        b"<boolean>false</boolean>"
        b"</boolean-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_several_values_different_generic_property() -> None:
    v: list[Value] = [
        LinkValue("res_link", ":linkProp"),
        SimpleText("Hello World", ":simpleTextProp"),
    ]
    result = serialise_values(v)
    assert len(result) == 2
    expected = (
        b"<resptr-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":linkProp"><resptr>res_link</resptr>'
        b"</resptr-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected
    expected = (
        b"<text-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":simpleTextProp">'
        b'<text encoding="utf8">Hello World</text>'
        b"</text-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_several_values_different_property() -> None:
    v: list[Value] = [
        BooleanValue("false", ":booleanProp"),
        LinkValue("res_link", ":linkProp"),
    ]
    result = serialise_values(v)
    assert len(result) == 2
    expected = (
        b'<boolean-prop xmlns="https://dasch.swiss/schema" '
        b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":booleanProp">'
        b"<boolean>false</boolean>"
        b"</boolean-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected
    expected = (
        b"<resptr-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":linkProp">'
        b"<resptr>res_link</resptr>"
        b"</resptr-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_several_values_same_property() -> None:
    v: list[Value] = [
        LinkValue("open_permission", ":linkProp", permissions=Permissions.OPEN),
        LinkValue("default_permission", ":linkProp"),
    ]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b'<resptr-prop xmlns="https://dasch.swiss/schema" '
        b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":linkProp">'
        b'<resptr permissions="open">open_permission</resptr>'
        b"<resptr>default_permission</resptr>"
        b"</resptr-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


if __name__ == "__main__":
    pytest.main([__file__])
