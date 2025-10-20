from unittest.mock import Mock

from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.clients.ontology_client import OntologyClient
from dsp_tools.commands.create.models.rdf_ontology import RdfCardinalityRestriction
from dsp_tools.commands.create.models.rdf_ontology import RdfResourceCardinality
from dsp_tools.commands.create.serialisation.cardinalities import _add_cardinalities_for_one_class
from dsp_tools.commands.create.serialisation.cardinalities import _make_cardinality_graph_for_request
from dsp_tools.commands.create.serialisation.cardinalities import _make_one_cardinality_graph
from dsp_tools.commands.create.serialisation.cardinalities import add_all_cardinalities
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.unittests.commands.create.serialisation.fixtures import ONTO
from test.unittests.commands.create.serialisation.fixtures import ONTO_IRI

RESOURCE_IRI = ONTO.Resource
PROP_IRI = ONTO.hasText
LAST_MODIFICATION_DATE = Literal("2025-10-14T13:00:00.000000Z", XSD.dateTimeStamp)


class TestMakeOneCardinalityGraph:
    """Tests for _make_one_cardinality_graph function"""

    def test_creates_correct_graph_structure_with_cardinality_1(self) -> None:
        cardinality = RdfCardinalityRestriction(OWL.cardinality, Literal(1))

        resource_card = RdfResourceCardinality(
            resource_iri=RESOURCE_IRI,
            on_property=PROP_IRI,
            cardinality=cardinality,
        )

        result_graph = _make_one_cardinality_graph(resource_card)

        # Verify the graph contains expected triples
        assert len(result_graph) == 4

        # Find the blank node
        blank_nodes = list(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert len(blank_nodes) == 1
        bn = blank_nodes[0]
        assert isinstance(bn, BNode)

        # Check the blank node is a Restriction
        assert (bn, RDF.type, OWL.Restriction) in result_graph

        # Check the cardinality value
        assert (bn, OWL.cardinality, Literal(1)) in result_graph

        # Check the property restriction
        assert (bn, OWL.onProperty, PROP_IRI) in result_graph

    def test_creates_correct_graph_with_max_cardinality(self) -> None:
        cardinality = RdfCardinalityRestriction(OWL.maxCardinality, Literal(1))

        resource_card = RdfResourceCardinality(
            resource_iri=RESOURCE_IRI,
            on_property=PROP_IRI,
            cardinality=cardinality,
        )

        result_graph = _make_one_cardinality_graph(resource_card)

        # Find the blank node
        bn = next(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))

        # Check the maxCardinality value
        assert (bn, OWL.maxCardinality, Literal(1)) in result_graph

    def test_creates_correct_graph_with_min_cardinality(self) -> None:
        cardinality = RdfCardinalityRestriction(OWL.minCardinality, Literal(0))

        resource_card = RdfResourceCardinality(
            resource_iri=RESOURCE_IRI,
            on_property=PROP_IRI,
            cardinality=cardinality,
        )

        result_graph = _make_one_cardinality_graph(resource_card)

        # Find the blank node
        bn = next(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))

        # Check the minCardinality value
        assert (bn, OWL.minCardinality, Literal(0)) in result_graph


class TestMakeCardinalityGraphForRequest:
    def test_combines_base_graph_and_cardinality(self) -> None:
        cardinality = RdfCardinalityRestriction(OWL.cardinality, Literal(1))

        resource_card = RdfResourceCardinality(
            resource_iri=RESOURCE_IRI,
            on_property=PROP_IRI,
            cardinality=cardinality,
        )

        result_graph = _make_cardinality_graph_for_request(resource_card, ONTO_IRI, LAST_MODIFICATION_DATE)

        # Check base ontology triples are present
        assert (ONTO_IRI, RDF.type, OWL.Ontology) in result_graph
        assert (ONTO_IRI, KNORA_API.lastModificationDate, LAST_MODIFICATION_DATE) in result_graph

        # Check cardinality triples are present
        blank_nodes = list(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))
        assert len(blank_nodes) == 1
        bn = blank_nodes[0]

        assert (bn, RDF.type, OWL.Restriction) in result_graph
        assert (bn, OWL.cardinality, Literal(1)) in result_graph
        assert (bn, OWL.onProperty, PROP_IRI) in result_graph

    def test_graph_has_correct_total_triples(self) -> None:
        cardinality = RdfCardinalityRestriction(OWL.cardinality, Literal(1))
        resource_card = RdfResourceCardinality(
            resource_iri=RESOURCE_IRI,
            on_property=PROP_IRI,
            cardinality=cardinality,
        )
        result_graph = _make_cardinality_graph_for_request(resource_card, ONTO_IRI, LAST_MODIFICATION_DATE)

        # Base graph: 2 triples (ontology type + lastModificationDate)
        # Cardinality graph: 4 triples (subClassOf + Restriction type + cardinality + onProperty)
        # Total: 6 triples
        assert len(result_graph) == 6


class TestAddOneCardinality:
    def test_calls_client_and_returns_modification_date(self) -> None:
        """Test that the function calls the client and returns the last modification date"""
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = LAST_MODIFICATION_DATE
        cardinality = RdfCardinalityRestriction(OWL.cardinality, Literal(1))

        resource_card = RdfResourceCardinality(
            resource_iri=RESOURCE_IRI,
            on_property=PROP_IRI,
            cardinality=cardinality,
        )

        result = _add_cardinalities_for_one_class(resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)

        assert result == LAST_MODIFICATION_DATE
        mock_client.post_resource_cardinalities.assert_called_once()

    def test_passes_correct_graph_to_client(self) -> None:
        """Test that the function passes a graph with correct structure to the client"""
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = LAST_MODIFICATION_DATE
        cardinality = RdfCardinalityRestriction(OWL.cardinality, Literal(1))

        resource_card = RdfResourceCardinality(
            resource_iri=RESOURCE_IRI,
            on_property=PROP_IRI,
            cardinality=cardinality,
        )

        _add_cardinalities_for_one_class(resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)

        # Verify that client was called with a Graph
        call_args = mock_client.post_resource_cardinalities.call_args
        passed_graph = call_args[0][0]

        assert isinstance(passed_graph, Graph)
        # Verify graph contains expected triples
        assert (ONTO_IRI, RDF.type, OWL.Ontology) in passed_graph
        assert (ONTO_IRI, KNORA_API.lastModificationDate, LAST_MODIFICATION_DATE) in passed_graph

    def test_returns_none_when_client_returns_none(self) -> None:
        """Test that the function returns None when the client returns None (error case)"""
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = None
        cardinality = RdfCardinalityRestriction(OWL.cardinality, Literal(1))
        resource_card = RdfResourceCardinality(
            resource_iri=RESOURCE_IRI,
            on_property=PROP_IRI,
            cardinality=cardinality,
        )
        result = _add_cardinalities_for_one_class(resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)
        assert result is None


class TestAddAllCardinalities:
    def test_adds_single_cardinality_successfully(self) -> None:
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = LAST_MODIFICATION_DATE

        cardinalities = [
            RdfResourceCardinality(
                resource_iri=RESOURCE_IRI,
                on_property=PROP_IRI,
                cardinality=RdfCardinalityRestriction(OWL.cardinality, Literal(1)),
            )
        ]
        result = add_all_cardinalities(cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)
        assert result is True
        assert mock_client.post_resource_cardinalities.call_count == 1

    def test_adds_multiple_cardinalities_successfully(self) -> None:
        mock_client = Mock(spec=OntologyClient)
        # Return different modification dates for each call
        mock_client.post_resource_cardinalities.side_effect = [
            Literal("2025-10-14T14:00:00.000000Z"),
            Literal("2025-10-14T14:01:00.000000Z"),
            Literal("2025-10-14T14:02:00.000000Z"),
        ]
        cardinalities = [
            RdfResourceCardinality(
                resource_iri=ONTO.Resource1,
                on_property=PROP_IRI,
                cardinality=RdfCardinalityRestriction(OWL.cardinality, Literal(1)),
            ),
            RdfResourceCardinality(
                resource_iri=ONTO.Resource2,
                on_property=PROP_IRI,
                cardinality=RdfCardinalityRestriction(OWL.maxCardinality, Literal(1)),
            ),
            RdfResourceCardinality(
                resource_iri=ONTO.Resource3,
                on_property=PROP_IRI,
                cardinality=RdfCardinalityRestriction(OWL.minCardinality, Literal(0)),
            ),
        ]
        result = add_all_cardinalities(cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)
        assert result is True
        assert mock_client.post_resource_cardinalities.call_count == 3

    def test_handles_partial_failure(self) -> None:
        mock_client = Mock(spec=OntologyClient)
        # Second call returns None (failure)
        mock_client.post_resource_cardinalities.side_effect = [
            Literal("2025-10-14T14:00:00.000000Z"),
            None,  # Failure
            Literal("2025-10-14T14:02:00.000000Z"),
        ]
        cardinalities = [
            RdfResourceCardinality(
                resource_iri=ONTO.Resource1,
                on_property=PROP_IRI,
                cardinality=RdfCardinalityRestriction(OWL.cardinality, Literal(1)),
            ),
            RdfResourceCardinality(
                resource_iri=ONTO.Resource2,
                on_property=PROP_IRI,
                cardinality=RdfCardinalityRestriction(OWL.maxCardinality, Literal(1)),
            ),
            RdfResourceCardinality(
                resource_iri=ONTO.Resource3,
                on_property=PROP_IRI,
                cardinality=RdfCardinalityRestriction(OWL.minCardinality, Literal(0)),
            ),
        ]
        result = add_all_cardinalities(cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)
        assert result is False
        assert mock_client.post_resource_cardinalities.call_count == 3

    def test_updates_modification_date_between_calls(self) -> None:
        mock_client = Mock(spec=OntologyClient)

        # Track the graphs passed to the client
        passed_graphs = []

        def capture_graph(graph: Graph) -> Literal:
            passed_graphs.append(graph)
            # Return a new modification date
            return Literal(f"2025-10-14T14:0{len(passed_graphs)}:00.000000Z")

        mock_client.post_resource_cardinalities.side_effect = capture_graph

        cardinalities = [
            RdfResourceCardinality(
                resource_iri=URIRef("http://example.org/onto#Resource1"),
                on_property=URIRef("http://example.org/onto#hasText"),
                cardinality=RdfCardinalityRestriction(OWL.cardinality, Literal(1)),
            ),
            RdfResourceCardinality(
                resource_iri=URIRef("http://example.org/onto#Resource2"),
                on_property=URIRef("http://example.org/onto#hasValue"),
                cardinality=RdfCardinalityRestriction(OWL.maxCardinality, Literal(1)),
            ),
        ]

        result = add_all_cardinalities(cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)

        assert result is True
        assert len(passed_graphs) == 2

        # First graph should have initial modification date
        first_graph_dates = list(passed_graphs[0].objects(ONTO_IRI, KNORA_API.lastModificationDate))
        assert len(first_graph_dates) == 1
        assert str(first_graph_dates[0]) == "2025-10-14T13:00:00.000000Z"

        # Second graph should have updated modification date from first response
        second_graph_dates = list(passed_graphs[1].objects(ONTO_IRI, KNORA_API.lastModificationDate))
        assert len(second_graph_dates) == 1
        assert str(second_graph_dates[0]) == "2025-10-14T14:01:00.000000Z"
