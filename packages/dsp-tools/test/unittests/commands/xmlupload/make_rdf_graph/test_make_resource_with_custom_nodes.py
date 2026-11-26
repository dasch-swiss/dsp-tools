from collections.abc import Callable
from itertools import count

import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.compare import isomorphic

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import make_values
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedBoolean
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedDate
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedList
from dsp_tools.utils.data_formats.date_util import Calendar
from dsp_tools.utils.data_formats.date_util import Date
from dsp_tools.utils.data_formats.date_util import Era
from dsp_tools.utils.data_formats.date_util import SingleDate
from dsp_tools.utils.rdf_constants import KNORA_API
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraFileValueType

ONTO_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
PROJECT_IRI = URIRef("http://rdfh.ch/9999/project")
RES_IRI = URIRef("http://rdfh.ch/9999/res/custom")
MIGRATION_IRI_STR = "http://rdfh.ch/9999/res/migration"
TYPE_IRI = URIRef(f"{ONTO_STR}TestResource")
LIST_NODE_IRI = URIRef("http://rdfh.ch/9999/lists/node")
NUM_VALUES = 3
NUM_NODES = NUM_VALUES + 2


@pytest.fixture
def lookups() -> IRILookups:
    return IRILookups(project_iri=PROJECT_IRI, id_to_iri=IriResolver({}))


@pytest.fixture
def resource() -> ProcessedResource:
    return ProcessedResource(
        res_id="res_id",
        type_iri=str(TYPE_IRI),
        label="Label",
        permissions=None,
        values=[
            ProcessedBoolean(True, f"{ONTO_STR}hasBool", None, None, 0),
            ProcessedList(str(LIST_NODE_IRI), f"{ONTO_STR}hasList", None, None, 1),
            ProcessedDate(
                Date(Calendar.GREGORIAN, SingleDate(Era.AD, 2000, None, None), None),
                f"{ONTO_STR}hasDate",
                None,
                None,
                2,
            ),
        ],
        file_value=ProcessedFileValue(
            value=ProcessedFileBitstream(value="original.jpg", res_id="res_id"),
            value_type=KnoraFileValueType.STILL_IMAGE_FILE,
            metadata=ProcessedFileMetadata(
                license_iri="http://rdfh.ch/licenses/cc-by-4.0", copyright_holder="holder", authorships=["author"]
            ),
        ),
    )


BITSTREAM = BitstreamInfo(internal_file_name="abcdef.jp2")


def _node_counter(received: list[BNode | URIRef] | None = None) -> Callable[[BNode | URIRef], URIRef]:
    counter = count(1)

    def make_node(res_node: BNode | URIRef) -> URIRef:
        if received is not None:
            received.append(res_node)
        return URIRef(f"http://rdfh.ch/9999/res/values/{next(counter)}")

    return make_node


def _value_node(n: int) -> URIRef:
    return URIRef(f"http://rdfh.ch/9999/res/values/{n}")


def _expected_graph(res_node: URIRef) -> Graph:
    g = Graph()
    g.add((res_node, RDF.type, TYPE_IRI))
    g.add((res_node, RDFS.label, Literal("Label", datatype=XSD.string)))
    g.add((res_node, KNORA_API.attachedToProject, PROJECT_IRI))

    bool_node, list_node, date_node, file_node = (_value_node(n) for n in (1, 2, 3, 4))
    g.add((res_node, URIRef(f"{ONTO_STR}hasBool"), bool_node))
    g.add((bool_node, RDF.type, KNORA_API.BooleanValue))
    g.add((bool_node, KNORA_API.booleanValueAsBoolean, Literal(True, datatype=XSD.boolean)))
    g.add((bool_node, KNORA_API.valueHasOrder, Literal(0, datatype=XSD.integer)))

    g.add((res_node, URIRef(f"{ONTO_STR}hasList"), list_node))
    g.add((list_node, RDF.type, KNORA_API.ListValue))
    g.add((list_node, KNORA_API.listValueAsListNode, LIST_NODE_IRI))
    g.add((list_node, KNORA_API.valueHasOrder, Literal(1, datatype=XSD.integer)))

    g.add((res_node, URIRef(f"{ONTO_STR}hasDate"), date_node))
    g.add((date_node, RDF.type, KNORA_API.DateValue))
    g.add((date_node, KNORA_API.valueHasOrder, Literal(2, datatype=XSD.integer)))
    g.add((date_node, KNORA_API.dateValueHasCalendar, Literal("GREGORIAN", datatype=XSD.string)))
    g.add((date_node, KNORA_API.dateValueHasStartYear, Literal(2000, datatype=XSD.integer)))
    g.add((date_node, KNORA_API.dateValueHasStartEra, Literal("AD", datatype=XSD.string)))

    g.add((res_node, KNORA_API.hasStillImageFileValue, file_node))
    g.add((file_node, RDF.type, KNORA_API.StillImageFileValue))
    g.add((file_node, KNORA_API.fileValueHasFilename, Literal("abcdef.jp2", datatype=XSD.string)))
    g.add((file_node, KNORA_API.hasLicense, URIRef("http://rdfh.ch/licenses/cc-by-4.0")))
    g.add((file_node, KNORA_API.hasCopyrightHolder, Literal("holder", datatype=XSD.string)))
    g.add((file_node, KNORA_API.hasAuthorship, Literal("author", datatype=XSD.string)))
    return g


def _subjects(g: Graph) -> set[BNode | URIRef]:
    return {s for s in g.subjects() if isinstance(s, (BNode, URIRef))}


def test_defaults_create_blank_nodes(resource: ProcessedResource, lookups: IRILookups) -> None:
    g = create_resource_with_values(resource, BITSTREAM, lookups)
    subjects = _subjects(g)
    assert len(subjects) == NUM_NODES
    assert all(isinstance(s, BNode) for s in subjects)


def test_migration_iri_is_used_without_passed_res_node(resource: ProcessedResource, lookups: IRILookups) -> None:
    resource.migration_metadata = MigrationMetadata(MIGRATION_IRI_STR, None)
    g = create_resource_with_values(resource, BITSTREAM, lookups)
    assert URIRef(MIGRATION_IRI_STR) in _subjects(g)


def test_passed_res_node_is_used(resource: ProcessedResource, lookups: IRILookups) -> None:
    g = create_resource_with_values(resource, BITSTREAM, lookups, res_node=RES_IRI)
    assert (RES_IRI, RDF.type, TYPE_IRI) in g
    assert RES_IRI in _subjects(g)


def test_passed_res_node_wins_over_migration_iri(resource: ProcessedResource, lookups: IRILookups) -> None:
    resource.migration_metadata = MigrationMetadata(MIGRATION_IRI_STR, None)
    g = create_resource_with_values(resource, BITSTREAM, lookups, res_node=RES_IRI)
    assert RES_IRI in _subjects(g)
    assert URIRef(MIGRATION_IRI_STR) not in _subjects(g)


def test_passed_value_node_factory_is_used_for_values_and_file_value(
    resource: ProcessedResource, lookups: IRILookups
) -> None:
    g = create_resource_with_values(resource, BITSTREAM, lookups, res_node=RES_IRI, make_value_node=_node_counter())
    assert isomorphic(g, _expected_graph(RES_IRI))


def test_value_node_factory_receives_the_resource_node(resource: ProcessedResource, lookups: IRILookups) -> None:
    received: list[BNode | URIRef] = []
    create_resource_with_values(resource, BITSTREAM, lookups, res_node=RES_IRI, make_value_node=_node_counter(received))
    assert received == [RES_IRI] * (NUM_VALUES + 1)


def test_make_values_uses_factory_per_value(resource: ProcessedResource, lookups: IRILookups) -> None:
    g = make_values(resource.values, RES_IRI, lookups, _node_counter())
    value_nodes = set(g.objects(RES_IRI))
    assert value_nodes == {_value_node(1), _value_node(2), _value_node(3)}


def test_make_values_default_creates_distinct_blank_nodes(resource: ProcessedResource, lookups: IRILookups) -> None:
    g = make_values(resource.values, RES_IRI, lookups)
    value_nodes = set(g.objects(RES_IRI))
    assert len(value_nodes) == NUM_VALUES
    assert all(isinstance(n, BNode) for n in value_nodes)
