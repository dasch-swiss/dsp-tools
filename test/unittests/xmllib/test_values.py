import warnings

import pytest
from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
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


class TestBooleanValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            BooleanValue("False", ":booleanProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            BooleanValue("other", ":booleanProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = BooleanValue("0", ":booleanProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<boolean-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":booleanProp">'
            b'<boolean permissions="open">false</boolean>'
            b"</boolean-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = BooleanValue("0", ":booleanProp", resource_id="res_id")
        expected = (
            b"<boolean-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":booleanProp">'
            b"<boolean>false</boolean>"
            b"</boolean-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestColorValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ColorValue("#FFFFFF", ":colorProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            ColorValue("invalidColor", ":colorProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = ColorValue("#000000", ":colorProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<color-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":colorProp">'
            b'<color permissions="open">#000000</color>'
            b"</color-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = ColorValue(
            "#000000", ":colorProp", resource_id="res_id", permissions=Permissions.PROJECT_SPECIFIC_PERMISSIONS
        )
        expected = (
            b"<color-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":colorProp">'
            b"<color>#000000</color>"
            b"</color-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestDateValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DateValue("2023-01-01", ":dateProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            DateValue("invalidDate", ":dateProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = DateValue("2023-01-01", ":dateProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<date-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":dateProp">'
            b'<date permissions="open">2023-01-01</date>'
            b"</date-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = DateValue("2023-01-01", ":dateProp", resource_id="res_id")
        expected = (
            b"<date-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":dateProp">'
            b"<date>2023-01-01</date>"
            b"</date-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestDecimalValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DecimalValue("3.14", ":decimalProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            DecimalValue("invalidDecimal", ":decimalProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = DecimalValue("3.14", ":decimalProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<decimal-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":decimalProp">'
            b'<decimal permissions="open">3.14</decimal>'
            b"</decimal-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = DecimalValue("3.14", ":decimalProp", resource_id="res_id")
        expected = (
            b"<decimal-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":decimalProp">'
            b"<decimal>3.14</decimal>"
            b"</decimal-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestGeonameValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            GeonameValue("00099", ":geonameProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            GeonameValue("invalidGeoname", ":geonameProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = GeonameValue("99", ":geonameProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<geoname-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":geonameProp">'
            b'<geoname permissions="open">99</geoname>'
            b"</geoname-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = GeonameValue("99", ":geonameProp", resource_id="res_id")
        expected = (
            b"<geoname-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":geonameProp">'
            b"<geoname>99</geoname>"
            b"</geoname-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestIntValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            IntValue("42", ":intProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            IntValue("invalidInt", ":intProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = IntValue("42", ":intProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<integer-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":intProp">'
            b'<integer permissions="open">42</integer>'
            b"</integer-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = IntValue("42", ":intProp", resource_id="res_id")
        expected = (
            b"<integer-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":intProp">'
            b"<integer>42</integer>"
            b"</integer-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestLinkValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            LinkValue("link", ":linkProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            LinkValue(None, ":linkProp", resource_id="res_id", permissions=Permissions.OPEN)  # type: ignore[arg-type]

    def test_serialise(self) -> None:
        v = LinkValue("res_link", ":linkProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<resptr-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":linkProp">'
            b'<resptr permissions="open">res_link</resptr>'
            b"</resptr-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = LinkValue("res_link", ":linkProp", resource_id="res_id")
        expected = (
            b"<resptr-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":linkProp">'
            b"<resptr>res_link</resptr>"
            b"</resptr-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestListValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ListValue("item1", "listName", ":listProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns_false_node(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            ListValue(None, "list", ":listProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_warns_false_list(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            ListValue("Node", None, ":listProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = ListValue("item1", "listName", ":listProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<list-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":listProp" list="listName">'
            b'<list permissions="open">item1</list>'
            b"</list-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = ListValue("item1", "listName", ":listProp", resource_id="res_id")
        expected = (
            b"<list-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":listProp" list="listName">'
            b"<list>item1</list>"
            b"</list-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestRichtext:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            Richtext("<p>Hello World</p>", ":richtextProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            Richtext(None, ":richtextProp", resource_id="res_id", permissions=Permissions.OPEN)  # type: ignore[arg-type]

    def test_serialise(self) -> None:
        v = Richtext("<p>Hello World</p>", ":richtextProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<text-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":richtextProp">'
            b'<text encoding="xml" permissions="open">&lt;p&gt;Hello World&lt;/p&gt;</text>'
            b"</text-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = Richtext("<p>Hello World</p>", ":richtextProp", resource_id="res_id")
        expected = (
            b"<text-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":richtextProp">'
            b'<text encoding="xml">&lt;p&gt;Hello World&lt;/p&gt;</text>'
            b"</text-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestSimpleText:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            SimpleText("Hello World", ":simpleTextProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            SimpleText(None, ":simpleTextProp", resource_id="res_id", permissions=Permissions.OPEN)  # type: ignore[arg-type]

    def test_serialise(self) -> None:
        v = SimpleText("Hello World", ":simpleTextProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<text-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":simpleTextProp">'
            b'<text encoding="utf8" permissions="open">Hello World</text>'
            b"</text-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = SimpleText("Hello World", ":simpleTextProp", resource_id="res_id")
        expected = (
            b"<text-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":simpleTextProp">'
            b'<text encoding="utf8">Hello World</text>'
            b"</text-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestTimeValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            TimeValue("2009-10-10T12:00:00-05:00", ":timeProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            TimeValue("invalidTime", ":timeProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = TimeValue("2009-10-10T12:00:00-05:00", ":timeProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<time-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":timeProp">'
            b'<time permissions="open">2009-10-10T12:00:00-05:00</time>'
            b"</time-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = TimeValue("2009-10-10T12:00:00-05:00", ":timeProp", resource_id="res_id")
        expected = (
            b"<time-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":timeProp">'
            b"<time>2009-10-10T12:00:00-05:00</time>"
            b"</time-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestUriValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            UriValue("https://example.com", ":uriProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            UriValue("invalidUri", ":uriProp", resource_id="res_id", permissions=Permissions.OPEN)

    def test_serialise(self) -> None:
        v = UriValue("https://example.com", ":uriProp", resource_id="res_id", permissions=Permissions.OPEN)
        expected = (
            b"<uri-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":uriProp">'
            b'<uri permissions="open">https://example.com</uri>'
            b"</uri-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected

    def test_serialise_doap(self) -> None:
        v = UriValue("https://example.com", ":uriProp", resource_id="res_id")
        expected = (
            b"<uri-prop "
            b'xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'name=":uriProp">'
            b"<uri>https://example.com</uri>"
            b"</uri-prop>"
        )
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


if __name__ == "__main__":
    pytest.main([__file__])
