import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.models.data_deserialised import BooleanValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ColorValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import DateValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import DecimalValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import GeomValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import GeonameValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import IntValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import LinkValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ListValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import RichtextData
from dsp_tools.commands.xml_validate.models.data_deserialised import SimpleTextData
from dsp_tools.commands.xml_validate.models.data_deserialised import TimeValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import UriValueData
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_boolean_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_color_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_date_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_decimal_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_geometry_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_geoname_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_int_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_list_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_one_resource
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_resptr_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_text_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_time_prop
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_uri_prop


class TestResource:
    def test_empty(self, resource_empty: etree._Element) -> None:
        res = _deserialise_one_resource(resource_empty)
        assert res.res_id == "one"
        assert res.res_class == ":ClassWithEverything"
        assert res.label == "lbl"
        assert len(res.values) == 0

    def test_with_props(self, resource_with_props: etree._Element) -> None:
        res = _deserialise_one_resource(resource_with_props)
        assert res.res_id == "one"
        assert res.res_class == ":ClassWithEverything"
        assert res.label == "lbl"
        assert len(res.values) == 3


class TestBooleanValue:
    def test_corr(self, boolean_value_corr: etree._Element) -> None:
        res_list = _deserialise_boolean_prop(boolean_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, BooleanValueData)
        assert res.prop_name == ":testBoolean"
        assert res.prop_value == "true"


class TestColorValue:
    def test_corr(self, color_value_corr: etree._Element) -> None:
        res_list = _deserialise_color_prop(color_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, ColorValueData)
        assert res.prop_name == ":testColor"
        assert res.prop_value == "#00ff00"

    def test_several(self, color_value_corr_several: etree._Element) -> None:
        res = _deserialise_color_prop(color_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, ColorValueData) for x in res])
        assert res[0].prop_name == ":testColor"
        assert res[0].prop_value == "#00ff00"
        assert res[1].prop_value == "#00ff11"


class TestDateValue:
    def test_corr(self, date_value_corr: etree._Element) -> None:
        res_list = _deserialise_date_prop(date_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, DateValueData)
        assert res.prop_name == ":testSubDate1"
        assert res.prop_value == "JULIAN:BCE:0700:BCE:0600"

    def test_several(self, date_value_corr_several: etree._Element) -> None:
        res = _deserialise_date_prop(date_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, DateValueData) for x in res])
        assert res[0].prop_name == ":testSubDate1"
        assert res[0].prop_value == "JULIAN:BCE:0700:BCE:0600"
        assert res[1].prop_value == "ISLAMIC:BCE:0700:BCE:0600"


class TestDecimalValue:
    def test_corr(self, decimal_value_corr: etree._Element) -> None:
        res_list = _deserialise_decimal_prop(decimal_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, DecimalValueData)
        assert res.prop_name == ":testDecimalSimpleText"
        assert res.prop_value == "2.71"

    def test_several(self, decimal_value_corr_several: etree._Element) -> None:
        res = _deserialise_decimal_prop(decimal_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, DecimalValueData) for x in res])
        assert res[0].prop_name == ":testDecimalSimpleText"
        assert res[0].prop_value == "1.0"
        assert res[1].prop_value == "2.0"


class TestGeomValue:
    def test_corr(self, geometry_value_corr: etree._Element) -> None:
        res_list = _deserialise_geometry_prop(geometry_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, GeomValueData)
        assert res.prop_name == "hasGeometry"
        assert len(res.prop_value) > 1


class TestGeonameValue:
    def test_corr(self, geoname_value_corr: etree._Element) -> None:
        res_list = _deserialise_geoname_prop(geoname_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, GeonameValueData)
        assert res.prop_name == ":testGeoname"
        assert res.prop_value == "1111111"

    def test_several(self, geoname_value_corr_several: etree._Element) -> None:
        res = _deserialise_geoname_prop(geoname_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, GeonameValueData) for x in res])
        assert res[0].prop_name == ":testGeoname"
        assert res[0].prop_value == "1111111"
        assert res[1].prop_value == "2222222"


