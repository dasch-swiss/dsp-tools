# mypy: disable-error-code="method-assign,no-untyped-def"

from rdflib import Graph

from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import _get_all_onto_classes
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import get_msg_str_unknown_classes_in_data
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from test.unittests.commands.validate_data.constants import PREFIXES

ONTO_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
NON_EXISTING_ONTO = "http://0.0.0.0:3333/ontology/9999/non-existent/v2#"
CLASSES_IN_ONTO = {
    f"{ONTO_STR}One",
    f"{KNORA_API_STR}LinkObj",
    f"{KNORA_API_STR}Region",
    f"{KNORA_API_STR}AudioSegment",
    f"{KNORA_API_STR}VideoSegment",
}
PREFIXED_IN_ONTO = {reformat_onto_iri(x) for x in CLASSES_IN_ONTO}


def _get_rdf_graphs(data_graph: Graph) -> RDFGraphs:
    ttl = f"""{PREFIXES}
    onto:One a owl:Class ;
            knora-api:isResourceClass true ;
            knora-api:canBeInstantiated true .

    knora-api:TextValue a owl:Class ;
            knora-api:isValueClass true .
    """
    onto_g = Graph()
    onto_g.parse(data=ttl, format="turtle")
    knora_subset = Graph()
    knora_subset.parse("testdata/validate-data/knora-api-subset.ttl")
    return RDFGraphs(
        data=data_graph, ontos=onto_g, cardinality_shapes=Graph(), content_shapes=Graph(), knora_api=knora_subset
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
        result = check_for_unknown_resource_classes(graphs, CLASSES_IN_ONTO)
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
        result = check_for_unknown_resource_classes(graphs, used_iris)
        assert isinstance(result, UnknownClassesInData)
        assert result.unknown_classes == {"onto:NonExistent"}
        assert result.defined_classes == PREFIXED_IN_ONTO
        expected_msg = (
            "Your data uses resource classes that do not exist in the ontologies in the database.\n"
            "The following classes that are used in the data are unknown: onto:NonExistent\n"
            "The following classes exist in the uploaded ontologies: "
            "AudioSegment, LinkObj, Region, VideoSegment, onto:One"
        )
        res_msg = get_msg_str_unknown_classes_in_data(result)
        assert res_msg == expected_msg

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
        result = check_for_unknown_resource_classes(graphs, used_iris)
        assert isinstance(result, UnknownClassesInData)
        assert result.unknown_classes == {"non-existent:One"}
        assert result.defined_classes == PREFIXED_IN_ONTO
        expected_msg = (
            "Your data uses ontologies that don't exist in the database.\n"
            "The following ontologies that are used in the data are unknown: non-existent\n"
            "The following ontologies are uploaded: onto"
        )
        res_msg = get_msg_str_unknown_classes_in_data(result)
        assert res_msg == expected_msg

    def test_get_all_onto_classes(self):
        graphs = _get_rdf_graphs(Graph())
        all_user_facing_classes = _get_all_onto_classes(graphs)
        assert all_user_facing_classes == CLASSES_IN_ONTO
