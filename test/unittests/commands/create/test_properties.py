# mypy: disable-error-code="no-untyped-def"
import rustworkx as rx

from dsp_tools.commands.create.create_on_server.properties import _get_property_create_order
from dsp_tools.commands.create.create_on_server.properties import _make_graph_to_sort
from dsp_tools.commands.create.create_on_server.properties import _sort_properties
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import KnoraObjectType
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty

KNORA_SUPER = "http://api.knora.org/ontology/knora-api/v2#hasValue"


def make_test_property(
    name: str,
    supers: list[str] | None = None,
    onto_name: str = "test_onto",
) -> ParsedProperty:
    supr = supers if supers else []
    supers.append(KNORA_SUPER)
    full_name = f"http://api.knora.org/ontology/0001/{onto_name}/v2#{name}"
    return ParsedProperty(
        name=full_name,
        labels={"en": f"Label for {name}"},
        comments=None,
        supers=supr,
        object=KnoraObjectType.TEXT,
        subject=None,
        gui_element=GuiElement.SIMPLETEXT,
        node_name=None,
        onto_name=onto_name,
    )


class TestMakeGraphToSort:
    def test_creates_graph_with_no_internal_dependencies(self):
        # Property has external super (knora-api:hasValue) but no internal dependencies
        prop = make_test_property("PropA")
        graph, node_to_iri = _make_graph_to_sort([prop])

        assert len(graph) == 1
        assert graph.num_edges() == 0  # External supers don't create edges
        assert prop.name in node_to_iri.values()

    def test_creates_graph_with_multiple_properties_no_internal_dependencies(self):
        # All properties have external supers but no dependencies on each other
        props = [
            make_test_property("PropA"),
            make_test_property("PropB"),
            make_test_property("PropC"),
        ]
        graph, node_to_iri = _make_graph_to_sort(props)

        assert len(graph) == 3
        assert graph.num_edges() == 0  # No internal dependencies
        assert all(p.name in node_to_iri.values() for p in props)

    def test_creates_graph_with_simple_linear_dependency(self):
        prop_b = make_test_property("PropB")
        prop_a = make_test_property("PropA", supers=[prop_b.name])

        graph, _node_to_iri = _make_graph_to_sort([prop_a, prop_b])

        assert len(graph) == 2
        assert graph.num_edges() == 1

    def test_creates_graph_with_multiple_linear_dependencies(self):
        prop_c = make_test_property("PropC")
        prop_b = make_test_property("PropB", supers=[prop_c.name])
        prop_a = make_test_property("PropA", supers=[prop_b.name])

        graph, _node_to_iri = _make_graph_to_sort([prop_a, prop_b, prop_c])

        assert len(graph) == 3
        assert graph.num_edges() == 2

    def test_creates_graph_with_multiple_supers(self):
        prop_b = make_test_property("PropB")
        prop_c = make_test_property("PropC")
        prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])

        graph, _node_to_iri = _make_graph_to_sort([prop_a, prop_b, prop_c])

        assert len(graph) == 3
        assert graph.num_edges() == 2

    def test_creates_graph_with_diamond_dependencies(self):
        # Diamond: D at top, B and C in middle (both depend on D), A at bottom (depends on B and C)
        prop_d = make_test_property("PropD")
        prop_b = make_test_property("PropB", supers=[prop_d.name])
        prop_c = make_test_property("PropC", supers=[prop_d.name])
        prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])

        graph, _node_to_iri = _make_graph_to_sort([prop_a, prop_b, prop_c, prop_d])

        assert len(graph) == 4
        assert graph.num_edges() == 4  # A->B, A->C, B->D, C->D

    def test_creates_graph_ignoring_external_supers(self):
        # Explicitly test that external knora-api supers don't create graph edges
        external_super = "http://api.knora.org/ontology/knora-api/v2#hasValue"
        prop_a = make_test_property("PropA", supers=[external_super])

        graph, _node_to_iri = _make_graph_to_sort([prop_a])

        assert len(graph) == 1
        assert graph.num_edges() == 0  # External super should not create an edge

    def test_creates_correct_node_to_iri_mapping(self):
        props = [
            make_test_property("PropA"),
            make_test_property("PropB"),
        ]
        _graph, node_to_iri = _make_graph_to_sort(props)

        assert len(node_to_iri) == 2
        iris_in_mapping = set(node_to_iri.values())
        expected_iris = {p.name for p in props}
        assert iris_in_mapping == expected_iris

    def test_empty_properties_list(self):
        graph, node_to_iri = _make_graph_to_sort([])

        assert len(graph) == 0
        assert len(node_to_iri) == 0
        assert graph.num_edges() == 0

    def test_graph_edge_count_matches_internal_dependencies(self):
        prop_c = make_test_property("PropC")
        prop_b = make_test_property("PropB", supers=[prop_c.name])
        prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])
        external_super = "http://api.knora.org/ontology/knora-api/v2#hasValue"
        prop_d = make_test_property("PropD", supers=[external_super])

        graph, _node_to_iri = _make_graph_to_sort([prop_a, prop_b, prop_c, prop_d])

        # A->B, A->C, B->C = 3 edges (D's external super creates no edge)
        assert graph.num_edges() == 3


class TestSortProperties:
    def test_sorts_single_node_graph(self):
        graph = rx.PyDiGraph()
        node_idx = graph.add_node("PropA")
        node_to_iri = {node_idx: "PropA"}

        result = _sort_properties(graph, node_to_iri)

        assert result == ["PropA"]

    def test_sorts_linear_dependency_graph(self):
        # Create graph: A -> B -> C (A depends on B, B depends on C)
        # Topological sort returns nodes where nodes with outgoing edges come first
        graph = rx.PyDiGraph()
        node_a = graph.add_node("PropA")
        node_b = graph.add_node("PropB")
        node_c = graph.add_node("PropC")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_b, node_c, None)
        node_to_iri = {node_a: "PropA", node_b: "PropB", node_c: "PropC"}

        result = _sort_properties(graph, node_to_iri)

        # A should come before B, B should come before C
        assert result.index("PropA") < result.index("PropB")
        assert result.index("PropB") < result.index("PropC")

    def test_sorts_complex_graph_with_multiple_branches(self):
        # Create graph with multiple branches
        graph = rx.PyDiGraph()
        node_a = graph.add_node("PropA")
        node_b = graph.add_node("PropB")
        node_c = graph.add_node("PropC")
        node_d = graph.add_node("PropD")
        # A -> B, C -> D
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_c, node_d, None)
        node_to_iri = {node_a: "PropA", node_b: "PropB", node_c: "PropC", node_d: "PropD"}

        result = _sort_properties(graph, node_to_iri)

        # A should come before B, C should come before D
        assert result.index("PropA") < result.index("PropB")
        assert result.index("PropC") < result.index("PropD")

    def test_sorts_diamond_pattern_correctly(self):
        # Diamond: A has edges to B and C, B and C have edges to D
        graph = rx.PyDiGraph()
        node_a = graph.add_node("PropA")
        node_b = graph.add_node("PropB")
        node_c = graph.add_node("PropC")
        node_d = graph.add_node("PropD")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_a, node_c, None)
        graph.add_edge(node_b, node_d, None)
        graph.add_edge(node_c, node_d, None)
        node_to_iri = {node_a: "PropA", node_b: "PropB", node_c: "PropC", node_d: "PropD"}

        result = _sort_properties(graph, node_to_iri)

        # A should come first (no incoming edges), D should come last (no outgoing edges)
        assert result.index("PropA") < result.index("PropB")
        assert result.index("PropA") < result.index("PropC")
        assert result.index("PropB") < result.index("PropD")
        assert result.index("PropC") < result.index("PropD")

    def test_sorted_order_respects_dependencies(self):
        # Create a more complex graph
        graph = rx.PyDiGraph()
        nodes = {name: graph.add_node(name) for name in ["A", "B", "C", "D", "E"]}
        # A -> B, A -> C, B -> D, C -> D, D -> E
        graph.add_edge(nodes["A"], nodes["B"], None)
        graph.add_edge(nodes["A"], nodes["C"], None)
        graph.add_edge(nodes["B"], nodes["D"], None)
        graph.add_edge(nodes["C"], nodes["D"], None)
        graph.add_edge(nodes["D"], nodes["E"], None)
        node_to_iri = {idx: name for name, idx in nodes.items()}

        result = _sort_properties(graph, node_to_iri)

        # Verify all dependencies are respected (source before target)
        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("C") < result.index("D")
        assert result.index("D") < result.index("E")


