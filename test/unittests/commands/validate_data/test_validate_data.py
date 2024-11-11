import pytest
from rdflib import Graph

from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.validate_data import _check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validate_data import _get_all_onto_classes
from dsp_tools.commands.validate_data.validate_data import _get_all_used_classes
from test.unittests.commands.validate_data.constants import PREFIXES


@pytest.fixture
def onto() -> Graph:
    ttl = f"""{PREFIXES}
    onto:One a owl:Class ;
            knora-api:isResourceClass true .
    
    knora-api:TextValue a owl:Class ;
            knora-api:isValueClass true .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


@pytest.fixture
def data_ok() -> Graph:
    ttl = f"""{PREFIXES}
    <http://data/identical_text_different_prop> a onto:One ;
            onto:testSimpleText <http://data/textValue> .
    
    <http://data/textValue> a knora-api:TextValue ;
            knora-api:valueAsString "Text"^^xsd:string .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


@pytest.fixture
def data_wrong() -> Graph:
    ttl = f"""{PREFIXES}
    <http://data/identical_text_different_prop> a onto:NonExistent ;
            onto:testSimpleText <http://data/textValue> .

    <http://data/textValue> a knora-api:TextValue ;
            knora-api:valueAsString "Text"^^xsd:string .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


@pytest.fixture
def data_prefix_non_existent() -> Graph:
    ttl = f"""{PREFIXES}
    @prefix  non-existing-onto: <http://0.0.0.0:3333/ontology/9999/non-existent/v2#> .
    
    <http://data/identical_text_different_prop> a non-existing-onto:One ;
            onto:testSimpleText <http://data/textValue> .
    
    <http://data/textValue> a knora-api:TextValue ;
            knora-api:valueAsString "Text"^^xsd:string .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


def _get_rdf_graphs(data_graph: Graph) -> RDFGraphs:
    ttl = f"""{PREFIXES}
    onto:One a owl:Class ;
            knora-api:isResourceClass true .

    knora-api:TextValue a owl:Class ;
            knora-api:isValueClass true .
    """
    onto_g = Graph()
    onto_g.parse(data=ttl, format="turtle")
    return RDFGraphs(
        data=data_graph, ontos=onto_g, cardinality_shapes=Graph(), content_shapes=Graph(), knora_api=Graph()
    )


class TestFindUnknownClasses:
    def test_check_for_unknown_resource_classes_data_ok(self, data_ok: Graph) -> None:
        graphs = _get_rdf_graphs(data_ok)
        result = _check_for_unknown_resource_classes(graphs)
        assert not result

    def test_check_for_unknown_resource_classes_data_wrong(self, data_wrong: Graph) -> None:
        graphs = _get_rdf_graphs(data_wrong)
        result = _check_for_unknown_resource_classes(graphs)
        assert isinstance(result, UnknownClassesInData)
        assert result.unknown_classes == {"onto:NonExistent"}
        assert result.classes_onto == {"onto:One"}
        assert result._get_unknown_ontos_msg() == ""

    def test_check_for_unknown_resource_classes_data_prefix_non_existent(self, data_prefix_non_existent: Graph) -> None:
        graphs = _get_rdf_graphs(data_prefix_non_existent)
        result = _check_for_unknown_resource_classes(graphs)
        assert isinstance(result, UnknownClassesInData)
        assert result.unknown_classes == {"non-existent:One"}
        assert result.classes_onto == {"onto:One"}
        assert result._get_unknown_ontos_msg() != ""

    def test_get_all_used_classes(self, data_ok: Graph) -> None:
        result = _get_all_used_classes(data_ok)
        expected = {"TextValue", "onto:One"}
        assert result == expected

    def test_get_all_onto_classes(self, onto: Graph) -> None:
        res_cls, value_cls = _get_all_onto_classes(onto)
        assert res_cls == {"onto:One"}
        assert value_cls == {"TextValue"}


if __name__ == "__main__":
    pytest.main([__file__])
