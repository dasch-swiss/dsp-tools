import warnings

import pytest

from dsp_tools.error.xmllib_warnings import XmllibInputWarning
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
        with pytest.warns(XmllibInputWarning):
            BooleanValue("other", ":booleanProp", resource_id="res_id", permissions=Permissions.OPEN)


class TestColorValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ColorValue.new("#FFFFFF", ":colorProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            ColorValue.new(
                "invalidColor", ":colorProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None
            )


class TestDateValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DateValue.new("2023-01-01", ":dateProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            DateValue.new("invalidDate", ":dateProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)


class TestDecimalValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DecimalValue.new("3.14", ":decimalProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            DecimalValue.new(
                "invalidDecimal", ":decimalProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None
            )


class TestGeonameValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            GeonameValue.new("00099", ":geonameProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            GeonameValue.new(
                "invalidGeoname", ":geonameProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None
            )


class TestIntValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            IntValue.new("42", ":intProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            IntValue.new("invalidInt", ":intProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)


class TestLinkValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            LinkValue.new("link", ":linkProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            LinkValue.new(None, ":linkProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)


class TestListValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ListValue.new(
                "item1", "listName", ":listProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None
            )
        assert len(caught_warnings) == 0

    def test_warns_false_node(self) -> None:
        with pytest.warns(XmllibInputWarning):
            ListValue.new(None, "list", ":listProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)

    def test_warns_false_list(self) -> None:
        with pytest.warns(XmllibInputWarning):
            ListValue.new("Node", None, ":listProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)


class TestRichtext:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            Richtext("<p>Hello World</p>", ":richtextProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            Richtext(None, ":richtextProp", resource_id="res_id", permissions=Permissions.OPEN)  # type: ignore[arg-type]


class TestSimpleText:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            SimpleText.new(
                "Hello World", ":simpleTextProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None
            )
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            SimpleText.new(None, ":simpleTextProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)


class TestTimeValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            TimeValue.new(
                "2009-10-10T12:00:00-05:00",
                ":timeProp",
                resource_id="res_id",
                permissions=Permissions.OPEN,
                comment=None,
            )
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            TimeValue.new("invalidTime", ":timeProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)


class TestUriValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            UriValue.new(
                "https://example.com", ":uriProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None
            )
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(XmllibInputWarning):
            UriValue.new("invalidUri", ":uriProp", resource_id="res_id", permissions=Permissions.OPEN, comment=None)


if __name__ == "__main__":
    pytest.main([__file__])
