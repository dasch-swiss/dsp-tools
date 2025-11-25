import pytest
import rustworkx as rx

from dsp_tools.commands.create.create_on_server.onto_utils import sort_for_upload
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
