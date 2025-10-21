from unittest.mock import Mock

from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import Graph
from rdflib import Literal

from dsp_tools.clients.ontology_client import OntologyClient
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.serialisation.cardinalities import _add_one_cardinality
from dsp_tools.commands.create.serialisation.cardinalities import _make_cardinality_graph_for_request
from dsp_tools.commands.create.serialisation.cardinalities import _make_one_cardinality_graph
from dsp_tools.commands.create.serialisation.cardinalities import add_all_cardinalities
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.unittests.commands.create.serialisation.fixtures import LAST_MODIFICATION_DATE
from test.unittests.commands.create.serialisation.fixtures import ONTO
from test.unittests.commands.create.serialisation.fixtures import ONTO_IRI

RESOURCE_IRI = ONTO.Resource
PROP_IRI = ONTO.hasText


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

        # Check the blank node is a Restriction
        assert (bn, RDF.type, OWL.Restriction) in result_graph

        # Check the cardinality value
        assert (bn, OWL.cardinality, Literal(1)) in result_graph

        # Check the property restriction
        assert (bn, OWL.onProperty, PROP_IRI) in result_graph

    def test_creates_correct_graph_with_max_cardinality(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_0_1,
            gui_order=None,
        )

        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)

        # Find the blank node
        bn = next(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))

        # Check the maxCardinality value
        assert (bn, OWL.maxCardinality, Literal(1)) in result_graph

    def test_creates_correct_graph_with_min_cardinality(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_0_N,
            gui_order=None,
        )

        result_graph = _make_one_cardinality_graph(property_card, RESOURCE_IRI)

        # Find the blank node
        bn = next(result_graph.objects(RESOURCE_IRI, RDFS.subClassOf))

        # Check the minCardinality value
        assert (bn, OWL.minCardinality, Literal(0)) in result_graph


class TestMakeCardinalityGraphForRequest:
    def test_combines_base_graph_and_cardinality(self) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )

        result_graph = _make_cardinality_graph_for_request(
            property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE
        )

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
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        result_graph = _make_cardinality_graph_for_request(
            property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE
        )

        # Base graph: 2 triples (ontology type + lastModificationDate)
        # Cardinality graph: 4 triples (subClassOf + Restriction type + cardinality + onProperty)
        # Total: 6 triples
        assert len(result_graph) == 6


class TestAddOneCardinality:
    def test_calls_client_and_returns_modification_date(self) -> None:
        """Test that the function calls the client and returns the last modification date"""
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = LAST_MODIFICATION_DATE

        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )

        result_date, problems = _add_one_cardinality(
            property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client
        )

        assert result_date == LAST_MODIFICATION_DATE
        assert problems is None
        mock_client.post_resource_cardinalities.assert_called_once()

    def test_passes_correct_graph_to_client(self) -> None:
        """Test that the function passes a graph with correct structure to the client"""
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = LAST_MODIFICATION_DATE

        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )

        _add_one_cardinality(property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)

        # Verify that client was called with a Graph
        call_args = mock_client.post_resource_cardinalities.call_args
        passed_graph = call_args[0][0]

        assert isinstance(passed_graph, Graph)
        # Verify graph contains expected triples
        assert (ONTO_IRI, RDF.type, OWL.Ontology) in passed_graph
        assert (ONTO_IRI, KNORA_API.lastModificationDate, LAST_MODIFICATION_DATE) in passed_graph

    def test_returns_problem_when_client_returns_none(self) -> None:
        """Test that the function returns a problem when the client returns None (error case)"""
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = None

        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )

        result_date, problem = _add_one_cardinality(
            property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client
        )

        assert result_date == LAST_MODIFICATION_DATE
        assert problem is not None


class TestAddAllCardinalities:
    def test_adds_single_cardinality_successfully(self) -> None:
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = LAST_MODIFICATION_DATE

        cardinalities = [
            ParsedClassCardinalities(
                class_iri=str(RESOURCE_IRI),
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_1,
                        gui_order=None,
                    )
                ],
            )
        ]
        result = add_all_cardinalities(cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)
        assert result is None
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
            ParsedClassCardinalities(
                class_iri=str(ONTO.Resource1),
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri=str(ONTO.Resource2),
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_0_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri=str(ONTO.Resource3),
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_0_N,
                        gui_order=None,
                    )
                ],
            ),
        ]
        result = add_all_cardinalities(cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)
        assert result is None
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
            ParsedClassCardinalities(
                class_iri=str(ONTO.Resource1),
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri=str(ONTO.Resource2),
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_0_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri=str(ONTO.Resource3),
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_0_N,
                        gui_order=None,
                    )
                ],
            ),
        ]
        result = add_all_cardinalities(cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)
        assert result is not None
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
            ParsedClassCardinalities(
                class_iri="http://example.org/onto#Resource1",
                cards=[
                    ParsedPropertyCardinality(
                        propname="http://example.org/onto#hasText",
                        cardinality=Cardinality.C_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri="http://example.org/onto#Resource2",
                cards=[
                    ParsedPropertyCardinality(
                        propname="http://example.org/onto#hasValue",
                        cardinality=Cardinality.C_0_1,
                        gui_order=None,
                    )
                ],
            ),
        ]

        result = add_all_cardinalities(cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client)

        assert result is None
        assert len(passed_graphs) == 2

        # First graph should have initial modification date
        first_graph_dates = list(passed_graphs[0].objects(ONTO_IRI, KNORA_API.lastModificationDate))
        assert len(first_graph_dates) == 1
        assert str(first_graph_dates[0]) == "2025-10-14T13:00:00.000000Z"

        # Second graph should have updated modification date from first response
        second_graph_dates = list(passed_graphs[1].objects(ONTO_IRI, KNORA_API.lastModificationDate))
        assert len(second_graph_dates) == 1
        assert str(second_graph_dates[0]) == "2025-10-14T14:01:00.000000Z"
