import pytest
import regex
from lxml import etree
from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.lookup_models import JSONLDContext
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.transform_resource_and_values_for_upload import KNORA_API
from dsp_tools.commands.xmlupload.transform_resource_and_values_for_upload import _make_one_prop_graph
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import PermissionNotExistsError
from dsp_tools.models.exceptions import UserError

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
namespaces = {"onto": ONTO, "knora-api": KNORA_API}

PERMISSION_LITERAL = Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)
RES_ONE_URI = URIRef("http://rdfh.ch/9999/res_one")


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


@pytest.fixture
def res_info() -> tuple[BNode, str]:
    return BNode(), "restype"


class TestMakeOnePropGraphSuccess:
    def test_boolean(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <boolean-prop name=":isTrueOrFalse">
            <boolean permissions="open">true</boolean>
        </boolean-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "boolean", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 4
        assert prop_name == ONTO.isTrueOrFalse
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.BooleanValue
        value = next(result.objects(val_bn, KNORA_API.booleanValueAsBoolean))
        assert value == Literal(True, datatype=XSD.boolean)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_color(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <color-prop name=":hasColor">
            <color>#5d1f1e</color>
        </color-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "color", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasColor
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.ColorValue
        value = next(result.objects(val_bn, KNORA_API.colorValueAsColor))
        assert value == Literal("#5d1f1e", datatype=XSD.string)

    def test_decimal(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <decimal-prop name=":hasDecimal">
            <decimal comment="Eulersche Zahl">2.718281828459</decimal>
        </decimal-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "decimal", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 4
        assert prop_name == ONTO.hasDecimal
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.DecimalValue
        value = next(result.objects(val_bn, KNORA_API.decimalValueAsDecimal))
        assert value == Literal("2.718281828459", datatype=XSD.decimal)
        comment = next(result.objects(val_bn, KNORA_API.valueHasComment))
        assert comment == Literal("Eulersche Zahl", datatype=XSD.string)

    def test_geometry(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <geometry-prop name=":hasGeometry">
            <geometry>
                {
                    "status": "active",
                    "type": "polygon",
                    "lineWidth": 5,
                    "points": [{"x": 0.4, "y": 0.6},
                               {"x": 0.5, "y": 0.9},
                               {"x": 0.8, "y": 0.9},
                               {"x": 0.7, "y": 0.6}]
                }
            </geometry>
        </geometry-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "geometry", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasGeometry
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.GeomValue
        value = next(result.objects(val_bn, KNORA_API.geometryValueAsGeometry))
        assert isinstance(value, Literal)

    def test_geoname(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <geoname-prop name=":hasGeoname">
            <geoname>5416656</geoname>
        </geoname-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "geoname", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasGeoname
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.GeonameValue
        value = next(result.objects(val_bn, KNORA_API.geonameValueAsGeonameCode))
        assert value == Literal("5416656", datatype=XSD.string)

    def test_integer(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <integer-prop name=":hasInteger">
            <integer comment="comment">1</integer>
            <integer>2</integer>
        </integer-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "integer", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 7
        assert prop_name == ONTO.hasInteger

        val_one = next(result.subjects(KNORA_API.intValueAsInt, Literal("1", datatype=XSD.integer)))
        assert next(result.objects(val_one, RDF.type)) == KNORA_API.IntValue
        assert next(result.subjects(prop_name, val_one)) == res_bn
        comment = next(result.objects(val_one, KNORA_API.valueHasComment))
        assert comment == Literal("comment", datatype=XSD.string)

        val_two = next(result.subjects(KNORA_API.intValueAsInt, Literal("2", datatype=XSD.integer)))
        assert next(result.objects(val_two, RDF.type)) == KNORA_API.IntValue
        assert next(result.subjects(prop_name, val_two)) == res_bn

    def test_time(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <time-prop name=":hasTime">
            <time>2019-10-23T13:45:12.01-14:00</time>
        </time-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "time", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasTime
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.TimeValue
        value = next(result.objects(val_bn, KNORA_API.timeValueAsTimeStamp))
        assert value == Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp)

    def test_uri(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <uri-prop name=":hasUri">
            <uri>https://dasch.swiss</uri>
        </uri-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "uri", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasUri
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.UriValue
        value = next(result.objects(val_bn, KNORA_API.uriValueAsUri))
        assert value == Literal("https://dasch.swiss", datatype=XSD.anyURI)

    def test_list(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <list-prop list="testlist" name=":hasListItem">
            <list>node</list>
        </list-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "list", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasListItem
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.ListValue
        value = next(result.objects(val_bn, KNORA_API.listValueAsListNode))
        assert value == URIRef("http://rdfh.ch/9999/node")

    def test_resptr(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <resptr-prop name=":hasResource">
            <resptr>res_one</resptr>
        </resptr-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "resptr", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasResourceValue
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.LinkValue
        value = next(result.objects(val_bn, KNORA_API.linkValueHasTargetIri))
        assert value == RES_ONE_URI

    def test_simpletext(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <text-prop name=":hasSimpleText">
            <text encoding="utf8">Text</text>
        </text-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "text", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == ONTO.hasSimpleText
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.TextValue
        value = next(result.objects(val_bn, KNORA_API.valueAsString))
        assert value == Literal("Text", datatype=XSD.string)

    def test_richtext(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <text-prop name=":hasRichtext">
            <text permissions="open" encoding="xml">Text</text>
        </text-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "text", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
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

    def test_date(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <date-prop name=":hasDate">
            <date>GREGORIAN:AD:0476-09-04:0477</date>
        </date-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "date", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
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

    def test_interval(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <hasSegmentBounds segment_start="0.1" segment_end="0.234"/>
        """)
        prop = XMLProperty.from_node(xml_prop, "interval", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 4
        assert prop_name == KNORA_API.hasSegmentBounds
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.IntervalValue
        start = next(result.objects(val_bn, KNORA_API.intervalValueHasStart))
        assert start == Literal("0.1", datatype=XSD.decimal)
        end = next(result.objects(val_bn, KNORA_API.intervalValueHasEnd))
        assert end == Literal("0.234", datatype=XSD.decimal)

    def test_segment_of_video(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, _ = res_info
        res_type = "knora-api:VideoSegment"
        xml_prop = etree.fromstring("""
        <isSegmentOf >res_one</isSegmentOf>
        """)
        prop = XMLProperty.from_node(xml_prop, "resptr", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == KNORA_API.isVideoSegmentOfValue
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.LinkValue
        value = next(result.objects(val_bn, KNORA_API.linkValueHasTargetIri))
        assert value == RES_ONE_URI

    def test_segment_of_audio(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, _ = res_info
        res_type = "knora-api:AudioSegment"
        xml_prop = etree.fromstring("""
        <isSegmentOf >res_one</isSegmentOf>
        """)
        prop = XMLProperty.from_node(xml_prop, "resptr", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 3
        assert prop_name == KNORA_API.isAudioSegmentOfValue
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.LinkValue
        value = next(result.objects(val_bn, KNORA_API.linkValueHasTargetIri))
        assert value == RES_ONE_URI


class TestMakeOnePropGraphRaises:
    def test_permissions(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <integer-prop name=":hasInteger">
            <integer permissions="nonExistent">4711</integer>
        </integer-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "integer", "onto")
        err_str = regex.escape("Could not find permissions for value: nonExistent")
        with pytest.raises(PermissionNotExistsError, match=err_str):
            _make_one_prop_graph(prop, res_type, res_bn, lookups)

    def test_unknown_type(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <other-prop name=":hasInteger">
            <other>4711</other>
        </other-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "other", "onto")
        err_str = regex.escape("Unknown value type: other")
        with pytest.raises(UserError, match=err_str):
            _make_one_prop_graph(prop, res_type, res_bn, lookups)

    def test_unknown_prefix(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <integer-prop name="other:hasInteger">
            <integer>4711</integer>
        </integer-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "integer", "onto")
        err_str = regex.escape("Could not find namespace for prefix: other")
        with pytest.raises(InputError, match=err_str):
            _make_one_prop_graph(prop, res_type, res_bn, lookups)

    def test_link_traget_not_found(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <resptr-prop name=":hasResource">
            <resptr>non_existing</resptr>
        </resptr-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "resptr", "onto")
        err_str = regex.escape(
            (
                "Could not find the ID non_existing in the id2iri mapping. "
                "This is probably because the resource 'non_existing' could not be created. "
                "See warnings.log for more information."
            )
        )
        with pytest.raises(BaseError, match=err_str):
            _make_one_prop_graph(prop, res_type, res_bn, lookups)

    def test_list_node_not_found(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <list-prop list="testlist" name=":hasListItem">
            <list>other</list>
        </list-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "list", "onto")
        err_str = regex.escape(
            (
                "Could not resolve list node ID 'testlist:other' to IRI. "
                "This is probably because the list node 'testlist:other' does not exist on the server."
            )
        )
        with pytest.raises(BaseError, match=err_str):
            _make_one_prop_graph(prop, res_type, res_bn, lookups)
