from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import Literal

from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.serialisation.ontology import _make_one_cardinality_graph
from dsp_tools.commands.create.serialisation.ontology import _make_ontology_base_graph
from dsp_tools.commands.create.serialisation.ontology import serialise_cardinality_graph_for_request
from test.unittests.commands.create.constants import LAST_MODIFICATION_DATE
from test.unittests.commands.create.constants import ONTO
from test.unittests.commands.create.constants import ONTO_IRI

RESOURCE_IRI = ONTO.Resource
PROP_IRI = ONTO.hasText


def test_creates_graph_with_correct_structure() -> None:
    result = _make_ontology_base_graph(ONTO_IRI, LAST_MODIFICATION_DATE)
    assert len(result) == 2


class TestSerialiseCardinality:
    def test_creates_correct_graph_structure_with_cardinality_1(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)
        assert len(result_graph) == 5
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

    def test_serialise_card(self):
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        serialised = serialise_cardinality_graph_for_request(
            property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE
        )

        # Check ontology-level properties
        assert serialised["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2"
        assert serialised["@type"] == ["http://www.w3.org/2002/07/owl#Ontology"]
        assert serialised["http://api.knora.org/ontology/knora-api/v2#lastModificationDate"] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#dateTimeStamp", "@value": "2025-10-14T13:00:00.000000Z"}
        ]

        # Check graph contains exactly 2 nodes
        assert len(serialised["@graph"]) == 2

        # Find the resource and restriction nodes
        resource_node = next(
            n for n in serialised["@graph"] if n["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2#Resource"
        )
        restriction_nodes = [n for n in serialised["@graph"] if n["@id"].startswith("_:")]

        # Verify resource node structure
        assert resource_node["@type"] == ["http://www.w3.org/2002/07/owl#Class"]
        assert len(resource_node["http://www.w3.org/2000/01/rdf-schema#subClassOf"]) == 1
        blank_node_id = resource_node["http://www.w3.org/2000/01/rdf-schema#subClassOf"][0]["@id"]
        assert blank_node_id.startswith("_:")

        # Verify restriction node structure
        assert len(restriction_nodes) == 1
        restriction_node = restriction_nodes[0]
        assert restriction_node["@id"] == blank_node_id
        assert restriction_node["@type"] == ["http://www.w3.org/2002/07/owl#Restriction"]
        assert restriction_node["http://www.w3.org/2002/07/owl#cardinality"] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#integer", "@value": 1}
        ]
        assert restriction_node["http://www.w3.org/2002/07/owl#onProperty"] == [
            {"@id": "http://0.0.0.0:3333/ontology/9999/onto/v2#hasText"}
        ]

