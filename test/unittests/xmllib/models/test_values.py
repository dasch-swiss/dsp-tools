import warnings

import pytest

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


class TestColorValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ColorValue("#FFFFFF", ":colorProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            ColorValue("invalidColor", ":colorProp", resource_id="res_id", permissions=Permissions.OPEN)


class TestDateValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DateValue("2023-01-01", ":dateProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            DateValue("invalidDate", ":dateProp", resource_id="res_id", permissions=Permissions.OPEN)


class TestDecimalValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DecimalValue("3.14", ":decimalProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            DecimalValue("invalidDecimal", ":decimalProp", resource_id="res_id", permissions=Permissions.OPEN)


class TestGeonameValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            GeonameValue("00099", ":geonameProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            GeonameValue("invalidGeoname", ":geonameProp", resource_id="res_id", permissions=Permissions.OPEN)


class TestIntValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            IntValue("42", ":intProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            IntValue("invalidInt", ":intProp", resource_id="res_id", permissions=Permissions.OPEN)


class TestLinkValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            LinkValue("link", ":linkProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            LinkValue(None, ":linkProp", resource_id="res_id", permissions=Permissions.OPEN)  # type: ignore[arg-type]


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


class TestRichtext:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            Richtext("<p>Hello World</p>", ":richtextProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            Richtext(None, ":richtextProp", resource_id="res_id", permissions=Permissions.OPEN)  # type: ignore[arg-type]


class TestSimpleText:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            SimpleText("Hello World", ":simpleTextProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            SimpleText(None, ":simpleTextProp", resource_id="res_id", permissions=Permissions.OPEN)  # type: ignore[arg-type]


class TestTimeValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            TimeValue("2009-10-10T12:00:00-05:00", ":timeProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            TimeValue("invalidTime", ":timeProp", resource_id="res_id", permissions=Permissions.OPEN)


class TestUriValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            UriValue("https://example.com", ":uriProp", resource_id="res_id", permissions=Permissions.OPEN)
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning):
            UriValue("invalidUri", ":uriProp", resource_id="res_id", permissions=Permissions.OPEN)


if __name__ == "__main__":
    pytest.main([__file__])
