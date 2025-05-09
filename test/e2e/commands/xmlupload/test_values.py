# mypy: disable-error-code="no-untyped-def"


from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias
from test.e2e.commands.xmlupload.conftest import _util_get_res_iri_from_label

BASE_NUMBER_OF_TRIPLES_PER_VALUE = 0


def _assert_number_of_values_is_one_and_get_val_iri(g: Graph, label: str, prop_iri: URIRef) -> SubjectObjectTypeAlias:
    res_iri = _util_get_res_iri_from_label(g, label)
    val_iri_list = list(g.objects(res_iri, prop_iri))
    assert len(val_iri_list) == 1
    return val_iri_list.pop(0)


def test_all_triples_of_a_value(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "", prop_iri)


def test_(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API))
    assert actual_value == expected_val
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE
