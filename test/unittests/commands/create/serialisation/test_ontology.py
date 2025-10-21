from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import Literal

from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.serialisation.ontology import _make_one_cardinality_graph
from dsp_tools.commands.create.serialisation.ontology import make_cardinality_graph_for_request
from dsp_tools.commands.create.serialisation.ontology import make_ontology_base_graph
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.unittests.commands.create.constants import LAST_MODIFICATION_DATE
from test.unittests.commands.create.constants import ONTO
from test.unittests.commands.create.constants import ONTO_IRI

RESOURCE_IRI = ONTO.Resource
PROP_IRI = ONTO.hasText


def test_creates_graph_with_correct_structure() -> None:
    result = make_ontology_base_graph(ONTO_IRI, LAST_MODIFICATION_DATE)
    assert len(result) == 2


class TestMakeOneCardinalityGraph:
    def test_creates_correct_graph_structure_with_cardinality_1(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)
        assert len(result_graph) == 4
        blank_nodes = list(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert len(blank_nodes) == 1
        bn = blank_nodes[0]
        assert (bn, RDF.type, OWL.Restriction) in result_graph
        assert (bn, OWL.cardinality, Literal(1)) in result_graph
        assert (bn, OWL.onProperty, PROP_IRI) in result_graph

    def test_creates_correct_graph_with_max_cardinality(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_0_1,
            gui_order=None,
        )
        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)
        bn = next(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert (bn, OWL.maxCardinality, Literal(1)) in result_graph

    def test_creates_correct_graph_with_min_cardinality(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_0_N,
            gui_order=None,
        )
        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)
        bn = next(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert (bn, OWL.minCardinality, Literal(0)) in result_graph


class TestMakeCardinalityGraphForRequest:
    def test_combines_base_graph_and_cardinality(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        result_graph = make_cardinality_graph_for_request(property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE)
        assert (ONTO_IRI, RDF.type, OWL.Ontology) in result_graph
        assert (ONTO_IRI, KNORA_API.lastModificationDate, LAST_MODIFICATION_DATE) in result_graph
        blank_nodes = list(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert len(blank_nodes) == 1
        bn = blank_nodes[0]
        assert (bn, RDF.type, OWL.Restriction) in result_graph
        assert (bn, OWL.cardinality, Literal(1)) in result_graph
        assert (bn, OWL.onProperty, PROP_IRI) in result_graph

    def test_graph_has_correct_total_triples(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        result_graph = make_cardinality_graph_for_request(property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE)
        ontology_graph_triples = 2
        cardinality_graph_triples = 4
        assert len(result_graph) == ontology_graph_triples + cardinality_graph_triples
