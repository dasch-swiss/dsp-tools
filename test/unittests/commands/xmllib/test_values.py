import warnings

import pytest
import regex
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
            BooleanValue("", ":booleanProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            BooleanValue("", ":booleanProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = BooleanValue("", ":booleanProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestColorValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ColorValue("", ":colorProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            ColorValue("", ":colorProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = ColorValue("", ":colorProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestDateValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DateValue("", ":dateProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            DateValue("", ":dateProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = DateValue("", ":dateProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestDecimalValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            DecimalValue("", ":decimalProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            DecimalValue("", ":decimalProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = DecimalValue("", ":decimalProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestGeonameValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            GeonameValue("", ":geonameProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            GeonameValue("", ":geonameProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = GeonameValue("", ":geonameProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestIntValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            IntValue("", ":intProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            IntValue("", ":intProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = IntValue("", ":intProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestLinkValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            LinkValue("", ":linkProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            LinkValue("", ":linkProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = LinkValue("", ":linkProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestListValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ListValue("", ":listProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            ListValue("", ":listProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = ListValue("", ":listProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestRichtext:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            Richtext("", ":richtextProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            Richtext("", ":richtextProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = Richtext("", ":richtextProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestSimpleText:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            SimpleText("", ":simpleTextProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            SimpleText("", ":simpleTextProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = SimpleText("", ":simpleTextProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestTimeValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            TimeValue("", ":timeProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            TimeValue("", ":timeProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = TimeValue("", ":timeProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


class TestUriValue:
    def test_good(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            UriValue("", ":uriProp", resource_id="res_id")
        assert len(caught_warnings) == 0

    def test_warns(self) -> None:
        expected = regex.escape("expected")
        with pytest.warns(DspToolsUserWarning, match=expected):
            UriValue("", ":uriProp", resource_id="res_id")

    def test_serialise(self) -> None:
        v = UriValue("", ":uriProp", resource_id="res_id")
        expected = ""
        res_str = etree.tostring(v.serialise())
        assert res_str == expected


if __name__ == "__main__":
    pytest.main([__file__])
