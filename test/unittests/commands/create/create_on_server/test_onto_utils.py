# mypy: disable-error-code="no-untyped-def"

from unittest.mock import Mock
from unittest.mock import patch

import pytest
import rustworkx as rx
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.create.create_on_server.onto_utils import get_modification_date_onto_lookup
from dsp_tools.commands.create.create_on_server.onto_utils import get_project_iri_lookup
from dsp_tools.commands.create.create_on_server.onto_utils import sort_for_upload
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.error.exceptions import CircularOntologyDependency

PROJECT_IRI = "http://rdfh.ch/projects/1234"
API_URL = "http://0.0.0.0:3333"


class TestSortUploadOrder:
    def test_sorts_single_node_graph(self):
        graph = rx.PyDiGraph()
        node_idx = graph.add_node("nodeA")
        node_to_iri = {node_idx: "nodeA"}
        result = sort_for_upload(graph, node_to_iri)
        assert result == ["nodeA"]

    def test_circular_reference_raises(self):
        graph = rx.PyDiGraph()
        node_idxa = graph.add_node("nodeA")
        node_idxb = graph.add_node("nodeB")
        graph.add_edge(node_idxa, node_idxb, None)
        graph.add_edge(node_idxb, node_idxa, None)
        node_to_iri = {node_idxa: "nodeA", node_idxb: "nodeB"}
        with pytest.raises(CircularOntologyDependency):
            sort_for_upload(graph, node_to_iri)

    def test_sorts_diamond_pattern_correctly(self):
        # Diamond: A has edges to B and C, B and C have edges to D
        graph = rx.PyDiGraph()
        node_a = graph.add_node("nodeA")
        node_b = graph.add_node("nodeB")
        node_c = graph.add_node("nodeC")
        node_d = graph.add_node("nodeD")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_a, node_c, None)
        graph.add_edge(node_b, node_d, None)
        graph.add_edge(node_c, node_d, None)
        node_to_iri = {node_a: "nodeA", node_b: "nodeB", node_c: "nodeC", node_d: "nodeD"}
        result = sort_for_upload(graph, node_to_iri)
        assert result[0] == "nodeD"
        assert result[-1] == "nodeA"
        assert set(result[1:3]) == {"nodeC", "nodeB"}


def test_creates_lookup_with_two_ontologies():
    onto_iri_1 = "http://0.0.0.0:3333/ontology/1234/onto1/v2"
    onto_iri_2 = "http://0.0.0.0:3333/ontology/1234/onto2/v2"
    mod_date_1 = Literal("2024-01-15T10:30:00Z")
    mod_date_2 = Literal("2024-02-20T14:45:00Z")

    project_iri_lookup = ProjectIriLookup(project_iri=PROJECT_IRI)
    project_iri_lookup.add_onto("onto1", onto_iri_1)
    project_iri_lookup.add_onto("onto2", onto_iri_2)

    mock_client = Mock()
    mock_client.get_last_modification_date.side_effect = [mod_date_1, mod_date_2]

    result = get_modification_date_onto_lookup(project_iri_lookup, mock_client)

    assert result.project_iri == PROJECT_IRI
    assert len(result.onto_iris) == 2
    assert result.onto_iris["onto1"] == URIRef(onto_iri_1)
    assert result.onto_iris["onto2"] == URIRef(onto_iri_2)
    assert len(result.iri_to_last_modification_date) == 2
    assert result.get_last_mod_date(onto_iri_1) == mod_date_1
    assert result.get_last_mod_date(onto_iri_2) == mod_date_2
    assert mock_client.get_last_modification_date.call_count == 2


class TestOntoLookup:
    @patch("dsp_tools.commands.create.create_on_server.onto_utils.OntologyGetClientLive")
    def test_with_ontos(self, mock_client_class):
        onto_1_iri = "http://0.0.0.0:3333/ontology/1234/onto/v2"
        onto_2_iri = "http://0.0.0.0:3333/ontology/1234/second-onto/v2"
        prefixes = """
        PREFIX knora-api:   <http://api.knora.org/ontology/knora-api/v2#>
        PREFIX owl:         <http://www.w3.org/2002/07/owl#>
        PREFIX rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:        <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd:         <http://www.w3.org/2001/XMLSchema#>"""
        onto_1 = f"""
        <{onto_1_iri}>
            rdf:type                        owl:Ontology;
            rdfs:label                      "Ontology";
            knora-api:attachedToProject     <{PROJECT_IRI}>;
            knora-api:lastModificationDate  "2025-12-02T07:25:20.084934632Z"^^xsd:dateTimeStamp .
        """
        onto_2 = f"""
        <{onto_2_iri}>
            rdf:type                        owl:Ontology;
            rdfs:label                      "Second Ontology";
            knora-api:attachedToProject     <{PROJECT_IRI}>;
            knora-api:lastModificationDate  "2025-12-02T07:25:20.296635591Z"^^xsd:dateTimeStamp ."""
        ontologies = [f"{prefixes}{onto_1}", f"{prefixes}{onto_2}"]
        mock_client = Mock()
        mock_client.get_ontologies.return_value = (ontologies, [])
        mock_client_class.return_value = mock_client

        result = get_project_iri_lookup(API_URL, "1234", PROJECT_IRI)
        assert result.project_iri == PROJECT_IRI
        expected = {"Ontology": onto_1_iri, "Second Ontology": onto_2_iri}
        assert result.onto_iris == expected
