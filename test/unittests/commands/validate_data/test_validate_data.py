# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest
from rdflib import Graph

from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.validate_data import _check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validate_data import _get_all_onto_classes
from test.unittests.commands.validate_data.constants import PREFIXES

ONTO_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
NON_EXISTING_ONTO = "http://0.0.0.0:3333/ontology/9999/non-existent/v2#"

PREFIXED_IN_ONTO = {"onto:One"}
CLASSES_IN_ONTO = {f"{ONTO_STR}One"}


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
    def test_check_for_unknown_resource_classes_data_ok(self):
        ttl = f"""{PREFIXES}
        <http://data/identical_text_different_prop> a onto:One ;
                onto:testSimpleText <http://data/textValue> .

        <http://data/textValue> a knora-api:TextValue ;
                knora-api:valueAsString "Text"^^xsd:string .
        """
        g = Graph()
        g.parse(data=ttl, format="turtle")
        graphs = _get_rdf_graphs(g)
        result = _check_for_unknown_resource_classes(graphs, CLASSES_IN_ONTO)
        assert not result

    def test_check_for_unknown_resource_classes_data_wrong(self):
        ttl = f"""{PREFIXES}
        <http://data/identical_text_different_prop> a onto:NonExistent ;
                onto:testSimpleText <http://data/textValue> .

        <http://data/textValue> a knora-api:TextValue ;
                knora-api:valueAsString "Text"^^xsd:string .
        """
        g = Graph()
        g.parse(data=ttl, format="turtle")
        graphs = _get_rdf_graphs(g)
        used_iris = {f"{ONTO_STR}NonExistent"}
        result = _check_for_unknown_resource_classes(graphs, used_iris)
        assert isinstance(result, UnknownClassesInData)
        assert result.unknown_classes == {"onto:NonExistent"}
        assert result.classes_onto == PREFIXED_IN_ONTO
        assert result._get_unknown_ontos_msg() == ""

    def test_check_for_unknown_resource_classes_data_prefix_non_existent(self):
        ttl = f"""{PREFIXES}
        @prefix  non-existent: <{NON_EXISTING_ONTO}> .

        <http://data/identical_text_different_prop> a non-existent:One ;
                onto:testSimpleText <http://data/textValue> .

        <http://data/textValue> a knora-api:TextValue ;
                knora-api:valueAsString "Text"^^xsd:string .
        """
        g = Graph()
        g.parse(data=ttl, format="turtle")
        graphs = _get_rdf_graphs(g)
        used_iris = {f"{NON_EXISTING_ONTO}One"}
        result = _check_for_unknown_resource_classes(graphs, used_iris)
        assert isinstance(result, UnknownClassesInData)
        assert result.unknown_classes == {"non-existent:One"}
        assert result.classes_onto == PREFIXED_IN_ONTO
        expected_msg = (
            "Your data uses ontologies that don't exist in the database.\n"
            "The following ontologies that are used in the data are unknown: non-existent\n"
            "The following ontologies are uploaded: onto"
        )
        assert result._get_unknown_ontos_msg() == expected_msg

    def test_get_all_onto_classes(self):
        ttl = f"""{PREFIXES}
        onto:One a owl:Class ;
                knora-api:isResourceClass true .

        knora-api:TextValue a owl:Class ;
                knora-api:isValueClass true .
        """
        g = Graph()
        g.parse(data=ttl, format="turtle")
        assert _get_all_onto_classes(g) == {f"{ONTO_STR}One"}


if __name__ == "__main__":
    pytest.main([__file__])
