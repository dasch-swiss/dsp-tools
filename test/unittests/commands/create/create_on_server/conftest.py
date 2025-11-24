# mypy: disable-error-code="no-untyped-def"
import pytest
import rustworkx as rx

from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import KnoraObjectType
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty

# Constants used across tests
KNORA_SUPER = "http://api.knora.org/ontology/knora-api/v2#hasValue"
EXTERNAL_SUPER = "http://xmlns.com/foaf/0.1/name"


def make_test_property(
    name: str,
    supers: list[str] | None = None,
    onto_name: str = "test_onto",
) -> ParsedProperty:
    """Helper function to create a test property with standard defaults."""
    supr = supers if supers else []
    supr.append(KNORA_SUPER)
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


# Factory fixtures
@pytest.fixture
def prop_factory():
    """Factory fixture to create test properties with custom parameters."""
    return make_test_property


# Individual property fixtures
@pytest.fixture
def prop_a():
    """Independent property A with no internal dependencies."""
    return make_test_property("PropA")


@pytest.fixture
def prop_b():
    """Independent property B with no internal dependencies."""
    return make_test_property("PropB")


@pytest.fixture
def prop_c():
    """Independent property C with no internal dependencies."""
    return make_test_property("PropC")


@pytest.fixture
def prop_d():
    """Independent property D with no internal dependencies."""
    return make_test_property("PropD")


# Property collection fixtures - Hierarchies
@pytest.fixture
def independent_props():
    """Three independent properties with no internal dependencies."""
    return [
        make_test_property("PropA"),
        make_test_property("PropB"),
        make_test_property("PropC"),
    ]


@pytest.fixture
def linear_chain_props():
    """Linear dependency chain: PropC -> PropB -> PropA (A depends on B, B depends on C)."""
    prop_c = make_test_property("PropC")
    prop_b = make_test_property("PropB", supers=[prop_c.name])
    prop_a = make_test_property("PropA", supers=[prop_b.name])
    return [prop_a, prop_b, prop_c]


@pytest.fixture
def simple_linear_props():
    """Simple two-property linear dependency: PropB -> PropA (A depends on B)."""
    prop_b = make_test_property("PropB")
    prop_a = make_test_property("PropA", supers=[prop_b.name])
    return [prop_a, prop_b]


@pytest.fixture
def diamond_props():
    """
    Diamond dependency pattern:
    - PropD at top
    - PropB and PropC in middle (both depend on PropD)
    - PropA at bottom (depends on both PropB and PropC)
    """
    prop_d = make_test_property("PropD")
    prop_b = make_test_property("PropB", supers=[prop_d.name])
    prop_c = make_test_property("PropC", supers=[prop_d.name])
    prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])
    return [prop_a, prop_b, prop_c, prop_d]


@pytest.fixture
def multiple_inheritance_props():
    """PropA inherits from both PropB and PropC (both independent)."""
    prop_b = make_test_property("PropB")
    prop_c = make_test_property("PropC")
    prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])
    return [prop_a, prop_b, prop_c]


@pytest.fixture
def grandparent_hierarchy_props():
    """Three-level hierarchy: Grandparent <- Parent <- Child."""
    prop_grandparent = make_test_property("Grandparent")
    prop_parent = make_test_property("Parent", supers=[prop_grandparent.name])
    prop_child = make_test_property("Child", supers=[prop_parent.name])
    return [prop_child, prop_parent, prop_grandparent]


@pytest.fixture
def mixed_dependency_props():
    """Properties with mixed internal and external dependencies."""
    prop_d = make_test_property("PropD")
    prop_c = make_test_property("PropC", supers=[prop_d.name, EXTERNAL_SUPER])
    prop_b = make_test_property("PropB", supers=[EXTERNAL_SUPER])
    prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])
    return [prop_a, prop_b, prop_c, prop_d]


@pytest.fixture
def graph_factory():
    """
    Factory to create a graph with custom nodes and edges.
    Returns a function that takes nodes dict and edges list.
    """


@pytest.fixture
def single_node_graph():
    """Graph with a single node (PropA)."""
    graph = rx.PyDiGraph()
    node_idx = graph.add_node("PropA")
    node_to_iri = {node_idx: "PropA"}
    return graph, node_to_iri


@pytest.fixture
def linear_graph():
    """Linear dependency graph: A -> B -> C."""
    graph = rx.PyDiGraph()
    node_a = graph.add_node("PropA")
    node_b = graph.add_node("PropB")
    node_c = graph.add_node("PropC")
    graph.add_edge(node_a, node_b, None)
    graph.add_edge(node_b, node_c, None)
    node_to_iri = {node_a: "PropA", node_b: "PropB", node_c: "PropC"}
    return graph, node_to_iri


@pytest.fixture
def multiple_branches_graph():
    """Graph with multiple independent branches: A -> B, C -> D."""
    graph = rx.PyDiGraph()
    node_a = graph.add_node("PropA")
    node_b = graph.add_node("PropB")
    node_c = graph.add_node("PropC")
    node_d = graph.add_node("PropD")
    graph.add_edge(node_a, node_b, None)
    graph.add_edge(node_c, node_d, None)
    node_to_iri = {node_a: "PropA", node_b: "PropB", node_c: "PropC", node_d: "PropD"}
    return graph, node_to_iri


@pytest.fixture
def diamond_graph():
    """
    Diamond pattern graph:
    - A has edges to B and C
    - B and C have edges to D
    """
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
    return graph, node_to_iri


@pytest.fixture
def complex_dependency_graph():
    """
    Complex graph with multiple levels:
    A -> B, A -> C, B -> D, C -> D, D -> E
    """
    graph = rx.PyDiGraph()
    nodes = {name: graph.add_node(name) for name in ["A", "B", "C", "D", "E"]}
    graph.add_edge(nodes["A"], nodes["B"], None)
    graph.add_edge(nodes["A"], nodes["C"], None)
    graph.add_edge(nodes["B"], nodes["D"], None)
    graph.add_edge(nodes["C"], nodes["D"], None)
    graph.add_edge(nodes["D"], nodes["E"], None)
    node_to_iri = {idx: name for name, idx in nodes.items()}
    return graph, node_to_iri
