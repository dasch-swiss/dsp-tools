import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.constants import KNORA_API_STR
from dsp_tools.commands.validate_data.constants import SubjectObjectTypeAlias
from dsp_tools.commands.validate_data.make_data_rdf import _make_one_rdflib_object
from dsp_tools.commands.validate_data.make_data_rdf import _make_one_resource
from dsp_tools.commands.validate_data.make_data_rdf import _make_one_value
from dsp_tools.commands.validate_data.make_data_rdf import _make_property_objects_graph
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation
from test.unittests.commands.validate_data.constants import API_SHAPES
from test.unittests.commands.validate_data.constants import DATA
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO

RES_IRI = DATA["id"]
RESOURCE_TYPE_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"


@pytest.mark.parametrize(
    ("trpl_obj", "object_type", "prop_type", "expected"),
    [
        (
            "label",
            TripleObjectType.STRING,
            None,
            Literal("label", datatype=XSD.string),
        ),
        (
            RESOURCE_TYPE_STR,
            TripleObjectType.IRI,
            None,
            URIRef(RESOURCE_TYPE_STR),
        ),
        (
            None,
            TripleObjectType.IRI,
            None,
            Literal("", datatype=XSD.string),
        ),
        (
            "res_id",
            TripleObjectType.IRI,
            TriplePropertyType.KNORA_STANDOFF_LINK,
            DATA.res_id,
        ),
    ],
)
def test_make_one_rdflib_object(
    trpl_obj: str | None,
    object_type: TripleObjectType,
    prop_type: TriplePropertyType | None,
    expected: SubjectObjectTypeAlias,
) -> None:
    result = _make_one_rdflib_object(trpl_obj, object_type, prop_type)
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

    def test_with_asset(self, resource_deserialised_with_asset: ResourceDeserialised) -> None:
        res_g = _make_one_resource(resource_deserialised_with_asset)
        assert len(res_g) == 5
        assert next(res_g.objects(RES_IRI, RDF.type)) == ONTO.ClassWithEverything
        assert next(res_g.objects(RES_IRI, RDFS.label)) == Literal("lbl", datatype=XSD.string)
        bool_bn = next(res_g.objects(RES_IRI, KNORA_API.hasAudioFileValue))
        assert next(res_g.objects(bool_bn, KNORA_API.fileValueHasFilename)) == Literal(
            "testdata/bitstreams/test.wav", datatype=XSD.string
        )


