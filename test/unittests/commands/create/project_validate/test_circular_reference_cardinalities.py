# mypy: disable-error-code="no-untyped-def"

import rustworkx as rx

from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.project_validate import _extract_mandatory_link_props_per_class
from dsp_tools.commands.create.project_validate import _find_circles_with_mandatory_cardinalities
from dsp_tools.commands.create.project_validate import _make_cardinality_dependency_graph


class TestExtractMandatoryLinkPropsPerClass:
    def test_extract_correct_properties(self):
        cardinalities = [
            ParsedClassCardinalities(
                class_iri="ClassA",
                cards=[
                    ParsedPropertyCardinality("prop1", Cardinality.C_1, None),  # mandatory - should be included
                    ParsedPropertyCardinality("prop2", Cardinality.C_1_N, None),  # mandatory - should be included
                    ParsedPropertyCardinality("prop3", Cardinality.C_0_1, None),  # optional - should be excluded
                    ParsedPropertyCardinality("prop4", Cardinality.C_0_N, None),  # optional - should be excluded
                    ParsedPropertyCardinality("textProp", Cardinality.C_1, None),  # not a link - should be excluded
                ],
            )
        ]
        link_prop_iris = ["prop1", "prop2", "prop3", "prop4"]
        result = _extract_mandatory_link_props_per_class(cardinalities, link_prop_iris)
        assert set(result["ClassA"]) == {"prop1", "prop2"}


class TestMakeCardinalityDependencyGraphRustworkx:
    def test_create_simple_graph_with_two_nodes(self):
        """Graph should have correct nodes and edges for a simple A->B relationship."""
        mandatory_links = {"ClassA": ["linkToB"]}
        link_prop_to_object = {"linkToB": "ClassB"}
        graph = _make_cardinality_dependency_graph(mandatory_links, link_prop_to_object)
        assert graph.num_nodes() == 2
        assert graph.num_edges() == 1
        node_data = {graph[i] for i in range(graph.num_nodes())}
        assert node_data == {"ClassA", "ClassB"}

    def test_create_graph_with_circular_dependency(self):
        """Graph should correctly represent A->B->A circular dependency."""
        mandatory_links = {
            "ClassA": ["linkToB"],
            "ClassB": ["linkToA"],
        }
        link_prop_to_object = {
            "linkToB": "ClassB",
            "linkToA": "ClassA",
        }
        graph = _make_cardinality_dependency_graph(mandatory_links, link_prop_to_object)
        assert graph.num_nodes() == 2
        assert graph.num_edges() == 2

    def test_create_graph_with_multiple_properties_same_target(self):
        """Multiple properties from same class to same target should create multiple edges."""
        mandatory_links = {"ClassA": ["linkToB1", "linkToB2"]}
        link_prop_to_object = {
            "linkToB1": "ClassB",
            "linkToB2": "ClassB",
        }
        graph = _make_cardinality_dependency_graph(mandatory_links, link_prop_to_object)
        assert graph.num_nodes() == 2
        assert graph.num_edges() == 2


class TestFindCirclesWithMandatoryCardinalities:
    def test_find_simple_two_node_cycle(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node("ClassA")
        node_b = graph.add_node("ClassB")
        node_c = graph.add_node("ClassC")
        graph.add_edge(node_a, node_b, "linkToB-1")
        graph.add_edge(node_a, node_b, "linkToB-2")
        graph.add_edge(node_a, node_c, "linkToC")
        graph.add_edge(node_b, node_a, "linkToA")
        link_prop_to_object = {
            "linkToB-1": "ClassB",
            "linkToB-2": "ClassB",
            "linkToC": "ClassC",
            "linkToA": "ClassA",
        }
        errors = _find_circles_with_mandatory_cardinalities(graph, link_prop_to_object)
        expected = {
            "Cycle:\n"
            "    ClassA -- linkToB-1 --> ClassB\n"
            "    ClassA -- linkToB-2 --> ClassB\n"
            "    ClassB -- linkToA --> ClassA"
        }
        assert len(errors) == len(expected)
        error_objects = [e.problematic_object for e in errors]
        assert set(error_objects) == expected
        assert all(e.problem == InputProblemType.MIN_CARDINALITY_ONE_WITH_CIRCLE for e in errors)

    def test_find_no_cycles_in_linear_graph(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node("ClassA")
        node_b = graph.add_node("ClassB")
        node_c = graph.add_node("ClassC")
        graph.add_edge(node_a, node_b, "linkToB")
        graph.add_edge(node_b, node_c, "linkToC")
        errors = _find_circles_with_mandatory_cardinalities(graph, {})
        assert len(errors) == 0

    def test_self_link(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node("ClassA")
        node_b = graph.add_node("ClassB")
        node_c = graph.add_node("ClassC")
        graph.add_edge(node_a, node_a, "selfLink")
        graph.add_edge(node_b, node_c, "linkToC")
        graph.add_edge(node_c, node_b, "linkToB")
        link_prop_to_object = {"selfLink": "ClassA", "linkToC": "ClassC", "linkToB": "ClassB"}
        errors = _find_circles_with_mandatory_cardinalities(graph, link_prop_to_object)
        assert len(errors) == 2
        expected = {
            "Cycle:\n    ClassA -- selfLink --> ClassA",
            "Cycle:\n    ClassB -- linkToC --> ClassC\n    ClassC -- linkToB --> ClassB",
        }
        strings = {x.problematic_object for x in errors}
        assert strings == expected
