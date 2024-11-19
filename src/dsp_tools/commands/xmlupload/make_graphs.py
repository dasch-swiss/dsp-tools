from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryResource
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryValue
from dsp_tools.commands.xmlupload.models.resource_value_models import PropertyObject
from dsp_tools.commands.xmlupload.models.resource_value_models import PropertyObjectCollection
from dsp_tools.commands.xmlupload.models.resource_value_models import RDFResource
from dsp_tools.commands.xmlupload.models.resource_value_models import ValueTypeTripleInfo

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


prop_dtype_mapper = {
    IntermediaryBoolean: ValueTypeTripleInfo(
        rdf_type=KNORA_API.BooleanValue,
        d_type=XSD.boolean,
        prop_name=KNORA_API.booleanValueAsBoolean,
    )
}


def make_resource_rdf(resource: IntermediaryResource) -> RDFResource:
    values = []
    for val in resource.values:
        match val:
            case IntermediaryBoolean() as val_type:
                values.append(_literal_value(val, prop_dtype_mapper[val_type]))
            case _:
                ...  # continue in the same manner
    resource_triples = _make_resource_triples(resource)
    return RDFResource(res_bn=BNode(), resource_triples=resource_triples, values=values)


def _make_resource_triples(resource: IntermediaryResource) -> list[PropertyObject]:
    triple_collection = [PropertyObject(RDF.type, URIRef(resource.res_type))]
    if resource.permissions:
        triple_collection.append(_make_permissions(resource.permissions))
    return triple_collection


def _literal_value(value: IntermediaryValue, value_type_info: ValueTypeTripleInfo) -> PropertyObjectCollection:
    bn = BNode()
    triples = _make_optional_triples(value)
    triples.append(PropertyObject(value_type_info.prop_name, Literal(value, datatype=value_type_info.d_type)))
    triples.append(PropertyObject(RDF.type, value_type_info.rdf_type))
    return PropertyObjectCollection(bn=bn, prop_name=URIRef(value.prop_name), value_triples=triples)


def _make_optional_triples(value: IntermediaryValue) -> list[PropertyObject]:
    optionals = []
    if value.permissions:
        optionals.append(_make_permissions(value.permissions))
    if value.comment:
        cmt = PropertyObject(KNORA_API.valueHasComment, Literal(value.comment, datatype=XSD.string))
        optionals.append(cmt)
    return optionals


def _make_permissions(permission: Permissions) -> PropertyObject:
    return PropertyObject(KNORA_API.hasPermissions, Literal(str(permission), datatype=XSD.string))
