import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Literal
from rdflib import URIRef
from rdflib.term import Node

from dsp_tools.commands.validate_data.make_data_rdf import _make_file_value
from dsp_tools.commands.validate_data.make_data_rdf import _make_one_rdflib_object
from dsp_tools.commands.validate_data.make_data_rdf import _make_one_resource
from dsp_tools.commands.validate_data.make_data_rdf import _make_one_value
from dsp_tools.commands.validate_data.models.data_deserialised import BitstreamDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IIIFUriDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ObjectTypes
from dsp_tools.commands.validate_data.models.data_deserialised import PropertyObject
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import UriValueDeserialised
from test.unittests.commands.validate_data.constants import API_SHAPES
from test.unittests.commands.validate_data.constants import DATA
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO

RES_IRI = DATA["id"]


@pytest.mark.parametrize(
    "property_object, expected",
    [
        (
            PropertyObject("", "true", ObjectTypes.boolean),
            Literal("true", datatype=XSD.boolean),
        ),
        (
            PropertyObject("", "2019-10-23T13:45:12.01-14:00", ObjectTypes.datetime),
            Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp),
        ),
        (
            PropertyObject("", "1.5", ObjectTypes.decimal),
            Literal("1.5", datatype=XSD.decimal),
        ),
        (
            PropertyObject("", "1", ObjectTypes.integer),
            Literal("1", datatype=XSD.integer),
        ),
        (
            PropertyObject("", "string", ObjectTypes.string),
            Literal("string", datatype=XSD.string),
        ),
        (
            PropertyObject("", "https://dasch.swiss", ObjectTypes.uri),
            Literal("https://dasch.swiss", datatype=XSD.anyURI),
        ),
        (
            PropertyObject("", RES_IRI, ObjectTypes.iri),
            URIRef(RES_IRI),
        ),
        (
            PropertyObject("", None, ObjectTypes.boolean),
            Literal("", datatype=XSD.string),
        ),
    ],
)
def test_make_one_rdflib_object(property_object: PropertyObject, expected: Node) -> None:
    result = _make_one_rdflib_object(property_object)
    assert result == expected


class TestResource:
    def test_empty(self, resource_deserialised_no_values: ResourceDeserialised) -> None:
        res_g = _make_one_resource(resource_deserialised_no_values)
        assert len(res_g) == 2
        assert next(res_g.objects(RES_IRI, RDF.type)) == ONTO.ClassWithEverything
        assert next(res_g.objects(RES_IRI, RDFS.label)) == Literal("lbl", datatype=XSD.string)

    def test_with_props(self, resource_deserialised_with_values: ResourceDeserialised) -> None:
        res_g = _make_one_resource(resource_deserialised_with_values)
        assert len(res_g) == 5
        assert next(res_g.objects(RES_IRI, RDF.type)) == ONTO.ClassWithEverything
        assert next(res_g.objects(RES_IRI, RDFS.label)) == Literal("lbl", datatype=XSD.string)
        bool_bn = next(res_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(res_g.objects(bool_bn, KNORA_API.booleanValueAsBoolean)) == Literal(False, datatype=XSD.boolean)


class TestBooleanValue:
    def test_corr(self, boolean_value_deserialised_corr: BooleanValueDeserialised) -> None:
        val_g = _make_one_value(boolean_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("false", datatype=XSD.boolean)

    def test_one(self, boolean_value_deserialised_one: BooleanValueDeserialised) -> None:
        val_g = _make_one_value(boolean_value_deserialised_one, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("true", datatype=XSD.boolean)

    def test_zero(self, boolean_value_deserialised_zero: BooleanValueDeserialised) -> None:
        val_g = _make_one_value(boolean_value_deserialised_zero, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("false", datatype=XSD.boolean)

    def test_none(self, boolean_value_deserialised_none: BooleanValueDeserialised) -> None:
        val_g = _make_one_value(boolean_value_deserialised_none, RES_IRI)
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("", datatype=XSD.string)


class TestColorValue:
    def test_corr(self, color_value_deserialised_corr: ColorValueDeserialised) -> None:
        val_g = _make_one_value(color_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testColor))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ColorValue
        assert next(val_g.objects(bn, KNORA_API.colorValueAsColor)) == Literal("#00ff00", datatype=XSD.string)

    def test_none(self, color_value_deserialised_none: ColorValueDeserialised) -> None:
        val_g = _make_one_value(color_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testColor))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ColorValue
        assert next(val_g.objects(bn, KNORA_API.colorValueAsColor)) == Literal("", datatype=XSD.string)


class TestDateValue:
    def test_corr(self, date_value_deserialised_corr: DateValueDeserialised) -> None:
        val_g = _make_one_value(date_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testSubDate1))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DateValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal(
            "JULIAN:BCE:0700:BCE:0600", datatype=XSD.string
        )

    def test_none(self, date_value_deserialised_none: DateValueDeserialised) -> None:
        val_g = _make_one_value(date_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testSubDate1))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DateValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal("", datatype=XSD.string)


