# mypy: disable-error-code="no-untyped-def"

from unittest.mock import Mock

import pytest
import rustworkx as rx
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.create.create_on_server.onto_utils import get_onto_lookup
from dsp_tools.commands.create.create_on_server.onto_utils import sort_for_upload
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.error.exceptions import CircularOntologyDependency


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
        # A should come first (no incoming edges), D should come last (no outgoing edges)
        assert result[0] == "nodeA"
        assert result[-1] == "nodeD"
        assert set(result[1:3]) == {"nodeC", "nodeB"}


def test_creates_lookup_with_two_ontologies():
    project_iri = "http://rdfh.ch/projects/1234"
    onto_iri_1 = "http://0.0.0.0:3333/ontology/1234/onto1/v2"
    onto_iri_2 = "http://0.0.0.0:3333/ontology/1234/onto2/v2"
    mod_date_1 = Literal("2024-01-15T10:30:00Z")
    mod_date_2 = Literal("2024-02-20T14:45:00Z")

    project_iri_lookup = ProjectIriLookup(project_iri=project_iri)
    project_iri_lookup.add_onto("onto1", onto_iri_1)
    project_iri_lookup.add_onto("onto2", onto_iri_2)

    mock_client = Mock()
    mock_client.get_last_modification_date.side_effect = [mod_date_1, mod_date_2]

    result = get_onto_lookup(project_iri_lookup, mock_client)

    assert result.project_iri == project_iri
    assert len(result.onto_iris) == 2
    assert result.onto_iris["onto1"] == URIRef(onto_iri_1)
    assert result.onto_iris["onto2"] == URIRef(onto_iri_2)
    assert len(result.name_to_last_modification_date) == 2
    assert result.get_last_mod_date("onto1") == mod_date_1
    assert result.get_last_mod_date("onto2") == mod_date_2
    assert mock_client.get_last_modification_date.call_count == 2
