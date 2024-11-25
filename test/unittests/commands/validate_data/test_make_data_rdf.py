import pytest
from rdflib import XSD
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.make_data_rdf import _get_file_extension
from dsp_tools.commands.validate_data.make_data_rdf import _transform_file_value
from dsp_tools.commands.validate_data.make_data_rdf import _transform_one_resource
from dsp_tools.commands.validate_data.make_data_rdf import _transform_one_value
from dsp_tools.commands.validate_data.models.data_deserialised import BitstreamDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import UriValueDeserialised
from dsp_tools.commands.validate_data.models.data_rdf import BooleanValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ColorValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import DateValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import DecimalValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import GeonameValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import IntValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import LinkValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ListValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import MovingImageFileValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ResourceRDF
from dsp_tools.commands.validate_data.models.data_rdf import RichtextRDF
from dsp_tools.commands.validate_data.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.validate_data.models.data_rdf import TimeValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import UriValueRDF
from test.unittests.commands.validate_data.constants import DATA


class TestResource:
    def test_empty(self, resource_deserialised_no_values: ResourceDeserialised) -> None:
        res_li = _transform_one_resource(resource_deserialised_no_values)
        assert len(res_li) == 1
        res = res_li[0]
        assert isinstance(res, ResourceRDF)
        assert res.res_iri == DATA["id"]
        assert res.res_class == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything")
        assert res.label == Literal("lbl", datatype=XSD.string)

    def test_with_props(self, resource_deserialised_with_values: ResourceDeserialised) -> None:
        res_list = _transform_one_resource(resource_deserialised_with_values)
        assert len(res_list) == 2
        res = res_list[0]
        assert isinstance(res, ResourceRDF)
        assert res.res_iri == DATA["id"]
        assert res.res_class == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything")
        assert res.label == Literal("lbl", datatype=XSD.string)
        val = res_list[1]
        assert isinstance(val, BooleanValueRDF)


class TestBooleanValue:
    def test_corr(self, boolean_value_deserialised_corr: BooleanValueDeserialised) -> None:
        val = _transform_one_value(boolean_value_deserialised_corr, DATA["id"])
        assert isinstance(val, BooleanValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean")
        assert val.object_value == Literal("false", datatype=XSD.boolean)

    def test_one(self, boolean_value_deserialised_one: BooleanValueDeserialised) -> None:
        val = _transform_one_value(boolean_value_deserialised_one, DATA["id"])
        assert isinstance(val, BooleanValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean")
        assert val.object_value == Literal("true", datatype=XSD.boolean)

    def test_zero(self, boolean_value_deserialised_zero: BooleanValueDeserialised) -> None:
        val = _transform_one_value(boolean_value_deserialised_zero, DATA["id"])
        assert isinstance(val, BooleanValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean")
        assert val.object_value == Literal("false", datatype=XSD.boolean)

    def test_none(self, boolean_value_deserialised_none: BooleanValueDeserialised) -> None:
        val = _transform_one_value(boolean_value_deserialised_none, DATA["id"])
        assert isinstance(val, BooleanValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestColorValue:
    def test_corr(self, color_value_deserialised_corr: ColorValueDeserialised) -> None:
        val = _transform_one_value(color_value_deserialised_corr, DATA["id"])
        assert isinstance(val, ColorValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testColor")
        assert val.object_value == Literal("#00ff00", datatype=XSD.string)

    def test_none(self, color_value_deserialised_none: ColorValueDeserialised) -> None:
        val = _transform_one_value(color_value_deserialised_none, DATA["id"])
        assert isinstance(val, ColorValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testColor")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestDateValue:
    def test_corr(self, date_value_deserialised_corr: DateValueDeserialised) -> None:
        val = _transform_one_value(date_value_deserialised_corr, DATA["id"])
        assert isinstance(val, DateValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1")
        assert val.object_value == Literal("JULIAN:BCE:0700:BCE:0600", datatype=XSD.string)

    def test_none(self, date_value_deserialised_none: DateValueDeserialised) -> None:
        val = _transform_one_value(date_value_deserialised_none, DATA["id"])
        assert isinstance(val, DateValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestDecimalValue:
    def test_corr(self, decimal_value_deserialised_corr: DecimalValueDeserialised) -> None:
        val = _transform_one_value(decimal_value_deserialised_corr, DATA["id"])
        assert isinstance(val, DecimalValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText")
        assert val.object_value == Literal("1.2", datatype=XSD.decimal)

    def test_none(self, decimal_value_deserialised_none: DecimalValueDeserialised) -> None:
        val = _transform_one_value(decimal_value_deserialised_none, DATA["id"])
        assert isinstance(val, DecimalValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestGeonameValue:
    def test_corr(self, geoname_value_deserialised_corr: GeonameValueDeserialised) -> None:
        val = _transform_one_value(geoname_value_deserialised_corr, DATA["id"])
        assert isinstance(val, GeonameValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname")
        assert val.object_value == Literal("1241345", datatype=XSD.string)

    def test_none(self, geoname_value_deserialised_none: GeonameValueDeserialised) -> None:
        val = _transform_one_value(geoname_value_deserialised_none, DATA["id"])
        assert isinstance(val, GeonameValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestIntValue:
    def test_corr(self, int_value_deserialised_corr: IntValueDeserialised) -> None:
        val = _transform_one_value(int_value_deserialised_corr, DATA["id"])
        assert isinstance(val, IntValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText")
        assert val.object_value == Literal("1", datatype=XSD.integer)

    def test_none(self, int_value_deserialised_none: IntValueDeserialised) -> None:
        val = _transform_one_value(int_value_deserialised_none, DATA["id"])
        assert isinstance(val, IntValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestLinkValue:
    def test_corr(self, link_value_deserialised_corr: LinkValueDeserialised) -> None:
        val = _transform_one_value(link_value_deserialised_corr, DATA["id"])
        assert isinstance(val, LinkValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo")
        assert val.object_value == DATA["link-id"]

    def test_none(self, link_value_deserialised_none: LinkValueDeserialised) -> None:
        val = _transform_one_value(link_value_deserialised_none, DATA["id"])
        assert isinstance(val, LinkValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo")
        assert val.object_value == DATA[""]


class TestListValue:
    def test_corr(self, list_value_deserialised_corr: ListValueDeserialised) -> None:
        val = _transform_one_value(list_value_deserialised_corr, DATA["id"])
        assert isinstance(val, ListValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp")
        assert val.list_name == Literal("firstList", datatype=XSD.string)
        assert val.object_value == Literal("n1", datatype=XSD.string)

    def test_none(self, list_value_deserialised_none: ListValueDeserialised) -> None:
        val = _transform_one_value(list_value_deserialised_none, DATA["id"])
        assert isinstance(val, ListValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp")
        assert val.list_name == Literal("firstList", datatype=XSD.string)
        assert val.object_value == Literal("", datatype=XSD.string)


class TestSimpleTextValue:
    def test_corr(self, simple_text_deserialised_corr: SimpleTextDeserialised) -> None:
        val = _transform_one_value(simple_text_deserialised_corr, DATA["id"])
        assert isinstance(val, SimpleTextRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea")
        assert val.object_value == Literal("simple text", datatype=XSD.string)

    def test_none(self, simple_text_deserialised_none: SimpleTextDeserialised) -> None:
        val = _transform_one_value(simple_text_deserialised_none, DATA["id"])
        assert isinstance(val, SimpleTextRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestRichtextValue:
    def test_corr(self, richtext_deserialised_corr: RichtextDeserialised) -> None:
        val = _transform_one_value(richtext_deserialised_corr, DATA["id"])
        assert isinstance(val, RichtextRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext")
        assert val.object_value == Literal("rich text", datatype=XSD.string)

    def test_none(self, richtext_deserialised_none: RichtextDeserialised) -> None:
        val = _transform_one_value(richtext_deserialised_none, DATA["id"])
        assert isinstance(val, RichtextRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestTimeValue:
    def test_corr(self, time_value_deserialised_corr: TimeValueDeserialised) -> None:
        val = _transform_one_value(time_value_deserialised_corr, DATA["id"])
        assert isinstance(val, TimeValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue")
        assert val.object_value == Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp)

    def test_none(self, time_value_deserialised_none: TimeValueDeserialised) -> None:
        val = _transform_one_value(time_value_deserialised_none, DATA["id"])
        assert isinstance(val, TimeValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestUriValue:
    def test_corr(self, uri_value_deserialised_corr: UriValueDeserialised) -> None:
        val = _transform_one_value(uri_value_deserialised_corr, DATA["id"])
        assert isinstance(val, UriValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue")
        assert val.object_value == Literal("https://dasch.swiss", datatype=XSD.anyURI)

    def test_none(self, uri_value_deserialised_none: UriValueDeserialised) -> None:
        val = _transform_one_value(uri_value_deserialised_none, DATA["id"])
        assert isinstance(val, UriValueRDF)
        assert val.res_iri == DATA["id"]
        assert val.prop_name == URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue")
        assert val.object_value == Literal("", datatype=XSD.string)


class TestTransformFileValue:
    def test_moving_image(self) -> None:
        bitstream = BitstreamDeserialised("id", "test.mp4")
        result = _transform_file_value(bitstream)
        assert isinstance(result, MovingImageFileValueRDF)
        assert result.value == Literal(bitstream.value)

    def test_other(self) -> None:
        bitstream = BitstreamDeserialised("id", "test.other")
        result = _transform_file_value(bitstream)
        assert not result


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("test.jpg", "jpg"),
        ("test.JPG", "jpg"),
        (None, ""),
        ("test", ""),
    ],
)
def test_get_file_extension(value: str | None, expected: str) -> None:
    assert _get_file_extension(value) == expected


if __name__ == "__main__":
    pytest.main([__file__])
