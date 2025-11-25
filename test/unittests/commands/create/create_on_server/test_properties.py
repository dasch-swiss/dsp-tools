# mypy: disable-error-code="no-untyped-def"

import pytest

from dsp_tools.commands.create.create_on_server.properties import _get_property_create_order
from dsp_tools.commands.create.create_on_server.properties import _make_graph_to_sort
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import KnoraObjectType
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty

KNORA_SUPER = "http://api.knora.org/ontology/knora-api/v2#hasValue"
EXTERNAL_SUPER = "http://xmlns.com/foaf/0.1/name"


def make_test_property(name: str, supers: list[str] | None = None) -> ParsedProperty:
    """Helper function to create a test property with standard defaults."""
    supr = supers if supers else []
    supr.append(KNORA_SUPER)
    full_name = f"http://api.knora.org/ontology/0001/onto/v2#{name}"
    return ParsedProperty(
        name=full_name,
        labels={"en": f"Label for {name}"},
        comments=None,
        supers=supr,
        object=KnoraObjectType.TEXT,
        subject=None,
        gui_element=GuiElement.SIMPLETEXT,
        node_name=None,
        onto_name="onto",
    )


@pytest.fixture
def three_multiple_inheritance_props():
    """PropA inherits from both PropB and PropC (both independent)."""
    prop_b = make_test_property("PropB")
    prop_c = make_test_property("PropC")
    prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])
    return [prop_a, prop_b, prop_c]


@pytest.fixture
def three_independent_props():
    """PropA inherits from both PropB and PropC (both independent)."""
    prop_b = make_test_property("PropB")
    prop_c = make_test_property("PropC")
    prop_a = make_test_property("PropA")
    return [prop_a, prop_b, prop_c]


class TestGetPropertyOrder:
    def test_multiple_inheritance_scenario(self, three_multiple_inheritance_props):
        prop_a, _, _ = three_multiple_inheritance_props
        result = _get_property_create_order(three_multiple_inheritance_props)
        # A has edges to both B and C, so A comes before both
        # the order afterwards does not matter
        assert len(result) == 3
        assert result[0] == prop_a.name

    def test_external_supers_do_not_break_sorting(self):
        p_b = make_test_property("PropB", supers=[])
        p_a = make_test_property("PropA", supers=[p_b.name])
        result = _get_property_create_order([p_a, p_b])
        # A has edge to B, so A comes before B
        assert result == [p_a.name, p_b.name]
        assert KNORA_SUPER not in result


class TestMakeGraphToSort:
    def test_creates_graph_with_multiple_properties_no_internal_dependencies(self, three_independent_props):
        graph, node_to_iri = _make_graph_to_sort(three_independent_props)
        assert len(graph) == 3
        assert graph.num_edges() == 0  # No internal dependencies
        assert all(p.name in node_to_iri.values() for p in three_independent_props)

    def test_creates_graph_with_multiple_supers(self, three_multiple_inheritance_props):
        graph, _node_to_iri = _make_graph_to_sort(three_multiple_inheritance_props)
        assert len(graph) == 3
        assert graph.num_edges() == 2

    def test_creates_correct_node_to_iri_mapping(self, three_independent_props):
        _graph, node_to_iri = _make_graph_to_sort(three_independent_props)
        assert len(node_to_iri) == 3
        iris_in_mapping = set(node_to_iri.values())
        expected_iris = {p.name for p in three_independent_props}
        assert iris_in_mapping == expected_iris
