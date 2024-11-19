from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryResource
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryValue
from dsp_tools.commands.xmlupload.models.resource_value_models import PropertyObject
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
            case IntermediaryBoolean():
                values.append(_literal_value(val, XSD.boolean))
            case _:
                ...  # continue in the same manner


def _literal_value(value: IntermediaryValue, value_type_info: ValueTypeTripleInfo) -> list[PropertyObject]:
    bn = BNode()
    triples = _make_optional_triples(bn, value)
    triples.append(PropertyObject(bn, value_type_info.prop_name, Literal(value, datatype=value_type_info.d_type)))
    triples.append(PropertyObject(bn, RDF.type, value_type_info.rdf_type))
    return triples


def _make_optional_triples(bn: BNode, value: IntermediaryValue) -> list[PropertyObject]:
    optionals = []
    if value.permissions:
        optionals.append(_make_permissions(bn, value.permissions))
    if value.comment:
        cmt = PropertyObject(bn, KNORA_API.valueHasComment, Literal(value.comment, datatype=XSD.string))
        optionals.append(cmt)
    return optionals


def _make_permissions(bn: BNode, permission: Permissions) -> PropertyObject:
    return PropertyObject(bn, KNORA_API.hasPermissions, Literal(str(permission), datatype=XSD.string))