class TestDecimalValue:
    def test_corr(self, decimal_value_deserialised_corr: DecimalValueDeserialised) -> None:
        val_g = _make_one_value(decimal_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testDecimalSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DecimalValue
        assert next(val_g.objects(bn, KNORA_API.decimalValueAsDecimal)) == Literal("1.2", datatype=XSD.decimal)

    def test_none(self, decimal_value_deserialised_none: DecimalValueDeserialised) -> None:
        val_g = _make_one_value(decimal_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testDecimalSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DecimalValue
        assert next(val_g.objects(bn, KNORA_API.decimalValueAsDecimal)) == Literal("", datatype=XSD.string)


class TestGeonameValue:
    def test_corr(self, geoname_value_deserialised_corr: GeonameValueDeserialised) -> None:
        val_g = _make_one_value(geoname_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testGeoname))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.GeonameValue
        assert next(val_g.objects(bn, KNORA_API.geonameValueAsGeonameCode)) == Literal("1241345", datatype=XSD.string)

    def test_none(self, geoname_value_deserialised_none: GeonameValueDeserialised) -> None:
        val_g = _make_one_value(geoname_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testGeoname))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.GeonameValue
        assert next(val_g.objects(bn, KNORA_API.geonameValueAsGeonameCode)) == Literal("", datatype=XSD.string)


class TestIntValue:
    def test_corr(self, int_value_deserialised_corr: IntValueDeserialised) -> None:
        val_g = _make_one_value(int_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testIntegerSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.IntValue
        assert next(val_g.objects(bn, KNORA_API.intValueAsInt)) == Literal("1", datatype=XSD.integer)

    def test_none(self, int_value_deserialised_none: IntValueDeserialised) -> None:
        val_g = _make_one_value(int_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testIntegerSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.IntValue
        assert next(val_g.objects(bn, KNORA_API.intValueAsInt)) == Literal("", datatype=XSD.string)


class TestLinkValue:
    def test_corr(self, link_value_deserialised_corr: LinkValueDeserialised) -> None:
        val_g = _make_one_value(link_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testHasLinkTo))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.LinkValue
        assert next(val_g.objects(bn, API_SHAPES.linkValueHasTargetID)) == DATA["link-id"]

    def test_none(self, link_value_deserialised_none: LinkValueDeserialised) -> None:
        val_g = _make_one_value(link_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testHasLinkTo))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.LinkValue
        assert next(val_g.objects(bn, API_SHAPES.linkValueHasTargetID)) == DATA[""]


