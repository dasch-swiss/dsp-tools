# mypy: disable-error-code="no-untyped-def"


from rdflib import RDF
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias
from test.e2e.commands.xmlupload.conftest import _util_get_res_iri_from_label

BASE_NUMBER_OF_TRIPLES_PER_VALUE = 9
OPEN_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
)
DOAP_PERMISSIONS = Literal("CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember")


def _assert_number_of_values_is_one_and_get_val_iri(g: Graph, label: str, prop_iri: URIRef) -> SubjectObjectTypeAlias:
    res_iri = _util_get_res_iri_from_label(g, label)
    val_iri_list = list(g.objects(res_iri, prop_iri))
    assert len(val_iri_list) == 1
    return val_iri_list.pop(0)


def test_all_triples_of_a_value(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testBoolean")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(
        class_with_everything_resource_graph, "bool_true", prop_iri
    )
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    props = [
        KNORA_API.arkUrl,
        KNORA_API.versionArkUrl,
        KNORA_API.userHasPermission,
        KNORA_API.attachedToUser,
        KNORA_API.valueHasUUID,
        KNORA_API.hasPermissions,
        RDF.type,
        KNORA_API.booleanValueAsBoolean,
        KNORA_API.valueCreationDate,
    ]
    for prp in props:
        assert len(list(class_with_everything_resource_graph.objects(val_iri, prp))) == 1
    assert len(val_triples) == len(props)


def test_doap(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testBoolean")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(
        class_with_everything_resource_graph, "bool_true", prop_iri
    )
    permissions = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.hasPermissions))
    assert permissions == DOAP_PERMISSIONS


def test_bool_true(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testBoolean")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(
        class_with_everything_resource_graph, "bool_true", prop_iri
    )
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal(True)
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.booleanValueAsBoolean))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.BooleanValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


# def test_(class_with_everything_resource_graph, onto_iri):
#     prop_iri = URIRef(f"{onto_iri}")
#     val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "", prop_iri)
#     val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
#     expected_val = Literal("")
#     actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API))
#     assert actual_value == expected_val
#     assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE
