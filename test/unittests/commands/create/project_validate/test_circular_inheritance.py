# mypy: disable-error-code="no-untyped-def"

import rustworkx as rx

from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.project_validate import _check_circular_inheritance_in_classes
from dsp_tools.commands.create.project_validate import _check_circular_inheritance_in_properties
from dsp_tools.commands.create.project_validate import _find_and_format_inheritance_cycles
from dsp_tools.commands.create.project_validate import _make_inheritance_graph_for_classes
from dsp_tools.commands.create.project_validate import _make_inheritance_graph_for_properties
from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX
from test.unittests.commands.create.constants import ONTO_NAMESPACE_STR


class TestMakeInheritanceGraphForClasses:
    def test_create_simple_linear_graph(self):
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassA",
                labels={"en": "A"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}ClassB"],
                onto_iri="onto",
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassB", labels={"en": "B"}, comments=None, supers=[], onto_iri="onto"
            ),
        ]
        graph = _make_inheritance_graph_for_classes(classes)
        assert graph.num_nodes() == 2
        assert graph.num_edges() == 1

    def test_create_graph_with_circular_dependency(self):
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassA",
                labels={"en": "A"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}ClassB"],
                onto_iri="onto",
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassB",
                labels={"en": "B"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}ClassA"],
                onto_iri="onto",
            ),
        ]
        graph = _make_inheritance_graph_for_classes(classes)
        assert graph.num_nodes() == 2
        assert graph.num_edges() == 2

    def test_ignores_knora_base_classes(self):
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassA",
                labels={"en": "A"},
                comments=None,
                supers=[f"{KNORA_API_PREFIX}Resource"],
                onto_iri="onto",
            ),
        ]
        graph = _make_inheritance_graph_for_classes(classes)
        assert graph.num_nodes() == 1
        assert graph.num_edges() == 0


class TestMakeInheritanceGraphForProperties:
    def test_create_simple_linear_graph(self):
        properties = [
            ParsedProperty(
                name=f"{ONTO_NAMESPACE_STR}PropA",
                labels={"en": "A"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}PropB"],
                object="text",
                subject=None,
                gui_element=GuiElement.SIMPLETEXT,
                node_name=None,
                onto_iri="onto",
            ),
            ParsedProperty(
                name=f"{ONTO_NAMESPACE_STR}PropB",
                labels={"en": "B"},
                comments=None,
                supers=[],
                object="text",
                subject=None,
                gui_element=GuiElement.SIMPLETEXT,
                node_name=None,
                onto_iri="onto",
            ),
        ]
        graph = _make_inheritance_graph_for_properties(properties)
        assert graph.num_nodes() == 2
        assert graph.num_edges() == 1


class TestFindAndFormatInheritanceCycles:
    def test_find_simple_two_node_cycle(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassA")
        node_b = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassB")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_b, node_a, None)

        errors = _find_and_format_inheritance_cycles(graph, InputProblemType.CIRCULAR_CLASS_INHERITANCE)

        assert len(errors) == 1
        assert errors[0].problematic_object == "asdf"
        assert errors[0].problem == InputProblemType.CIRCULAR_CLASS_INHERITANCE

    def test_find_three_node_cycle(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassA")
        node_b = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassB")
        node_c = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassC")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_b, node_c, None)
        graph.add_edge(node_c, node_a, None)

        errors = _find_and_format_inheritance_cycles(graph, InputProblemType.CIRCULAR_CLASS_INHERITANCE)

        assert len(errors) == 1
        assert errors[0].problematic_object == "asdf"

    def test_find_no_cycles_in_linear_graph(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassA")
        node_b = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassB")
        node_c = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassC")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_b, node_c, None)

        errors = _find_and_format_inheritance_cycles(graph, InputProblemType.CIRCULAR_CLASS_INHERITANCE)

        assert len(errors) == 0

    def test_self_reference_cycle(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node(f"{ONTO_NAMESPACE_STR}ClassA")
        graph.add_edge(node_a, node_a, None)

        errors = _find_and_format_inheritance_cycles(graph, InputProblemType.CIRCULAR_CLASS_INHERITANCE)

        assert len(errors) == 1
        assert errors[0].problematic_object == "ClassA"


class TestCheckCircularInheritanceInClasses:
    def test_no_classes_returns_none(self):
        result = _check_circular_inheritance_in_classes([])
        assert result is None

    def test_linear_inheritance_returns_none(self):
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassA",
                labels={"en": "A"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}ClassB"],
                onto_iri="onto",
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassB", labels={"en": "B"}, comments=None, supers=[], onto_iri="onto"
            ),
        ]
        result = _check_circular_inheritance_in_classes(classes)
        assert result is None

    def test_circular_inheritance_returns_problems(self):
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassA",
                labels={"en": "A"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}ClassB"],
                onto_iri="onto",
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ClassB",
                labels={"en": "B"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}ClassA"],
                onto_iri="onto",
            ),
        ]
        result = _check_circular_inheritance_in_classes(classes)
        assert result is not None
        assert len(result.problems) == 1
        assert "Cycle" in result.problems[0].problematic_object


class TestCheckCircularInheritanceInProperties:
    def test_no_properties_returns_none(self):
        result = _check_circular_inheritance_in_properties([])
        assert result is None

    def test_circular_inheritance_returns_problems(self):
        properties = [
            ParsedProperty(
                name=f"{ONTO_NAMESPACE_STR}PropA",
                labels={"en": "A"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}PropB"],
                object="text",
                subject=None,
                gui_element=GuiElement.SIMPLETEXT,
                node_name=None,
                onto_iri="onto",
            ),
            ParsedProperty(
                name=f"{ONTO_NAMESPACE_STR}PropB",
                labels={"en": "B"},
                comments=None,
                supers=[f"{ONTO_NAMESPACE_STR}PropA"],
                object="text",
                subject=None,
                gui_element=GuiElement.SIMPLETEXT,
                node_name=None,
                onto_iri="onto",
            ),
        ]
        result = _check_circular_inheritance_in_properties(properties)
        assert result is not None
        assert len(result.problems) == 1
        assert "Cycle" in result.problems[0].problematic_object