class TestListValue:
    def test_corr(self, list_value_deserialised_corr: ListValueDeserialised) -> None:
        val_g = _make_one_value(list_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 4
        bn = next(val_g.objects(RES_IRI, ONTO.testListProp))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ListValue
        assert next(val_g.objects(bn, API_SHAPES.listNodeAsString)) == Literal("n1", datatype=XSD.string)
        assert next(val_g.objects(bn, API_SHAPES.listNameAsString)) == Literal("firstList", datatype=XSD.string)

    def test_none(self, list_value_deserialised_none: ListValueDeserialised) -> None:
        val_g = _make_one_value(list_value_deserialised_none, RES_IRI)
        assert len(val_g) == 4
        bn = next(val_g.objects(RES_IRI, ONTO.testListProp))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ListValue
        assert next(val_g.objects(bn, API_SHAPES.listNodeAsString)) == Literal("", datatype=XSD.string)
        assert next(val_g.objects(bn, API_SHAPES.listNameAsString)) == Literal("firstList", datatype=XSD.string)


class TestSimpleTextValue:
    def test_corr(self, simple_text_deserialised_corr: SimpleTextDeserialised) -> None:
        val_g = _make_one_value(simple_text_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTextarea))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal("simple text", datatype=XSD.string)

    def test_none(self, simple_text_deserialised_none: SimpleTextDeserialised) -> None:
        val_g = _make_one_value(simple_text_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTextarea))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal("", datatype=XSD.string)


class TestRichtextValue:
    def test_corr(self, richtext_deserialised_corr: RichtextDeserialised) -> None:
        val_g = _make_one_value(richtext_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testRichtext))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.textValueAsXml)) == Literal("rich text", datatype=XSD.string)

    def test_none(self, richtext_deserialised_none: RichtextDeserialised) -> None:
        val_g = _make_one_value(richtext_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testRichtext))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.textValueAsXml)) == Literal("", datatype=XSD.string)


class TestTimeValue:
    def test_corr(self, time_value_deserialised_corr: TimeValueDeserialised) -> None:
        val_g = _make_one_value(time_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTimeValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TimeValue
        assert next(val_g.objects(bn, KNORA_API.timeValueAsTimeStamp)) == Literal(
            "2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp
        )

    def test_none(self, time_value_deserialised_none: TimeValueDeserialised) -> None:
        val_g = _make_one_value(time_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTimeValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TimeValue
        assert next(val_g.objects(bn, KNORA_API.timeValueAsTimeStamp)) == Literal("", datatype=XSD.string)


class TestUriValue:
    def test_corr(self, uri_value_deserialised_corr: UriValueDeserialised) -> None:
        val_g = _make_one_value(uri_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testUriValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.UriValue
        assert next(val_g.objects(bn, KNORA_API.uriValueAsUri)) == Literal("https://dasch.swiss", datatype=XSD.anyURI)

    def test_none(self, uri_value_deserialised_none: UriValueDeserialised) -> None:
        val_g = _make_one_value(uri_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testUriValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.UriValue
        assert next(val_g.objects(bn, KNORA_API.uriValueAsUri)) == Literal("", datatype=XSD.string)


class TestTransformFileValue:
    def test_make_file_value_graph_real_file(self) -> None:
        bitstream = BitstreamDeserialised("id", "test.zip")
        file_g = _make_file_value(bitstream)
        assert len(file_g) == 3
        bn = next(file_g.objects(RES_IRI, KNORA_API.hasArchiveFileValue))
        assert next(file_g.objects(bn, RDF.type)) == KNORA_API.ArchiveFileValue
        assert next(file_g.objects(bn, KNORA_API.fileValueHasFilename)) == Literal("test.zip", datatype=XSD.string)

    def test_make_file_value_graph_iiif_uri(self) -> None:
        uri = "https://iiif.wellcomecollection.org/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/max/0/default.jpg"
        iiif = IIIFUriDeserialised("id", uri)
        file_g = _make_file_value(iiif)
        assert len(file_g) == 3
        bn = next(file_g.objects(RES_IRI, KNORA_API.hasStillImageFileValue))
        assert next(file_g.objects(bn, RDF.type)) == KNORA_API.StillImageExternalFileValue
        assert next(file_g.objects(bn, KNORA_API.stillImageFileValueHasExternalUrl)) == Literal(
            uri, datatype=XSD.anyURI
        )

    def test_none(self) -> None:
        bitstream = BitstreamDeserialised("id", None)
        result = _make_file_value(bitstream)
        assert len(result) == 0

    def test_other(self) -> None:
        bitstream = BitstreamDeserialised("id", "test.other")
        result = _make_file_value(bitstream)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__])
