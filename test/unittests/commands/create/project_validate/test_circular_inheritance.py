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


class TestMakeInheritanceGraphForClasses:
    def test_create_simple_linear_graph(self):
        classes = [
            ParsedClass(name="ClassA", labels={"en": "A"}, comments=None, supers=["ClassB"], onto_iri="onto"),
            ParsedClass(name="ClassB", labels={"en": "B"}, comments=None, supers=[], onto_iri="onto"),
        ]
        graph = _make_inheritance_graph_for_classes(classes)
        assert graph.num_nodes() == 2
        assert graph.num_edges() == 1

    def test_create_graph_with_circular_dependency(self):
        classes = [
            ParsedClass(name="ClassA", labels={"en": "A"}, comments=None, supers=["ClassB"], onto_iri="onto"),
            ParsedClass(name="ClassB", labels={"en": "B"}, comments=None, supers=["ClassA"], onto_iri="onto"),
        ]
        graph = _make_inheritance_graph_for_classes(classes)
        assert graph.num_nodes() == 2
        assert graph.num_edges() == 2

    def test_ignores_knora_base_classes(self):
        classes = [
            ParsedClass(
                name="ClassA",
                labels={"en": "A"},
                comments=None,
                supers=["http://api.knora.org/ontology/knora-api/v2#Resource"],
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
                name="PropA",
                labels={"en": "A"},
                comments=None,
                supers=["PropB"],
                object="text",
                subject=None,
                gui_element=GuiElement.SIMPLETEXT,
                node_name=None,
                onto_iri="onto",
            ),
            ParsedProperty(
                name="PropB",
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
        node_a = graph.add_node("http://example.org/ClassA")
        node_b = graph.add_node("http://example.org/ClassB")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_b, node_a, None)

        errors = _find_and_format_inheritance_cycles(graph, "class")

        assert len(errors) == 1
        assert "ClassA" in errors[0].problematic_object
        assert "ClassB" in errors[0].problematic_object
        assert errors[0].problem == InputProblemType.CIRCULAR_CLASS_INHERITANCE

    def test_find_three_node_cycle(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node("http://example.org/ClassA")
        node_b = graph.add_node("http://example.org/ClassB")
        node_c = graph.add_node("http://example.org/ClassC")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_b, node_c, None)
        graph.add_edge(node_c, node_a, None)

        errors = _find_and_format_inheritance_cycles(graph, "class")

        assert len(errors) == 1
        assert "ClassA" in errors[0].problematic_object
        assert "ClassB" in errors[0].problematic_object
        assert "ClassC" in errors[0].problematic_object

    def test_find_no_cycles_in_linear_graph(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node("http://example.org/ClassA")
        node_b = graph.add_node("http://example.org/ClassB")
        node_c = graph.add_node("http://example.org/ClassC")
        graph.add_edge(node_a, node_b, None)
        graph.add_edge(node_b, node_c, None)

        errors = _find_and_format_inheritance_cycles(graph, "class")

        assert len(errors) == 0

    def test_self_reference_cycle(self):
        graph: rx.PyDiGraph = rx.PyDiGraph()
        node_a = graph.add_node("http://example.org/ClassA")
        graph.add_edge(node_a, node_a, None)

        errors = _find_and_format_inheritance_cycles(graph, "class")

        assert len(errors) == 1
        assert "ClassA" in errors[0].problematic_object


class TestCheckCircularInheritanceInClasses:
    def test_no_classes_returns_none(self):
        result = _check_circular_inheritance_in_classes([])
        assert result is None

    def test_linear_inheritance_returns_none(self):
        classes = [
            ParsedClass(name="ClassA", labels={"en": "A"}, comments=None, supers=["ClassB"], onto_iri="onto"),
            ParsedClass(name="ClassB", labels={"en": "B"}, comments=None, supers=[], onto_iri="onto"),
        ]
        result = _check_circular_inheritance_in_classes(classes)
        assert result is None

    def test_circular_inheritance_returns_problems(self):
        classes = [
            ParsedClass(name="ClassA", labels={"en": "A"}, comments=None, supers=["ClassB"], onto_iri="onto"),
            ParsedClass(name="ClassB", labels={"en": "B"}, comments=None, supers=["ClassA"], onto_iri="onto"),
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
                name="PropA",
                labels={"en": "A"},
                comments=None,
                supers=["PropB"],
                object="text",
                subject=None,
                gui_element=GuiElement.SIMPLETEXT,
                node_name=None,
                onto_iri="onto",
            ),
            ParsedProperty(
                name="PropB",
                labels={"en": "B"},
                comments=None,
                supers=["PropA"],
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