class TestIntValue:
    def test_corr(self, integer_value_corr: etree._Element) -> None:
        res_list = _deserialise_int_prop(integer_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, IntValueData)
        assert res.prop_name == ":testIntegerSimpleText"
        assert res.prop_value == "1"

    def test_several(self, integer_value_corr_several: etree._Element) -> None:
        res = _deserialise_int_prop(integer_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, IntValueData) for x in res])
        assert res[0].prop_name == ":testIntegerSimpleText"
        assert res[0].prop_value == "1"
        assert res[1].prop_value == "2"


class TestListValue:
    def test_corr(self, list_value_corr: etree._Element) -> None:
        res_list = _deserialise_list_prop(list_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, ListValueData)
        assert res.prop_name == ":testListProp"
        assert res.list_name == "onlyList"
        assert res.prop_value == "n1"

    def test_several(self, list_value_corr_several: etree._Element) -> None:
        res = _deserialise_list_prop(list_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, ListValueData) for x in res])
        one = res[0]
        assert isinstance(one, ListValueData)
        assert one.prop_name == ":testListProp"
        assert one.list_name == "onlyList"
        assert res[0].prop_value == "n1"
        assert res[1].prop_value == "n2"


class TestSimpleTextValue:
    def test_corr(self, text_simpletext_value_corr: etree._Element) -> None:
        res_list = _deserialise_text_prop(text_simpletext_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, SimpleTextData)
        assert res.prop_name == ":testTextarea"
        assert res.prop_value == "Text"

    def test_several(self, text_simpletext_value_corr_several: etree._Element) -> None:
        res = _deserialise_text_prop(text_simpletext_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, SimpleTextData) for x in res])
        assert res[0].prop_name == ":testSimpleText"
        assert res[0].prop_value == "Text 1"
        assert res[1].prop_value == "Text 2"

    def test_wrong(self, text_simpletext_value_wrong: etree._Element) -> None:
        res_list = _deserialise_text_prop(text_simpletext_value_wrong)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, SimpleTextData)
        assert res.prop_name == ":testSimpleText"
        assert res.prop_value == ""


class TestRichtextValue:
    def test_corr(self, text_richtext_value_corr: etree._Element) -> None:
        res_list = _deserialise_text_prop(text_richtext_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, RichtextData)
        assert res.prop_name == ":testRichtext"
        assert res.prop_value == "Text"

    def test_several(self, text_richtext_value_corr_several: etree._Element) -> None:
        res = _deserialise_text_prop(text_richtext_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, RichtextData) for x in res])
        assert res[0].prop_name == ":testRichtext"
        assert res[0].prop_value == "Text 1"
        assert res[1].prop_value == "Text 2"


class TestTimeValue:
    def test_corr(self, time_value_corr: etree._Element) -> None:
        res_list = _deserialise_time_prop(time_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, TimeValueData)
        assert res.prop_name == ":testTimeValue"
        assert res.prop_value == "2019-10-23T13:45:12.01-14:00"

    def test_several(self, time_value_corr_several: etree._Element) -> None:
        res = _deserialise_time_prop(time_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, TimeValueData) for x in res])
        assert res[0].prop_name == ":testTimeValue"
        assert res[0].prop_value == "2019-10-23T13:45:12.01-14:00"
        assert res[1].prop_value == "2019-10-23T13:45:12.01-08:00"


class TestUriValue:
    def test_corr(self, uri_value_corr: etree._Element) -> None:
        res_list = _deserialise_uri_prop(uri_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, UriValueData)
        assert res.prop_name == ":testUriValue"
        assert res.prop_value == "https://dasch.swiss"

    def test_several(self, uri_value_corr_several: etree._Element) -> None:
        res = _deserialise_uri_prop(uri_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, UriValueData) for x in res])
        assert res[0].prop_name == ":testUriValue"
        assert res[0].prop_value == "https://dasch.swiss"
        assert res[1].prop_value == "https://app.dasch.swiss"


class TestLinkValue:
    def test_corr(self, resptr_value_corr: etree._Element) -> None:
        res_list = _deserialise_resptr_prop(resptr_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, LinkValueData)
        assert res.prop_name == ":testHasLinkTo"
        assert res.prop_value == "id_1"

    def test_several(self, resptr_value_corr_several: etree._Element) -> None:
        res = _deserialise_resptr_prop(resptr_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, LinkValueData) for x in res])
        assert res[0].prop_name == ":testHasLinkTo"
        assert res[0].prop_value == "id_1"
        assert res[1].prop_value == "id_2"


if __name__ == "__main__":
    pytest.main([__file__])
