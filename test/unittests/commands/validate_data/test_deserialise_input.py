import pytest
from lxml import etree

from dsp_tools.commands.validate_data.deserialise_input import _deserialise_all_resources
from dsp_tools.commands.validate_data.deserialise_input import _deserialise_one_property
from dsp_tools.commands.validate_data.deserialise_input import _deserialise_one_resource
from dsp_tools.commands.validate_data.deserialise_input import _get_text_as_string
from dsp_tools.commands.validate_data.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RegionDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import UriValueDeserialised


class TestResource:
    def test_empty(self, resource_empty: etree._Element) -> None:
        res = _deserialise_one_resource(resource_empty)
        assert isinstance(res, ResourceDeserialised)
        assert res.res_id == "one"
        assert res.res_class == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert res.label == "lbl"
        assert len(res.values) == 0

    def test_with_props(self, root_resource_with_props: etree._Element) -> None:
        res_list = _deserialise_all_resources(root_resource_with_props).resources
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, ResourceDeserialised)
        assert res.res_id == "one"
        assert res.res_class == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert res.label == "lbl"
        assert len(res.values) == 3

    def test_region(self, root_resource_region: etree._Element) -> None:
        res_list = _deserialise_all_resources(root_resource_region).resources
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, RegionDeserialised)
        assert res.res_id == "region_1"


class TestBooleanValue:
    def test_corr(self, boolean_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(boolean_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, BooleanValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean"
        assert res.object_value == "true"


class TestColorValue:
    def test_corr(self, color_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(color_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, ColorValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testColor"
        assert res.object_value == "#00ff00"

    def test_several(self, color_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(color_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, ColorValueDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testColor"
        assert res[0].object_value == "#00ff00"
        assert res[1].object_value == "#00ff11"


class TestDateValue:
    def test_corr(self, date_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(date_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, DateValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1"
        assert res.object_value == "JULIAN:BCE:0700:BCE:0600"

    def test_several(self, date_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(date_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, DateValueDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1"
        assert res[0].object_value == "JULIAN:BCE:0700:BCE:0600"
        assert res[1].object_value == "ISLAMIC:BCE:0700:BCE:0600"


class TestDecimalValue:
    def test_corr(self, decimal_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(decimal_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, DecimalValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText"
        assert res.object_value == "2.71"

    def test_several(self, decimal_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(decimal_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, DecimalValueDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText"
        assert res[0].object_value == "1.0"
        assert res[1].object_value == "2.0"


class TestGeonameValue:
    def test_corr(self, geoname_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(geoname_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, GeonameValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname"
        assert res.object_value == "1111111"

    def test_several(self, geoname_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(geoname_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, GeonameValueDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname"
        assert res[0].object_value == "1111111"
        assert res[1].object_value == "2222222"


class TestIntValue:
    def test_corr(self, integer_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(integer_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, IntValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText"
        assert res.object_value == "1"

    def test_several(self, integer_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(integer_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, IntValueDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText"
        assert res[0].object_value == "1"
        assert res[1].object_value == "2"


class TestListValue:
    def test_corr(self, list_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(list_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, ListValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp"
        assert res.list_name == "firstList"
        assert res.object_value == "n1"

    def test_several(self, list_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(list_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, ListValueDeserialised) for x in res])
        one = res[0]
        assert isinstance(one, ListValueDeserialised)
        assert one.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp"
        assert one.list_name == "firstList"
        assert res[0].object_value == "n1"
        assert res[1].object_value == "n2"


class TestSimpleTextValue:
    def test_corr(self, text_simpletext_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(text_simpletext_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, SimpleTextDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea"
        assert res.object_value == "Text"

    def test_several(self, text_simpletext_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(text_simpletext_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, SimpleTextDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText"
        assert res[0].object_value == "Text 1"
        assert res[1].object_value == "Text 2"

    def test_wrong(self, text_simpletext_value_wrong: etree._Element) -> None:
        res_list = _deserialise_one_property(text_simpletext_value_wrong)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, SimpleTextDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText"
        assert not res.object_value


class TestRichtextValue:
    def test_corr(self, text_richtext_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(text_richtext_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, RichtextDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext"
        assert res.object_value == "<p>Text</p>"

    def test_several(self, text_richtext_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(text_richtext_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, RichtextDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext"
        assert res[0].object_value == "Text 1"
        assert res[1].object_value == "Text 2"


class TestTimeValue:
    def test_corr(self, time_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(time_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, TimeValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue"
        assert res.object_value == "2019-10-23T13:45:12.01-14:00"

    def test_several(self, time_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(time_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, TimeValueDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue"
        assert res[0].object_value == "2019-10-23T13:45:12.01-14:00"
        assert res[1].object_value == "2019-10-23T13:45:12.01-08:00"


class TestUriValue:
    def test_corr(self, uri_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(uri_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, UriValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue"
        assert res.object_value == "https://dasch.swiss"

    def test_several(self, uri_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(uri_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, UriValueDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue"
        assert res[0].object_value == "https://dasch.swiss"
        assert res[1].object_value == "https://app.dasch.swiss"


class TestLinkValue:
    def test_corr(self, resptr_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(resptr_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, LinkValueDeserialised)
        assert res.prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo"
        assert res.object_value == "id_1"

    def test_several(self, resptr_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(resptr_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, LinkValueDeserialised) for x in res])
        assert res[0].prop_name == "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo"
        assert res[0].object_value == "id_1"
        assert res[1].object_value == "id_2"


@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        ('<text encoding="xml"><p>Text</p></text>', "<p>Text</p>"),
        ('<text encoding="xml"><text>Text</text></text>', "<text>Text</text>"),
        ('<text encoding="xml"><p><p>Text second word</p>Tail</p></text>', "<p><p>Text second word</p>Tail</p>"),
        ('<text encoding="xml"> </text>', " "),
        ('<text encoding="xml"></text>', None),
        ('<text encoding="xml"><br/>Text</text>', "<br/>Text"),
        ('<text encoding="xml">Text<br/>  </text>', "Text<br/>"),
        ('<text encoding="xml">  Text<br/>Text<br/>Text</text>', "Text<br/>Text<br/>Text"),
    ],
)
def test_get_text_as_string(input_str: str, expected: str) -> None:
    val = etree.fromstring(input_str)
    result = _get_text_as_string(val)
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
