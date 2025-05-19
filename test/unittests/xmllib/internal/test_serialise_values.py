# mypy: disable-error-code="no-untyped-def"
import os
from unittest import mock

import pytest
from lxml import etree

from dsp_tools.xmllib.internal.serialise_values import _sort_and_group_values
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


@pytest.fixture
def mixed_values() -> list[Value]:
    return [
        BooleanValue("false", ":bool"),
        LinkValue("b", ":link"),
        IntValue("2", ":int"),
        LinkValue("a", ":link"),
        IntValue("1", ":int"),
        SimpleText("a", ":text1"),
        SimpleText("b", ":text2"),
    ]


EXPECTED_TYPE_LOOKUP = {
    ":bool": "boolean",
    ":int": "integer",
    ":text1": "simpletext",
    ":text2": "simpletext",
    ":link": "resptr",
}


class TestSortValue:
    def test_no_sorting(self, mixed_values):
        result_tups, type_lookup = _sort_and_group_values(mixed_values)
        assert type_lookup == EXPECTED_TYPE_LOOKUP
        expected_props = {x.prop_name for x in mixed_values}
        actual_props = {x[0] for x in result_tups}
        assert len(result_tups) == len(expected_props)
        assert expected_props == actual_props

    @mock.patch.dict(os.environ, {"XMLLIB_SORT_PROPERTIES": "true"})
    def test_with_sorting(self, mixed_values):
        result_tups, type_lookup = _sort_and_group_values(mixed_values)
        assert type_lookup == EXPECTED_TYPE_LOOKUP
        expected_prop_order = [":bool", ":int", ":link", ":text1", ":text2"]
        result_order = [x[0] for x in result_tups]
        assert result_order == expected_prop_order
        bool_val = result_tups[0][1]
        assert len(bool_val) == 1
        int_val = result_tups[1][1]
        assert len(int_val) == 2
        assert int_val[0].value == "1"
        assert int_val[1].value == "2"
        link_val = result_tups[2][1]
        assert len(link_val) == 2
        assert link_val[0].value == "a"
        assert link_val[1].value == "b"
        text_1 = result_tups[3][1]
        assert len(text_1) == 1
        text_2 = result_tups[4][1]
        assert len(text_2) == 1


class TestSerialiseValues:
    def test_boolean(self):
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

    def test_color(self):
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

    def test_date(self):
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

    def test_decimal(self):
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

    def test_geoname(self):
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

    def test_int(self):
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

    def test_link(self):
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

    def test_list(self):
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
    def test_richtext_tags(self, orig: str, expected: str):
        result = serialise_values([Richtext(orig, ":richtextProp")])
        assert len(result) == 1
        expected_xml = (
            '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'name=":richtextProp">'
            f'<text encoding="xml">{expected}</text></text-prop>'
        )
        res_str = etree.tostring(result.pop(0), encoding="unicode")
        assert res_str == expected_xml

    def test_simpletext(self):
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

    def test_simpletext_escapes(self):
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

    def test_time(self):
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

    def test_uri(self):
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

    def test_value_with_default_permission(self):
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

    def test_several_values_different_generic_property(self):
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

    def test_several_values_different_property(self):
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

    def test_several_values_same_property(self):
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
