import pytest
from lxml import etree

from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.values import BooleanValue
from dsp_tools.xmllib.models.values import ColorValue
from dsp_tools.xmllib.models.values import DateValue
from dsp_tools.xmllib.models.values import DecimalValue
from dsp_tools.xmllib.models.values import GeonameValue
from dsp_tools.xmllib.models.values import IntValue
from dsp_tools.xmllib.models.values import LinkValue
from dsp_tools.xmllib.models.values import ListValue
from dsp_tools.xmllib.models.values import Richtext
from dsp_tools.xmllib.models.values import SimpleText
from dsp_tools.xmllib.models.values import TimeValue
from dsp_tools.xmllib.models.values import UriValue
from dsp_tools.xmllib.models.values import Value
from dsp_tools.xmllib.serialise.serialise_values import serialise_values


def test_boolean() -> None:
    v: list[Value] = [BooleanValue("0", ":booleanProp", resource_id="res_id", permissions=Permissions.OPEN)]
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
    v: list[Value] = [ColorValue("#000000", ":colorProp", resource_id="res_id", permissions=Permissions.OPEN)]
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
    v: list[Value] = [DateValue("2023-01-01", ":dateProp", resource_id="res_id", permissions=Permissions.OPEN)]
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
    v: list[Value] = [DecimalValue("3.14", ":decimalProp", resource_id="res_id", permissions=Permissions.OPEN)]
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
    v: list[Value] = [GeonameValue("99", ":geonameProp", resource_id="res_id", permissions=Permissions.OPEN)]
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
    v: list[Value] = [IntValue("42", ":intProp", resource_id="res_id", permissions=Permissions.OPEN)]
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
    v: list[Value] = [LinkValue("res_link", ":linkProp", resource_id="res_id", permissions=Permissions.OPEN)]
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
    v: list[Value] = [ListValue("item1", "listName", ":listProp", resource_id="res_id", permissions=Permissions.OPEN)]
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


def test_richtext() -> None:
    v: list[Value] = [
        Richtext(
            "<otherTag>Hello World</otherTag>", ":richtextProp", resource_id="res_id", permissions=Permissions.OPEN
        )
    ]
    result = serialise_values(v)
    assert len(result) == 1
    expected = (
        b"<text-prop "
        b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'name=":richtextProp">'
        b'<text permissions="open" encoding="xml">&lt;otherTag&gt;Hello World&lt;/otherTag&gt;</text>'
        b"</text-prop>"
    )
    res_str = etree.tostring(result.pop(0))
    assert res_str == expected


def test_simpletext() -> None:
    v: list[Value] = [SimpleText("Hello World", ":simpleTextProp", resource_id="res_id", permissions=Permissions.OPEN)]
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


def test_time() -> None:
    v: list[Value] = [
        TimeValue("2009-10-10T12:00:00-05:00", ":timeProp", resource_id="res_id", permissions=Permissions.OPEN)
    ]
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
    v: list[Value] = [UriValue("https://example.com", ":uriProp", resource_id="res_id", permissions=Permissions.OPEN)]
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
    v: list[Value] = [BooleanValue("0", ":booleanProp", resource_id="res_id")]
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
        LinkValue("res_link", ":linkProp", resource_id="res_id"),
        SimpleText("Hello World", ":simpleTextProp", resource_id="res_id"),
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
        BooleanValue("0", ":booleanProp", resource_id="res_id"),
        LinkValue("res_link", ":linkProp", resource_id="res_id"),
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
        LinkValue("open_permission", ":linkProp", resource_id="res_id", permissions=Permissions.OPEN),
        LinkValue("default_permission", ":linkProp", resource_id="res_id"),
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
