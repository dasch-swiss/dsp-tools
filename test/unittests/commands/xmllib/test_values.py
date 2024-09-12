import warnings

import pytest
from lxml import etree

from dsp_tools.commands.xmllib.models.values import BooleanValue
from dsp_tools.commands.xmllib.models.values import ColorValue
from dsp_tools.commands.xmllib.models.values import DateValue
from dsp_tools.commands.xmllib.models.values import DecimalValue
from dsp_tools.commands.xmllib.models.values import GeonameValue
from dsp_tools.commands.xmllib.models.values import IntValue
from dsp_tools.commands.xmllib.models.values import LinkValue
from dsp_tools.commands.xmllib.models.values import ListValue
from dsp_tools.commands.xmllib.models.values import Richtext
from dsp_tools.commands.xmllib.models.values import SimpleText
from dsp_tools.commands.xmllib.models.values import TimeValue
from dsp_tools.commands.xmllib.models.values import UriValue
from dsp_tools.models.custom_warnings import DspToolsUserWarning


class TestBooleanValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            BooleanValue("False", ":booleanProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            BooleanValue("other", ":booleanProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = BooleanValue("0", ":booleanProp", resource_id="res_id")
        expected = (
            b'<boolean-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":booleanProp">'
            b'<boolean permissions="prop-default">false</boolean></boolean-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestColorValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ColorValue("#FFFFFF", ":colorProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            ColorValue("invalidColor", ":colorProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = ColorValue("#000000", ":colorProp", resource_id="res_id")
        expected = (
            b'<color-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":colorProp">'
            b'<color permissions="prop-default">#000000</color></color-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestDateValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DateValue("2023-01-01", ":dateProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            DateValue("invalidDate", ":dateProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = DateValue("2023-01-01", ":dateProp", resource_id="res_id")
        expected = (
            b'<date-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":dateProp">'
            b'<date permissions="prop-default">2023-01-01</date></date-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestDecimalValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DecimalValue("3.14", ":decimalProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            DecimalValue("invalidDecimal", ":decimalProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = DecimalValue("3.14", ":decimalProp", resource_id="res_id")
        expected = (
            b'<decimal-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":decimalProp">'
            b'<decimal permissions="prop-default">3.14</decimal></decimal-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestGeonameValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            GeonameValue("00099", ":geonameProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            GeonameValue("invalidGeoname", ":geonameProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = GeonameValue("99", ":geonameProp", resource_id="res_id")
        expected = (
            b'<geoname-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":geonameProp">'
            b'<geoname permissions="prop-default">99</geoname></geoname-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestIntValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            IntValue("42", ":intProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            IntValue("invalidInt", ":intProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = IntValue("42", ":intProp", resource_id="res_id")
        expected = (
            b'<integer-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":intProp">'
            b'<integer permissions="prop-default">42</integer></integer-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestLinkValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            LinkValue("link", ":linkProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            LinkValue(None, ":linkProp", resource_id="res_id")  # type: ignore[arg-type]

    def test_serialise(self) -> None:
        v = LinkValue("res_link", ":linkProp", resource_id="res_id")
        expected = (
            b'<resptr-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":linkProp">'
            b'<resptr permissions="prop-default">res_link</resptr></resptr-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestListValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ListValue("item1", "listName", ":listProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns_false_node(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            ListValue(None, "list", ":listProp", resource_id="res_id")

    def test_warns_false_list(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            ListValue("Node", None, ":listProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = ListValue("item1", "listName", ":listProp", resource_id="res_id")
        expected = (
            b'<list-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":listProp" list="listName">'
            b'<list permissions="prop-default">item1</list></list-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestRichtext:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            Richtext("<p>Hello World</p>", ":richtextProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            Richtext(None, ":richtextProp", resource_id="res_id")  # type: ignore[arg-type]

    def test_serialise(self) -> None:
        v = Richtext("<p>Hello World</p>", ":richtextProp", resource_id="res_id")
        expected = (
            b'<text-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":richtextProp">'
            b'<text encoding="xml" permissions="prop-default">&lt;p&gt;Hello World&lt;/p&gt;</text></text-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestSimpleText:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            SimpleText("Hello World", ":simpleTextProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            SimpleText(None, ":simpleTextProp", resource_id="res_id")  # type: ignore[arg-type]

    def test_serialise(self) -> None:
        v = SimpleText("Hello World", ":simpleTextProp", resource_id="res_id")
        expected = (
            b'<text-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":simpleTextProp">'
            b'<text encoding="utf8" permissions="prop-default">Hello World</text></text-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestTimeValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            TimeValue("2009-10-10T12:00:00-05:00", ":timeProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            TimeValue("invalidTime", ":timeProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = TimeValue("2009-10-10T12:00:00-05:00", ":timeProp", resource_id="res_id")
        expected = (
            b'<time-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":timeProp">'
            b'<time permissions="prop-default">2009-10-10T12:00:00-05:00</time></time-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestUriValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            UriValue("https://example.com", ":uriProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            UriValue("invalidUri", ":uriProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = UriValue("https://example.com", ":uriProp", resource_id="res_id")
        expected = (
            b'<uri-prop xmlns="https://dasch.swiss/schema" '
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":uriProp">'
            b'<uri permissions="prop-default">https://example.com</uri></uri-prop>'
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


if __name__ == "__main__":
    pytest.main([__file__])
