from uuid import uuid4

from rdflib import RDF
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.constants import DATA
from dsp_tools.commands.validate_data.constants import KNORA_API
from dsp_tools.commands.validate_data.constants import TRIPLE_OBJECT_TYPE_TO_XSD
from dsp_tools.commands.validate_data.constants import TRIPLE_PROP_TYPE_TO_IRI_MAPPER
from dsp_tools.commands.validate_data.constants import VALUE_INFO_TO_RDF_MAPPER
from dsp_tools.commands.validate_data.constants import VALUE_INFO_TRIPLE_OBJECT_TYPE
from dsp_tools.commands.validate_data.models.data_deserialised import AbstractFileValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DataDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IIIFUriDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import KnoraValueType
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TripleObjectType
from dsp_tools.commands.validate_data.models.data_deserialised import ValueInformation
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import IIIF_URI_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import get_file_type_info
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.models.exceptions import BaseError


def make_data_rdf(data_deserialised: DataDeserialised) -> Graph:
    """
    Transforms the deserialised data into instances that can produce a RDF graph.

    Args:
        data_deserialised: Deserialised Data

    Returns:
        Graph with the data
    """
    g = Graph()
    for r in data_deserialised.resources:
        g += _make_one_resource(r)
    for f in data_deserialised.file_values:
        g += _make_file_value(f)
    return g


def _make_one_resource(res: ResourceDeserialised) -> Graph:
    res_iri = DATA[res.res_id]
    g = Graph()
    for trpl in res.property_objects:
        object_val = _make_one_rdflib_object(trpl.object_value, trpl.object_type)
        g.add((res_iri, TRIPLE_PROP_TYPE_TO_IRI_MAPPER[trpl.property_type], object_val))
    for v in res.values:
        g += _make_one_value(v, res_iri)
    return g


def _make_one_value(val: ValueInformation, res_iri: URIRef) -> Graph:
    if val.knora_type == KnoraValueType.LINK_VALUE and val.user_facing_value:
        triple_object: Literal | URIRef = DATA[val.user_facing_value]
    else:
        triple_object = _make_one_rdflib_object(val.user_facing_value, VALUE_INFO_TRIPLE_OBJECT_TYPE[val.knora_type])
    prop_type_info = VALUE_INFO_TO_RDF_MAPPER[val.knora_type]

    g = Graph()
    val_iri = DATA[str(uuid4())]
    g.add((res_iri, URIRef(val.user_facing_prop), val_iri))
    g.add((val_iri, RDF.type, prop_type_info.knora_type))
    g.add((val_iri, prop_type_info.knora_prop, triple_object))
    return g


def _make_one_rdflib_object(object_value: str | None, object_type: TripleObjectType) -> Literal | URIRef:
    if not object_value:
        return Literal("", datatype=XSD.string)
    if object_type == TripleObjectType.IRI:
        return URIRef(object_value)
    return Literal(object_value, datatype=TRIPLE_OBJECT_TYPE_TO_XSD[object_type])


def _make_file_value(val: AbstractFileValueDeserialised) -> Graph:
    if val.value is None:
        return Graph()
    if isinstance(val, IIIFUriDeserialised):
        return _make_file_value_graph(val, IIIF_URI_VALUE, KNORA_API.stillImageFileValueHasExternalUrl)
    try:
        file_type = get_file_type_info(val.value)
        return _make_file_value_graph(val, file_type)
    except BaseError:
        return Graph()


def _make_file_value_graph(
    val: AbstractFileValueDeserialised,
    prop_type_info: RDFPropTypeInfo,
    prop_to_value: URIRef = KNORA_API.fileValueHasFilename,
) -> Graph:
    g = Graph()
    res_iri = DATA[val.res_id]
    val_iri = DATA[str(uuid4())]
    g.add((res_iri, prop_type_info.knora_prop, val_iri))
    g.add((val_iri, RDF.type, prop_type_info.knora_type))
    g.add((val_iri, prop_to_value, Literal(val.value, datatype=prop_type_info.xsd_type)))
    return g
