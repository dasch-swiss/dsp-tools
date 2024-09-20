import pytest
from lxml import etree
from rdflib import XSD
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xml_validate.models.data_rdf import BooleanValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ColorValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import DateValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import DecimalValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import GeonameValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import IntValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import LinkValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ListValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import RichtextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import TimeValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import UriValueRDF
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_all_resources
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_one_property
from dsp_tools.commands.xml_validate.reformat_input import _deserialise_one_resource


class TestResource:
    def test_empty(self, resource_empty: etree._Element) -> None:
        res = _deserialise_one_resource(resource_empty)
        assert res.res_id == URIRef("one")
        assert res.res_class == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything")
        assert res.label == Literal("lbl", datatype=XSD.string)
        assert len(res.values) == 0

    def test_with_props(self, root_resource_with_props: etree._Element) -> None:
        res_list = _deserialise_all_resources(root_resource_with_props)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.res_id == URIRef("one")
        assert res.res_class == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything")
        assert res.label == Literal("lbl", datatype=XSD.string)
        assert len(res.values) == 3

    def test_region(self, root_resource_region: etree._Element) -> None:
        res_list = _deserialise_all_resources(root_resource_region)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.res_id == URIRef("region_1")
        assert res.label == Literal("Region", datatype=XSD.string)
        assert len(res.values) == 0


class TestBooleanValue:
    def test_corr(self, boolean_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(boolean_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, BooleanValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean")
        assert res.object_value == Literal("true", datatype=XSD.boolean)


class TestColorValue:
    def test_corr(self, color_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(color_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, ColorValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testColor")
        assert res.object_value == Literal("#00ff00", datatype=XSD.string)

    def test_several(self, color_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(color_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, ColorValueRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testColor")
        assert res[0].object_value == Literal("#00ff00", datatype=XSD.string)
        assert res[1].object_value == Literal("#00ff11", datatype=XSD.string)


class TestDateValue:
    def test_corr(self, date_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(date_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, DateValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1")
        assert res.object_value == Literal("JULIAN:BCE:0700:BCE:0600", datatype=XSD.string)

    def test_several(self, date_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(date_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, DateValueRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1")
        assert res[0].object_value == Literal("JULIAN:BCE:0700:BCE:0600", datatype=XSD.string)
        assert res[1].object_value == Literal("ISLAMIC:BCE:0700:BCE:0600", datatype=XSD.string)


class TestDecimalValue:
    def test_corr(self, decimal_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(decimal_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, DecimalValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText")
        assert res.object_value == Literal("2.71", datatype=XSD.decimal)

    def test_several(self, decimal_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(decimal_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, DecimalValueRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText")
        assert res[0].object_value == Literal("1.0", datatype=XSD.decimal)
        assert res[1].object_value == Literal("2.0", datatype=XSD.decimal)


class TestGeonameValue:
    def test_corr(self, geoname_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(geoname_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, GeonameValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname")
        assert res.object_value == Literal("1111111", datatype=XSD.integer)

    def test_several(self, geoname_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(geoname_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, GeonameValueRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname")
        assert res[0].object_value == Literal("1111111", datatype=XSD.integer)
        assert res[1].object_value == Literal("2222222", datatype=XSD.integer)


class TestIntValue:
    def test_corr(self, integer_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(integer_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, IntValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText")
        assert res.object_value == Literal("1", datatype=XSD.integer)

    def test_several(self, integer_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(integer_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, IntValueRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText")
        assert res[0].object_value == Literal("1", datatype=XSD.integer)
        assert res[1].object_value == Literal("2", datatype=XSD.integer)


class TestListValue:
    def test_corr(self, list_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(list_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, ListValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp")
        assert res.list_name == Literal("onlyList", datatype=XSD.string)
        assert res.object_value == Literal("n1", datatype=XSD.string)

    def test_several(self, list_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(list_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, ListValueRDF) for x in res])
        one = res[0]
        assert isinstance(one, ListValueRDF)
        assert one.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp")
        assert one.list_name == Literal("onlyList", datatype=XSD.string)
        assert res[0].object_value == Literal("n1", datatype=XSD.string)
        assert res[1].object_value == Literal("n2", datatype=XSD.string)


class TestSimpleTextValue:
    def test_corr(self, text_simpletext_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(text_simpletext_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, SimpleTextRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea")
        assert res.object_value == Literal("Text", datatype=XSD.string)

    def test_several(self, text_simpletext_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(text_simpletext_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, SimpleTextRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText")
        assert res[0].object_value == Literal("Text 1", datatype=XSD.string)
        assert res[1].object_value == Literal("Text 2", datatype=XSD.string)

    def test_wrong(self, text_simpletext_value_wrong: etree._Element) -> None:
        res_list = _deserialise_one_property(text_simpletext_value_wrong)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, SimpleTextRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText")
        assert res.object_value == Literal("", datatype=XSD.string)


class TestRichtextValue:
    def test_corr(self, text_richtext_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(text_richtext_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, RichtextRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext")
        assert res.object_value == Literal("Text", datatype=XSD.string)

    def test_several(self, text_richtext_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(text_richtext_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, RichtextRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext")
        assert res[0].object_value == Literal("Text 1", datatype=XSD.string)
        assert res[1].object_value == Literal("Text 2", datatype=XSD.string)


class TestTimeValue:
    def test_corr(self, time_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(time_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, TimeValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue")
        assert res.object_value == Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp)

    def test_several(self, time_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(time_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, TimeValueRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue")
        assert res[0].object_value == Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp)
        assert res[1].object_value == Literal("2019-10-23T13:45:12.01-08:00", datatype=XSD.dateTimeStamp)


class TestUriValue:
    def test_corr(self, uri_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(uri_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, UriValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue")
        assert res.object_value == Literal("https://dasch.swiss", datatype=XSD.anyURI)

    def test_several(self, uri_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(uri_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, UriValueRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue")
        assert res[0].object_value == Literal("https://dasch.swiss", datatype=XSD.anyURI)
        assert res[1].object_value == Literal("https://app.dasch.swiss", datatype=XSD.anyURI)


class TestLinkValue:
    def test_corr(self, resptr_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(resptr_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert isinstance(res, LinkValueRDF)
        assert res.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo")
        assert res.object_value == URIRef("id_1")

    def test_several(self, resptr_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(resptr_value_corr_several)
        assert len(res) == 2
        assert all([isinstance(x, LinkValueRDF) for x in res])
        assert res[0].prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo")
        assert res[0].object_value == URIRef("id_1")
        assert res[1].object_value == URIRef("id_2")


if __name__ == "__main__":
    pytest.main([__file__])
