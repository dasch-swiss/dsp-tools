from uuid import uuid4

from rdflib import RDF
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from loguru import logger
from dsp_tools.commands.validate_data.constants import DATA
from dsp_tools.commands.validate_data.constants import TRIPLE_OBJECT_TYPE_TO_XSD
from dsp_tools.commands.validate_data.constants import TRIPLE_PROP_TYPE_TO_IRI_MAPPER
from dsp_tools.commands.validate_data.constants import VALUE_INFO_TO_RDF_MAPPER
from dsp_tools.commands.validate_data.constants import VALUE_INFO_TRIPLE_OBJECT_TYPE
from dsp_tools.commands.validate_data.models.data_deserialised import DataDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import KnoraValueType
from dsp_tools.commands.validate_data.models.data_deserialised import PropertyObject
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TripleObjectType
from dsp_tools.commands.validate_data.models.data_deserialised import ValueInformation


def make_data_rdf(data_deserialised: DataDeserialised) -> Graph:
    """
    Transforms the deserialised data into instances that can produce a RDF graph.

    Args:
        data_deserialised: Deserialised Data

    Returns:
        Graph with the data
    """
    logger.info("Creating the RDF data graph.")
    g = Graph()
    for r in data_deserialised.resources:
        g += _make_one_resource(r)
    return g


def _make_one_resource(res: ResourceDeserialised) -> Graph:
    res_iri = DATA[res.res_id]
    g = _make_property_objects_graph(res.property_objects, res_iri)
    for v in res.values:
        g += _make_one_value(v, res_iri)
    return g


def _make_one_value(val: ValueInformation, res_iri: URIRef) -> Graph:
    if val.knora_type == KnoraValueType.LINK_VALUE:
        link_val = val.user_facing_value if val.user_facing_value else ""
        triple_object: Literal | URIRef = DATA[link_val]
    else:
        triple_object = _make_one_rdflib_object(val.user_facing_value, VALUE_INFO_TRIPLE_OBJECT_TYPE[val.knora_type])
    prop_type_info = VALUE_INFO_TO_RDF_MAPPER[val.knora_type]

    val_iri = DATA[str(uuid4())]
    g = _make_property_objects_graph(val.value_metadata, val_iri)
    g.add((res_iri, URIRef(val.user_facing_prop), val_iri))
    g.add((val_iri, RDF.type, prop_type_info.knora_type))
    g.add((val_iri, prop_type_info.knora_prop, triple_object))
    return g


def _make_property_objects_graph(property_objects: list[PropertyObject], subject_iri: URIRef) -> Graph:
    g = Graph()
    for trpl in property_objects:
        object_val = _make_one_rdflib_object(trpl.object_value, trpl.object_type)
        g.add((subject_iri, TRIPLE_PROP_TYPE_TO_IRI_MAPPER[trpl.property_type], object_val))
    return g


def _make_one_rdflib_object(object_value: str | None, object_type: TripleObjectType) -> Literal | URIRef:
    if not object_value:
        return Literal("", datatype=XSD.string)
    if object_type == TripleObjectType.IRI:
        return URIRef(object_value)
    return Literal(object_value, datatype=TRIPLE_OBJECT_TYPE_TO_XSD[object_type])