class TestGetPropertyCreateOrder:
    def test_returns_correct_order_for_simple_hierarchy(self):
        # PropB is the super, PropA inherits from PropB
        prop_b = make_test_property("PropB")
        prop_a = make_test_property("PropA", supers=[prop_b.name])

        result = _get_property_create_order([prop_a, prop_b])

        # Note: The current implementation creates edge A->B (child to parent)
        # So topological sort returns child before parent
        assert result.index(prop_a.name) < result.index(prop_b.name)

    def test_returns_correct_order_for_complex_hierarchy(self):
        # Hierarchy: PropD at top, PropB and PropC inherit from PropD, PropA inherits from PropB and PropC
        prop_d = make_test_property("PropD")
        prop_c = make_test_property("PropC", supers=[prop_d.name])
        prop_b = make_test_property("PropB", supers=[prop_d.name])
        prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])

        result = _get_property_create_order([prop_a, prop_b, prop_c, prop_d])

        # With edges pointing child->parent, children come before parents
        assert result.index(prop_a.name) < result.index(prop_b.name)
        assert result.index(prop_a.name) < result.index(prop_c.name)
        assert result.index(prop_b.name) < result.index(prop_d.name)
        assert result.index(prop_c.name) < result.index(prop_d.name)

    def test_properties_with_no_internal_dependencies_can_be_in_any_order(self):
        # All properties have external supers but no dependencies on each other
        props = [
            make_test_property("PropA"),
            make_test_property("PropB"),
            make_test_property("PropC"),
        ]

        result = _get_property_create_order(props)

        # All properties should be in the result (order doesn't matter without internal dependencies)
        assert len(result) == 3
        assert all(p.name in result for p in props)

    def test_child_always_comes_before_parent(self):
        # Create hierarchy: Grandparent <- Parent <- Child
        prop_grandparent = make_test_property("Grandparent")
        prop_parent = make_test_property("Parent", supers=[prop_grandparent.name])
        prop_child = make_test_property("Child", supers=[prop_parent.name])

        result = _get_property_create_order([prop_child, prop_parent, prop_grandparent])

        # Child comes before Parent, Parent comes before Grandparent
        assert result.index(prop_child.name) < result.index(prop_parent.name)
        assert result.index(prop_parent.name) < result.index(prop_grandparent.name)

    def test_multiple_inheritance_scenario(self):
        prop_b = make_test_property("PropB")
        prop_c = make_test_property("PropC")
        prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])

        result = _get_property_create_order([prop_a, prop_b, prop_c])

        # A has edges to both B and C, so A comes before both
        assert result.index(prop_a.name) < result.index(prop_b.name)
        assert result.index(prop_a.name) < result.index(prop_c.name)

    def test_external_supers_do_not_break_sorting(self):
        external_super = "http://api.knora.org/ontology/knora-api/v2#hasValue"
        prop_b = make_test_property("PropB", supers=[external_super])
        prop_a = make_test_property("PropA", supers=[prop_b.name, external_super])

        result = _get_property_create_order([prop_a, prop_b])

        # A has edge to B, so A comes before B
        assert result.index(prop_a.name) < result.index(prop_b.name)
        # External super should not be in the result
        assert external_super not in result

    def test_empty_list_returns_empty_list(self):
        result = _get_property_create_order([])

        assert result == []

    def test_input_order_does_not_affect_output_order(self):
        # Create hierarchy: PropA <- PropB <- PropC
        prop_a = make_test_property("PropA")
        prop_b = make_test_property("PropB", supers=[prop_a.name])
        prop_c = make_test_property("PropC", supers=[prop_b.name])

        # Pass them in reverse order
        result = _get_property_create_order([prop_c, prop_b, prop_a])

        # Should still get correct dependency order (children before parents)
        assert result.index(prop_c.name) < result.index(prop_b.name)
        assert result.index(prop_b.name) < result.index(prop_a.name)

    def test_mixed_dependencies_with_external_supers(self):
        external_super = "http://api.knora.org/ontology/knora-api/v2#hasValue"
        prop_d = make_test_property("PropD")
        prop_c = make_test_property("PropC", supers=[prop_d.name, external_super])
        prop_b = make_test_property("PropB", supers=[external_super])
        prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])

        result = _get_property_create_order([prop_a, prop_b, prop_c, prop_d])

        # Verify internal dependencies are respected (children before parents)
        assert result.index(prop_c.name) < result.index(prop_d.name)
        assert result.index(prop_a.name) < result.index(prop_b.name)
        assert result.index(prop_a.name) < result.index(prop_c.name)
        # Verify we have exactly 4 properties (no external ones)
        assert len(result) == 4
