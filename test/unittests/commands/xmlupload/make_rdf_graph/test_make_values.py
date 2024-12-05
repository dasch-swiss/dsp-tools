import pytest
import regex
from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import KNORA_API
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import _make_one_prop_graph
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryColor
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDate
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDecimal
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeometry
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeoname
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInt
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInterval
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryList
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryTime
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryUri
from dsp_tools.commands.xmlupload.models.intermediary.values import IntervalFloats
from dsp_tools.commands.xmlupload.models.lookup_models import JSONLDContext
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.date_util import Calendar
from dsp_tools.utils.date_util import Date
from dsp_tools.utils.date_util import Era
from dsp_tools.utils.date_util import SingleDate

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
namespaces = {"onto": ONTO, "knora-api": KNORA_API}

PERMISSION_LITERAL = Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)
RES_ONE_URI = URIRef("http://rdfh.ch/9999/res_one")


def onto_str(prop: str) -> str:
    return f"http://0.0.0.0:3333/ontology/9999/onto/v2#{prop}"


@pytest.fixture
def permissions_lookup() -> dict[str, Permissions]:
    return {"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})}


@pytest.fixture
def lookups(permissions_lookup: dict[str, Permissions]) -> Lookups:
    return Lookups(
        project_iri="http://rdfh.ch/9999/project",
        id_to_iri=IriResolver({"res_one": "http://rdfh.ch/9999/res_one"}),
        permissions=permissions_lookup,
        listnodes={"testlist:node": "http://rdfh.ch/9999/node"},
        namespaces=namespaces,
        jsonld_context=JSONLDContext({}),
    )


class TestMakeOnePropGraphSuccess:
    def test_boolean(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryBoolean(True, onto_str("isTrueOrFalse"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 4
        assert prop_name == ONTO.isTrueOrFalse
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.BooleanValue
        value = next(result.objects(val_bn, KNORA_API.booleanValueAsBoolean))
        assert value == Literal(True, datatype=XSD.boolean)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_color(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryColor("#5d1f1e", onto_str("hasColor"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasColor
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.ColorValue
        value = next(result.objects(val_bn, KNORA_API.colorValueAsColor))
        assert value == Literal("#5d1f1e", datatype=XSD.string)

    def test_decimal(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryDecimal(2.718281828459, onto_str("hasDecimal"), "Eulersche Zahl", None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 4
        assert prop_name == ONTO.hasDecimal
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.DecimalValue
        value = next(result.objects(val_bn, KNORA_API.decimalValueAsDecimal))
        assert value == Literal("2.718281828459", datatype=XSD.decimal)
        comment = next(result.objects(val_bn, KNORA_API.valueHasComment))
        assert comment == Literal("Eulersche Zahl", datatype=XSD.string)

    def test_geometry(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryGeometry(
            '{"status": "active", "type": "polygon", "lineWidth": 5, '
            '"points": [{"x": 0.4, "y": 0.6}, {"x": 0.5, "y": 0.9}, {"x": 0.8, "y": 0.9}, {"x": 0.7, "y": 0.6}]}',
            onto_str("hasGeometry"),
            None,
            None,
        )
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasGeometry
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.GeomValue
        value = next(result.objects(val_bn, KNORA_API.geometryValueAsGeometry))
        assert isinstance(value, Literal)

    def test_geoname(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryGeoname("5416656", onto_str("hasGeoname"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasGeoname
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.GeonameValue
        value = next(result.objects(val_bn, KNORA_API.geonameValueAsGeonameCode))
        assert value == Literal("5416656", datatype=XSD.string)

    def test_integer(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryInt(1, onto_str("hasInteger"), "comment", None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 4
        assert prop_name == ONTO.hasInteger
        val = next(result.subjects(KNORA_API.intValueAsInt, Literal("1", datatype=XSD.integer)))
        assert next(result.objects(val, RDF.type)) == KNORA_API.IntValue
        assert next(result.subjects(prop_name, val)) == res_bn
        comment = next(result.objects(val, KNORA_API.valueHasComment))
        assert comment == Literal("comment", datatype=XSD.string)

    def test_time(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryTime("2019-10-23T13:45:12.01-14:00", onto_str("hasTime"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasTime
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.TimeValue
        value = next(result.objects(val_bn, KNORA_API.timeValueAsTimeStamp))
        assert value == Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp)

    def test_uri(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryUri("https://dasch.swiss", onto_str("hasUri"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasUri
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.UriValue
        value = next(result.objects(val_bn, KNORA_API.uriValueAsUri))
        assert value == Literal("https://dasch.swiss", datatype=XSD.anyURI)

    def test_list(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryList("http://rdfh.ch/9999/node", onto_str("hasListItem"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasListItem
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.ListValue
        value = next(result.objects(val_bn, KNORA_API.listValueAsListNode))
        assert value == URIRef("http://rdfh.ch/9999/node")

    def test_resptr(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryLink("res_one", onto_str("hasResource"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasResourceValue
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.LinkValue
        value = next(result.objects(val_bn, KNORA_API.linkValueHasTargetIri))
        assert value == RES_ONE_URI

    def test_simpletext(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediarySimpleText("Text", onto_str("hasSimpleText"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasSimpleText
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.TextValue
        value = next(result.objects(val_bn, KNORA_API.valueAsString))
        assert value == Literal("Text", datatype=XSD.string)

    def test_richtext(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryRichtext(FormattedTextValue("Text"), onto_str("hasRichtext"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 5
        assert prop_name == ONTO.hasRichtext
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.TextValue
        value = next(result.objects(val_bn, KNORA_API.textValueAsXml))
        assert value == Literal('<?xml version="1.0" encoding="UTF-8"?>\n<text>Text</text>', datatype=XSD.string)
        mapping = next(result.objects(val_bn, KNORA_API.textValueHasMapping))
        assert mapping == URIRef("http://rdfh.ch/standoff/mappings/StandardMapping")
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_date(self, lookups: Lookups) -> None:
        res_bn = BNode()
        date = Date(
            calendar=Calendar.GREGORIAN,
            start=SingleDate(era=Era.AD, year=476, month=9, day=4),
            end=SingleDate(era=None, year=477, month=None, day=None),
        )
        prop = IntermediaryDate(date, onto_str("hasDate"), None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 9
        assert prop_name == ONTO.hasDate
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.DateValue
        calendar = next(result.objects(val_bn, KNORA_API.dateValueHasCalendar))
        assert calendar == Literal("GREGORIAN", datatype=XSD.string)
        start_day = next(result.objects(val_bn, KNORA_API.dateValueHasStartDay))
        assert start_day == Literal("4", datatype=XSD.integer)
        start_month = next(result.objects(val_bn, KNORA_API.dateValueHasStartMonth))
        assert start_month == Literal("9", datatype=XSD.integer)
        start_year = next(result.objects(val_bn, KNORA_API.dateValueHasStartYear))
        assert start_year == Literal("476", datatype=XSD.integer)
        start_era = next(result.objects(val_bn, KNORA_API.dateValueHasStartEra))
        assert start_era == Literal("AD", datatype=XSD.string)
        end_year = next(result.objects(val_bn, KNORA_API.dateValueHasEndYear))
        assert end_year == Literal("477", datatype=XSD.integer)
        start_era = next(result.objects(val_bn, KNORA_API.dateValueHasEndEra))
        assert start_era == Literal("AD", datatype=XSD.string)

    def test_interval(self, lookups: Lookups) -> None:
        res_bn = BNode()
        interval = IntervalFloats(0.1, 0.234)
        prop = IntermediaryInterval(interval, "http://api.knora.org/ontology/knora-api/v2#hasSegmentBounds", None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 4
        assert prop_name == KNORA_API.hasSegmentBounds
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.IntervalValue
        start = next(result.objects(val_bn, KNORA_API.intervalValueHasStart))
        assert start == Literal("0.1", datatype=XSD.decimal)
        end = next(result.objects(val_bn, KNORA_API.intervalValueHasEnd))
        assert end == Literal("0.234", datatype=XSD.decimal)

    def test_segment_of_video(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryLink("res_one", "http://api.knora.org/ontology/knora-api/v2#isVideoSegmentOf", None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == KNORA_API.isVideoSegmentOfValue
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.LinkValue
        value = next(result.objects(val_bn, KNORA_API.linkValueHasTargetIri))
        assert value == RES_ONE_URI

    def test_segment_of_audio(self, lookups: Lookups) -> None:
        res_bn = BNode()
        prop = IntermediaryLink("res_one", "http://api.knora.org/ontology/knora-api/v2#isAudioSegmentOf", None, None)
        result, prop_name = _make_one_prop_graph(prop, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == KNORA_API.isAudioSegmentOfValue
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.LinkValue
        value = next(result.objects(val_bn, KNORA_API.linkValueHasTargetIri))
        assert value == RES_ONE_URI


def test_link_traget_not_found(lookups: Lookups) -> None:
    res_bn = BNode()
    prop = IntermediaryLink("non_existing", onto_str("hasResource"), None, None)
    err_str = regex.escape(
        (
            "Could not find the ID non_existing in the id2iri mapping. "
            "This is probably because the resource 'non_existing' could not be created. "
            "See warnings.log for more information."
        )
    )
    with pytest.raises(BaseError, match=err_str):
        _make_one_prop_graph(prop, res_bn, lookups)
