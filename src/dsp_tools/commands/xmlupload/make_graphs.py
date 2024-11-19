from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.intermediary_models import IntermediaryAbstractFileValue
from dsp_tools.commands.xmlupload.models.intermediary_models import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.intermediary_models import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary_models import IntermediaryValue
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.resource_value_models import RDFResource
from dsp_tools.commands.xmlupload.models.resource_value_models import RDFTriple
from dsp_tools.commands.xmlupload.models.resource_value_models import ValueTypeTripleInfo

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


prop_dtype_mapper = {
    IntermediaryBoolean: ValueTypeTripleInfo(
        rdf_type=KNORA_API.BooleanValue,
        d_type=XSD.boolean,
        prop_name=KNORA_API.booleanValueAsBoolean,
    )
}


def make_resource_rdf(resource: IntermediaryResource, id_to_iri_lookup: dict[str, str]) -> RDFResource:  # noqa:ARG001
    """
    Takes the intermediary resources and makes them into ones, that can be serialised as a graph.

    Args:
        resource: Resource to transform
        id_to_iri_lookup: To resolve references in richtext and link triples

    Returns:
        Resource that can be serialised as a graph.
    """
    triples = []
    res_bn = BNode()
    for val in resource.values:
        match val:
            case IntermediaryBoolean() as val_type:
                triples.append(_literal_value(val, prop_dtype_mapper[val_type], res_bn))
            case _:
                ...  # continue in the same manner
    triples.extend(_make_resource_triples(resource, res_bn))
    if resource.file_value:
        triples.extend(_make_file_triples(resource.file_value))
    graph = _make_graph(triples)
    return RDFResource(res_id=resource.res_id, res_bn=res_bn, graph=graph)


def _make_graph(triples: list[RDFTriple]) -> Graph:
    g = Graph()
    for trip in triples:
        g.add(trip.to_triple())
    return g


def _make_resource_triples(resource: IntermediaryResource, res_bn: BNode) -> list[RDFTriple]:
    triple_collection = [RDFTriple(res_bn, RDF.type, URIRef(resource.res_type))]
    if resource.permissions:
        triple_collection.append(_make_permissions(res_bn, resource.permissions))
    return triple_collection


def _literal_value(value: IntermediaryValue, value_type_info: ValueTypeTripleInfo, res_bn: BNode) -> list[RDFTriple]:
    bn = BNode()
    triples = _make_optional_triples(bn, value)
    literal_value = RDFTriple(bn, value_type_info.prop_name, Literal(value.value, datatype=value_type_info.d_type))
    triples.append(literal_value)
    triples.append(RDFTriple(res_bn, URIRef(value.prop_name), bn))
    triples.append(RDFTriple(bn, RDF.type, value_type_info.rdf_type))
    return triples


def _make_optional_triples(value_bn: BNode, value: IntermediaryValue) -> list[RDFTriple]:
    optionals = []
    if value.permissions:
        optionals.append(_make_permissions(value_bn, value.permissions))
    if value.comment:
        cmt = RDFTriple(value_bn, KNORA_API.valueHasComment, Literal(value.comment, datatype=XSD.string))
        optionals.append(cmt)
    return optionals


def _make_file_triples(file: IntermediaryAbstractFileValue) -> list[RDFTriple]:  # noqa:ARG001
    return []


def _make_permissions(subject_ref: URIRef | BNode, permission: Permissions) -> RDFTriple:
    return RDFTriple(subject_ref, KNORA_API.hasPermissions, Literal(str(permission), datatype=XSD.string))
