import pytest
from lxml import etree
from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.lookup_models import JSONLDContext
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.transform_resource_and_values_for_upload import KNORA_API
from dsp_tools.commands.xmlupload.transform_resource_and_values_for_upload import _make_one_prop_graph

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
namespaces = {"onto": ONTO, "knora-api": KNORA_API}

PERMISSION_LITERAL = Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)


@pytest.fixture
def permissions_lookup() -> dict[str, Permissions]:
    return {"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})}


@pytest.fixture
def lookups(permissions_lookup: dict[str, Permissions]) -> Lookups:
    return Lookups(
        project_iri="http://rdfh.ch/9999/project",
        id_to_iri=IriResolver({"res_one": "http://rdfh.ch/9999/res_one"}),
        permissions=permissions_lookup,
        listnodes={"node": "http://rdfh.ch/9999/node"},
        namespaces=namespaces,
        jsonld_context=JSONLDContext({}),
    )


@pytest.fixture
def res_info() -> tuple[BNode, str]:
    return BNode(), "restype"


class TestMakeOnePropGraph:
    def test_boolean_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
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

    def test_color_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
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

    def test_decimal_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
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

    def test_geometry_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
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

    def test_geoname_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
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

    def test_integer_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <integer-prop name=":hasInteger">
            <integer>4711</integer>
        </integer-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "integer", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_time_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <time-prop name=":hasTime">
            <time>2019-10-23T13:45:12.01-14:00</time>
        </time-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "time", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_uri_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <uri-prop name=":hasUri">
            <uri>https://dasch.swiss</uri>
        </uri-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "uri", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_list_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <list-prop list="testlist" name=":hasListItem">
            <list>node</list>
        </list-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "list", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_resptr_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <resptr-prop name=":hasResource">
            <resptr>res_one</resptr>
        </resptr-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "resptr", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_simpletext_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <text-prop name=":hasSimpleText">
            <text encoding="utf8">Text</text>
        </text-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "text", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_richtext_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <text-prop name=":hasRichtext">
            <text encoding="xml">Text</text>
        </text-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "text", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_date_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <date-prop name=":hasDate">
            <date>GREGORIAN:AD:0476-09-04:AD:0477</date>
        </date-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "date", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_interval_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <hasSegmentBounds segment_start="0.1" segment_end="0.234"/>
        """)
        prop = XMLProperty.from_node(xml_prop, "interval", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_segment_of_video_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, _ = res_info
        res_type = "knora-api:VideoSegment"
        xml_prop = etree.fromstring("""
        <isSegmentOf >res_one</isSegmentOf>
        """)
        prop = XMLProperty.from_node(xml_prop, "resptr", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL

    def test_segment_of_audio_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, _ = res_info
        res_type = "knora-api:AudioSegment"
        xml_prop = etree.fromstring("""
        <isSegmentOf >res_one</isSegmentOf>
        """)
        prop = XMLProperty.from_node(xml_prop, "resptr", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 0
        assert prop_name == ONTO
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API
        value = next(result.objects(val_bn, KNORA_API))
        assert value == Literal("", datatype=XSD)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL
