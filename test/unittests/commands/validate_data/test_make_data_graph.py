# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.rdf_like_data import MigrationMetadata
from dsp_tools.commands.validate_data.models.rdf_like_data import PropertyObject
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeResource
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeValue
from dsp_tools.commands.validate_data.models.rdf_like_data import TripleObjectType
from dsp_tools.commands.validate_data.models.rdf_like_data import TriplePropertyType
from dsp_tools.commands.validate_data.prepare_data.make_data_graph import _make_one_rdflib_object
from dsp_tools.commands.validate_data.prepare_data.make_data_graph import _make_one_resource
from dsp_tools.commands.validate_data.prepare_data.make_data_graph import _make_one_value
from dsp_tools.commands.validate_data.prepare_data.make_data_graph import _make_property_objects_graph
from dsp_tools.utils.rdflib_constants import API_SHAPES
from dsp_tools.utils.rdflib_constants import DATA
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from test.unittests.commands.validate_data.constants import ONTO

LABEL_TRIPLE = PropertyObject(TriplePropertyType.RDFS_LABEL, "lbl", TripleObjectType.STRING)
TYPE_TRIPLE = PropertyObject(
    TriplePropertyType.RDF_TYPE, "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything", TripleObjectType.IRI
)

UNREIFIED_TRIPLE_OBJECTS = [LABEL_TRIPLE, TYPE_TRIPLE]


RES_IRI = DATA["id"]
RESOURCE_TYPE_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"


@pytest.fixture
def rdf_like_boolean_value_corr() -> RdfLikeValue:
    return RdfLikeValue(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "false", KnoraValueType.BOOLEAN_VALUE, []
    )


@pytest.mark.parametrize(
    ("trpl_obj", "object_type", "prop_type", "expected"),
    [
        (
            "1900-20-01",
            TripleObjectType.DATE_YYYY_MM_DD,
            TriplePropertyType.KNORA_DATE_START,
            Literal("1900-20-01", datatype=XSD.string),
        ),
        (
            "9-01-01",
            TripleObjectType.DATE_YYYY_MM_DD,
            TriplePropertyType.KNORA_DATE_START,
            Literal("9-01-01", datatype=XSD.string),
        ),
        (
            "1990-01-50",
            TripleObjectType.DATE_YYYY_MM_DD,
            TriplePropertyType.KNORA_DATE_START,
            Literal("1990-01-50", datatype=XSD.string),
        ),
        (
            "1900-01-01",
            TripleObjectType.DATE_YYYY_MM_DD,
            TriplePropertyType.KNORA_DATE_START,
            Literal("1900-01-01", datatype=XSD.date),
        ),
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
            TripleObjectType.INTERNAL_ID,
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
):
    result = _make_one_rdflib_object(trpl_obj, object_type, prop_type)
    assert result == expected


class TestResource:
    def test_empty(self):
        res = RdfLikeResource(
            res_id="id",
            property_objects=UNREIFIED_TRIPLE_OBJECTS,
            values=[],
            migration_metadata=MigrationMetadata(),
        )
        res_g = _make_one_resource(res)
        assert len(res_g) == 2
        assert next(res_g.objects(RES_IRI, RDF.type)) == ONTO.ClassWithEverything
        assert next(res_g.objects(RES_IRI, RDFS.label)) == Literal("lbl", datatype=XSD.string)

    def test_with_props(self, rdf_like_boolean_value_corr):
        res = RdfLikeResource(
            res_id="id",
            property_objects=UNREIFIED_TRIPLE_OBJECTS,
            values=[rdf_like_boolean_value_corr],
            migration_metadata=MigrationMetadata(),
        )
        res_g = _make_one_resource(res)
        assert len(res_g) == 5
        assert next(res_g.objects(RES_IRI, RDF.type)) == ONTO.ClassWithEverything
        assert next(res_g.objects(RES_IRI, RDFS.label)) == Literal("lbl", datatype=XSD.string)
        bool_bn = next(res_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(res_g.objects(bool_bn, KNORA_API.booleanValueAsBoolean)) == Literal(False, datatype=XSD.boolean)


class TestBooleanValue:
    def test_corr(self, rdf_like_boolean_value_corr):
        val_g = _make_one_value(rdf_like_boolean_value_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("false", datatype=XSD.boolean)

    def test_one(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "1", KnoraValueType.BOOLEAN_VALUE, []
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("true", datatype=XSD.boolean)

    def test_zero(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "0", KnoraValueType.BOOLEAN_VALUE, []
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("false", datatype=XSD.boolean)


class TestColorValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testColor", "#00ff00", KnoraValueType.COLOR_VALUE, []
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testColor))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ColorValue
        assert next(val_g.objects(bn, KNORA_API.colorValueAsColor)) == Literal("#00ff00", datatype=XSD.string)


class TestDateValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1",
            "JULIAN:BCE:0700:BCE:0600",
            KnoraValueType.DATE_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testSubDate1))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DateValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal(
            "JULIAN:BCE:0700:BCE:0600", datatype=XSD.string
        )

    def test_with_date_range_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1",
            "GREGORIAN:CE:1900:CE:2000",
            KnoraValueType.DATE_VALUE,
            [
                PropertyObject(TriplePropertyType.KNORA_DATE_START, "1900-01-01", TripleObjectType.DATE_YYYY_MM_DD),
                PropertyObject(TriplePropertyType.KNORA_DATE_END, "2000-01-01", TripleObjectType.DATE_YYYY_MM_DD),
            ],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 5
        bn = next(val_g.objects(RES_IRI, ONTO.testSubDate1))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DateValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal(
            "GREGORIAN:CE:1900:CE:2000", datatype=XSD.string
        )
        assert next(val_g.objects(bn, API_SHAPES.dateHasStart)) == Literal("1900-01-01", datatype=XSD.date)
        assert next(val_g.objects(bn, API_SHAPES.dateHasEnd)) == Literal("2000-01-01", datatype=XSD.date)

    def test_with_date_range_invalid_date(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1",
            "GREGORIAN:CE:1900:CE:2000-50",
            KnoraValueType.DATE_VALUE,
            [
                PropertyObject(TriplePropertyType.KNORA_DATE_START, "1900-01-01", TripleObjectType.DATE_YYYY_MM_DD),
                PropertyObject(TriplePropertyType.KNORA_DATE_END, "2000-50-01", TripleObjectType.DATE_YYYY_MM_DD),
            ],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 5
        bn = next(val_g.objects(RES_IRI, ONTO.testSubDate1))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DateValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal(
            "GREGORIAN:CE:1900:CE:2000-50", datatype=XSD.string
        )
        assert next(val_g.objects(bn, API_SHAPES.dateHasStart)) == Literal("1900-01-01", datatype=XSD.date)
        assert next(val_g.objects(bn, API_SHAPES.dateHasEnd)) == Literal("2000-50-01", datatype=XSD.string)


class TestDecimalValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText",
            "1.2",
            KnoraValueType.DECIMAL_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testDecimalSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DecimalValue
        assert next(val_g.objects(bn, KNORA_API.decimalValueAsDecimal)) == Literal("1.2", datatype=XSD.decimal)


class TestGeonameValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname",
            "1241345",
            KnoraValueType.GEONAME_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testGeoname))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.GeonameValue
        assert next(val_g.objects(bn, KNORA_API.geonameValueAsGeonameCode)) == Literal("1241345", datatype=XSD.string)


class TestIntValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText",
            "1",
            KnoraValueType.INT_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testIntegerSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.IntValue
        assert next(val_g.objects(bn, KNORA_API.intValueAsInt)) == Literal("1", datatype=XSD.integer)


class TestIntervalValue:
    def test_corr(self):
        seg_start = PropertyObject(TriplePropertyType.KNORA_INTERVAL_START, "1", TripleObjectType.DECIMAL)
        seg_end = PropertyObject(TriplePropertyType.KNORA_INTERVAL_END, "2", TripleObjectType.DECIMAL)
        val = RdfLikeValue(
            user_facing_prop=f"{KNORA_API_STR}hasSegmentBounds",
            user_facing_value=None,
            knora_type=KnoraValueType.INTERVAL_VALUE,
            value_metadata=[seg_start, seg_end],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 4
        bn = next(val_g.objects(RES_IRI, KNORA_API.hasSegmentBounds))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.IntervalValue
        assert next(val_g.objects(bn, KNORA_API.intervalValueHasStart)) == Literal("1", datatype=XSD.decimal)
        assert next(val_g.objects(bn, KNORA_API.intervalValueHasEnd)) == Literal("2", datatype=XSD.decimal)


class TestLinkValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo",
            "link-id",
            KnoraValueType.LINK_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testHasLinkTo))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.LinkValue
        assert next(val_g.objects(bn, API_SHAPES.linkValueHasTargetID)) == DATA["link-id"]

    def test_none(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo", None, KnoraValueType.LINK_VALUE, []
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testHasLinkTo))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.LinkValue
        assert next(val_g.objects(bn, API_SHAPES.linkValueHasTargetID)) == DATA[""]


class TestListValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp", "n1", KnoraValueType.LIST_VALUE, []
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testListProp))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ListValue
        assert next(val_g.objects(bn, KNORA_API.listValueAsListNode)) == Literal("n1", datatype=XSD.string)


class TestSimpleTextValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea",
            "simple text",
            KnoraValueType.SIMPLETEXT_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTextarea))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal("simple text", datatype=XSD.string)


class TestRichtextValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext",
            "rich text",
            KnoraValueType.RICHTEXT_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testRichtext))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.textValueAsXml)) == Literal("rich text", datatype=XSD.string)


class TestTimeValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue",
            "2019-10-23T13:45:12.01-14:00",
            KnoraValueType.TIME_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTimeValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TimeValue
        assert next(val_g.objects(bn, KNORA_API.timeValueAsTimeStamp)) == Literal(
            "2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp
        )


class TestUriValue:
    def test_corr(self):
        val = RdfLikeValue(
            "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue",
            "https://dasch.swiss",
            KnoraValueType.URI_VALUE,
            [],
        )
        val_g = _make_one_value(val, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testUriValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.UriValue
        assert next(val_g.objects(bn, KNORA_API.uriValueAsUri)) == Literal("https://dasch.swiss", datatype=XSD.anyURI)


def test_make_property_objects_graph():
    test_prop_obj = PropertyObject(TriplePropertyType.RDF_TYPE, RESOURCE_TYPE_STR, TripleObjectType.IRI)
    graph = _make_property_objects_graph([test_prop_obj], RES_IRI)
    assert len(graph) == 1
    assert next(graph.objects(RES_IRI, RDF.type)) == URIRef(RESOURCE_TYPE_STR)


class TestFileValue:
    def test_make_file_value_graph_real_file(self):
        file_value = RdfLikeValue(
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

    def test_make_file_value_graph_iiif_uri(self):
        uri = "https://iiif.wellcomecollection.org/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/max/0/default.jpg"
        file_value = RdfLikeValue(
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