class TestBooleanValue:
    def test_corr(self, boolean_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(boolean_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("false", datatype=XSD.boolean)

    def test_one(self, boolean_value_deserialised_one: ValueInformation) -> None:
        val_g = _make_one_value(boolean_value_deserialised_one, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("true", datatype=XSD.boolean)

    def test_zero(self, boolean_value_deserialised_zero: ValueInformation) -> None:
        val_g = _make_one_value(boolean_value_deserialised_zero, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("false", datatype=XSD.boolean)


class TestColorValue:
    def test_corr(self, color_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(color_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testColor))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ColorValue
        assert next(val_g.objects(bn, KNORA_API.colorValueAsColor)) == Literal("#00ff00", datatype=XSD.string)


class TestDateValue:
    def test_corr(self, date_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(date_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testSubDate1))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DateValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal(
            "JULIAN:BCE:0700:BCE:0600", datatype=XSD.string
        )


class TestDecimalValue:
    def test_corr(self, decimal_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(decimal_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testDecimalSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DecimalValue
        assert next(val_g.objects(bn, KNORA_API.decimalValueAsDecimal)) == Literal("1.2", datatype=XSD.decimal)


class TestGeonameValue:
    def test_corr(self, geoname_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(geoname_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testGeoname))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.GeonameValue
        assert next(val_g.objects(bn, KNORA_API.geonameValueAsGeonameCode)) == Literal("1241345", datatype=XSD.string)


class TestIntValue:
    def test_corr(self, int_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(int_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testIntegerSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.IntValue
        assert next(val_g.objects(bn, KNORA_API.intValueAsInt)) == Literal("1", datatype=XSD.integer)


class TestIntervalValue:
    def test_corr(self, interval_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(interval_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 4
        bn = next(val_g.objects(RES_IRI, KNORA_API.hasSegmentBounds))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.IntervalValue
        assert next(val_g.objects(bn, KNORA_API.intervalValueHasStart)) == Literal("1", datatype=XSD.decimal)
        assert next(val_g.objects(bn, KNORA_API.intervalValueHasEnd)) == Literal("2", datatype=XSD.decimal)


class TestLinkValue:
    def test_corr(self, link_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(link_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testHasLinkTo))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.LinkValue
        assert next(val_g.objects(bn, API_SHAPES.linkValueHasTargetID)) == DATA["link-id"]

    def test_none(self, link_value_deserialised_none: ValueInformation) -> None:
        val_g = _make_one_value(link_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testHasLinkTo))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.LinkValue
        assert next(val_g.objects(bn, API_SHAPES.linkValueHasTargetID)) == DATA[""]


class TestListValue:
    def test_corr(self, list_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(list_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testListProp))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ListValue
        assert next(val_g.objects(bn, API_SHAPES.listNodeAsString)) == Literal("n1", datatype=XSD.string)


class TestSimpleTextValue:
    def test_corr(self, simple_text_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(simple_text_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTextarea))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal("simple text", datatype=XSD.string)


class TestRichtextValue:
    def test_corr(self, richtext_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(richtext_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testRichtext))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.textValueAsXml)) == Literal("rich text", datatype=XSD.string)


class TestTimeValue:
    def test_corr(self, time_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(time_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTimeValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TimeValue
        assert next(val_g.objects(bn, KNORA_API.timeValueAsTimeStamp)) == Literal(
            "2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp
        )


class TestUriValue:
    def test_corr(self, uri_value_deserialised_corr: ValueInformation) -> None:
        val_g = _make_one_value(uri_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testUriValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.UriValue
        assert next(val_g.objects(bn, KNORA_API.uriValueAsUri)) == Literal("https://dasch.swiss", datatype=XSD.anyURI)


def test_make_property_objects_graph() -> None:
    test_prop_obj = PropertyObject(TriplePropertyType.RDF_TYPE, RESOURCE_TYPE_STR, TripleObjectType.IRI)
    graph = _make_property_objects_graph([test_prop_obj], RES_IRI)
    assert len(graph) == 1
    assert next(graph.objects(RES_IRI, RDF.type)) == URIRef(RESOURCE_TYPE_STR)


class TestTransformFileValue:
    def test_make_file_value_graph_real_file(self) -> None:
        file_value = ValueInformation(
            user_facing_prop=f"{KNORA_API_STR}hasArchiveFileValue",
            user_facing_value="test.zip",
            knora_type=KnoraValueType.ARCHIVE_FILE,
            value_metadata=[],
        )
        file_g = _make_one_value(file_value, RES_IRI)
        assert len(file_g) == 3
        bn = next(file_g.objects(RES_IRI, KNORA_API.hasArchiveFileValue))
        assert next(file_g.objects(bn, RDF.type)) == KNORA_API.ArchiveFileValue
        assert next(file_g.objects(bn, KNORA_API.fileValueHasFilename)) == Literal("test.zip", datatype=XSD.string)

    def test_make_file_value_graph_iiif_uri(self) -> None:
        uri = "https://iiif.wellcomecollection.org/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/max/0/default.jpg"
        file_value = ValueInformation(
            user_facing_prop=f"{KNORA_API_STR}hasStillImageFileValue",
            user_facing_value=uri,
            knora_type=KnoraValueType.STILL_IMAGE_IIIF,
            value_metadata=[],
        )
        file_g = _make_one_value(file_value, RES_IRI)
        assert len(file_g) == 3
        bn = next(file_g.objects(RES_IRI, KNORA_API.hasStillImageFileValue))
        assert next(file_g.objects(bn, RDF.type)) == KNORA_API.StillImageExternalFileValue
        assert next(file_g.objects(bn, KNORA_API.stillImageFileValueHasExternalUrl)) == Literal(
            uri, datatype=XSD.anyURI
        )


if __name__ == "__main__":
    pytest.main([__file__])
