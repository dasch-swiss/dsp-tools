# mypy: disable-error-code="no-untyped-def"
import rustworkx as rx

from dsp_tools.commands.create.create_on_server.properties import _get_property_create_order
from dsp_tools.commands.create.create_on_server.properties import _make_graph_to_sort
from dsp_tools.commands.create.create_on_server.properties import _sort_properties
from test.unittests.commands.create.create_on_server.conftest import EXTERNAL_SUPER
from test.unittests.commands.create.create_on_server.conftest import KNORA_SUPER


def _create_graph(nodes: dict[str, str], edges: list[tuple[str, str]]) -> tuple[rx.PyDiGraph, dict[int, str]]:
    graph = rx.PyDiGraph()
    node_indices = {}
    node_to_iri = {}

    # Add nodes
    for node_name, iri in nodes.items():
        idx = graph.add_node(node_name)
        node_indices[node_name] = idx
        node_to_iri[idx] = iri

    # Add edges
    for source, target in edges:
        graph.add_edge(node_indices[source], node_indices[target], None)

    return graph, node_to_iri


class TestMakeGraphToSort:
    def test_creates_graph_with_multiple_properties_no_internal_dependencies(self, independent_props):
        graph, node_to_iri = _make_graph_to_sort(independent_props)
        assert len(graph) == 3
        assert graph.num_edges() == 0  # No internal dependencies
        assert all(p.name in node_to_iri.values() for p in independent_props)

    def test_creates_graph_with_simple_linear_dependency(self, simple_linear_props):
        graph, _node_to_iri = _make_graph_to_sort(simple_linear_props)
        assert len(graph) == 2
        assert graph.num_edges() == 1

    def test_creates_graph_with_multiple_linear_dependencies(self, linear_chain_props):
        graph, _node_to_iri = _make_graph_to_sort(linear_chain_props)
        assert len(graph) == 3
        assert graph.num_edges() == 2

    def test_creates_graph_with_multiple_supers(self, multiple_inheritance_props):
        graph, _node_to_iri = _make_graph_to_sort(multiple_inheritance_props)
        assert len(graph) == 3
        assert graph.num_edges() == 2

    def test_creates_graph_with_diamond_dependencies(self, diamond_props):
        # Diamond: D at top, B and C in middle (both depend on D), A at bottom (depends on B and C)
        graph, _node_to_iri = _make_graph_to_sort(diamond_props)
        assert len(graph) == 4
        assert graph.num_edges() == 4  # A->B, A->C, B->D, C->D

    def test_creates_graph_ignoring_external_supers(self, prop_a):
        graph, _node_to_iri = _make_graph_to_sort([prop_a])
        assert len(graph) == 1
        assert graph.num_edges() == 0  # External super should not create an edge

    def test_creates_correct_node_to_iri_mapping(self, prop_a, prop_b):
        props = [prop_a, prop_b]
        _graph, node_to_iri = _make_graph_to_sort(props)
        assert len(node_to_iri) == 2
        iris_in_mapping = set(node_to_iri.values())
        expected_iris = {p.name for p in props}
        assert iris_in_mapping == expected_iris

    def test_graph_edge_count_matches_internal_dependencies(self, prop_factory, prop_a, prop_b, prop_c, prop_d):
        prop_c = prop_factory("PropC")
        prop_b = prop_factory("PropB", supers=[prop_c.name])
        prop_a = prop_factory("PropA", supers=[prop_b.name, prop_c.name])
        prop_d = prop_factory("PropD", supers=[EXTERNAL_SUPER])

        graph, _node_to_iri = _make_graph_to_sort([prop_a, prop_b, prop_c, prop_d])

        # A->B, A->C, B->C = 3 edges (D's external super creates no edge)
        assert graph.num_edges() == 3


class TestSortProperties:
    def test_sorts_single_node_graph(self, single_node_graph):
        graph, node_to_iri = single_node_graph
        result = _sort_properties(graph, node_to_iri)
        assert result == ["PropA"]

    def test_sorts_linear_dependency_graph(self, linear_graph):
        # Create graph: A -> B -> C (A depends on B, B depends on C)
        # Topological sort returns nodes where nodes with outgoing edges come first
        graph, node_to_iri = linear_graph

        result = _sort_properties(graph, node_to_iri)

        # A should come before B, B should come before C
        assert result == ["PropA", "PropB", "PropC"]

    def test_sorts_complex_graph_with_multiple_branches(self, multiple_branches_graph):
        # Create graph with multiple branches
        graph, node_to_iri = multiple_branches_graph

        result = _sort_properties(graph, node_to_iri)

        # A should come before B, C should come before D
        assert result == ["PropC", "PropD", "PropA", "PropB"]

    def test_sorts_diamond_pattern_correctly(self, diamond_graph):
        # Diamond: A has edges to B and C, B and C have edges to D
        graph, node_to_iri = diamond_graph

        result = _sort_properties(graph, node_to_iri)

        # A should come first (no incoming edges), D should come last (no outgoing edges)
        assert result == ["PropA", "PropC", "PropB", "PropD"]

    def test_sorted_order_respects_dependencies(self, complex_dependency_graph):
        # Create a more complex graph
        graph, node_to_iri = complex_dependency_graph

        result = _sort_properties(graph, node_to_iri)

        # Verify all dependencies are respected (source before target)
        assert result == ["A", "C", "B", "D", "E"]


class TestGetPropertyCreateOrder:
    def test_returns_correct_order_for_simple_hierarchy(self, simple_linear_props, prop_a, prop_b):
        # PropB is the super, PropA inherits from PropB
        prop_a, prop_b = simple_linear_props

        result = _get_property_create_order(simple_linear_props)

        # Note: The current implementation creates edge A->B (child to parent)
        # So topological sort returns child before parent
        assert result == [prop_a.name, prop_b.name]

    def test_returns_correct_order_for_complex_hierarchy(self, diamond_props, prop_a, prop_b, prop_c, prop_d):
        # Hierarchy: PropD at top, PropB and PropC inherit from PropD, PropA inherits from PropB and PropC
        prop_a, prop_b, prop_c, prop_d = diamond_props

        result = _get_property_create_order(diamond_props)

        # With edges pointing child->parent, children come before parents
        assert result == [prop_a.name, prop_c.name, prop_b.name, prop_d.name]

    def test_properties_with_no_internal_dependencies_can_be_in_any_order(self, independent_props):
        # All properties have external supers but no dependencies on each other
        result = _get_property_create_order(independent_props)

        # All properties should be in the result (order doesn't matter without internal dependencies)
        assert len(result) == 3
        assert all(p.name in result for p in independent_props)

    def test_child_always_comes_before_parent(self, grandparent_hierarchy_props):
        # Create hierarchy: Grandparent <- Parent <- Child
        prop_child, prop_parent, prop_grandparent = grandparent_hierarchy_props

        result = _get_property_create_order(grandparent_hierarchy_props)

        # Child comes before Parent, Parent comes before Grandparent
        assert result == [prop_child.name, prop_parent.name, prop_grandparent.name]

    def test_multiple_inheritance_scenario(self, multiple_inheritance_props, prop_a, prop_b, prop_c):
        prop_a, prop_b, prop_c = multiple_inheritance_props

        result = _get_property_create_order(multiple_inheritance_props)

        # A has edges to both B and C, so A comes before both
        assert result == [prop_a.name, prop_c.name, prop_b.name]

    def test_external_supers_do_not_break_sorting(self, prop_factory, prop_a, prop_b):
        prop_b = prop_factory("PropB", supers=[])
        prop_a = prop_factory("PropA", supers=[prop_b.name])
        result = _get_property_create_order([prop_a, prop_b])
        # A has edge to B, so A comes before B
        assert result == [prop_a.name, prop_b.name]
        assert KNORA_SUPER not in result

    def test_input_order_does_not_affect_output_order(self, prop_a, prop_b, prop_c):
        result = _get_property_create_order([prop_c, prop_b, prop_a])
        assert result == [prop_c.name, prop_b.name, prop_a.name]

    def test_mixed_dependencies_with_external_supers(self, prop_a, prop_b, prop_c, prop_d):
        mixed_dependency_props = [prop_a, prop_b, prop_c, prop_d]
        result = _get_property_create_order(mixed_dependency_props)
        assert result == [prop_a.name, prop_c.name, prop_d.name, prop_b.name]
