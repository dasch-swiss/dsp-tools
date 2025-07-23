from loguru import logger
from rdflib import RDF
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.xsd_datetime import parse_xsd_date

from dsp_tools.commands.validate_data.mappers import TRIPLE_OBJECT_TYPE_TO_XSD
from dsp_tools.commands.validate_data.mappers import TRIPLE_PROP_TYPE_TO_IRI_MAPPER
from dsp_tools.commands.validate_data.mappers import VALUE_INFO_TO_RDF_MAPPER
from dsp_tools.commands.validate_data.mappers import VALUE_INFO_TRIPLE_OBJECT_TYPE
from dsp_tools.commands.validate_data.models.rdf_like_data import PropertyObject
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeData
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeResource
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeValue
from dsp_tools.commands.validate_data.models.rdf_like_data import TripleObjectType
from dsp_tools.commands.validate_data.models.rdf_like_data import TriplePropertyType
from dsp_tools.utils.rdflib_constants import DATA
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType


def make_data_graph(data: RdfLikeData) -> Graph:
    logger.debug("Creating the RDF data graph.")
    g = Graph()
    for r in data.resources:
        g += _make_one_resource(r)
    return g


def _make_one_resource(res: RdfLikeResource) -> Graph:
    res_iri = DATA[res.res_id]
    g = _make_property_objects_graph(res.property_objects, res_iri)
    for v in res.values:
        g += _make_one_value(v, res_iri)
    return g


def _make_one_value(val: RdfLikeValue, res_iri: URIRef) -> Graph:
    prop_type_info = VALUE_INFO_TO_RDF_MAPPER[val.knora_type]

    val_iri = DATA[val.value_uuid]
    g = _make_property_objects_graph(val.value_metadata, val_iri)
    g.add((res_iri, URIRef(val.user_facing_prop), val_iri))
    g.add((val_iri, RDF.type, prop_type_info.knora_type))
    # The interval values are added in the property objects graph
    if val.knora_type == KnoraValueType.INTERVAL_VALUE:
        return g
    if val.knora_type == KnoraValueType.LINK_VALUE:
        link_val = val.user_facing_value if val.user_facing_value else ""
        triple_object: Literal | URIRef = DATA[link_val]
    else:
        triple_object = _make_one_rdflib_object(val.user_facing_value, VALUE_INFO_TRIPLE_OBJECT_TYPE[val.knora_type])
    g.add((val_iri, prop_type_info.knora_prop, triple_object))
    return g


def _make_property_objects_graph(property_objects: list[PropertyObject], subject_iri: URIRef) -> Graph:
    g = Graph()
    for trpl in property_objects:
        object_val = _make_one_rdflib_object(trpl.object_value, trpl.object_type, trpl.property_type)
        g.add((subject_iri, TRIPLE_PROP_TYPE_TO_IRI_MAPPER[trpl.property_type], object_val))
    return g


def _make_one_rdflib_object(
    object_value: str | None, object_type: TripleObjectType, prop_type: TriplePropertyType | None = None
) -> Literal | URIRef:
    if not object_value:
        return Literal("", datatype=XSD.string)
    if object_type == TripleObjectType.IRI:
        return URIRef(object_value)
    if object_type == TripleObjectType.INTERNAL_ID:
        return DATA[object_value]
    if prop_type in (TriplePropertyType.KNORA_DATE_START, TriplePropertyType.KNORA_DATE_END):
        return _process_date_string(object_value, object_type)
    return Literal(object_value, datatype=TRIPLE_OBJECT_TYPE_TO_XSD[object_type])


def _process_date_string(object_value: str, object_type: TripleObjectType) -> Literal:
    # In case a date is not a valid xsd datatype, rdflib only raises the error when serialising the graph
    # not during the construction of the literal.
    # Therefore, we test the validity beforehand with the rdflib native functions.
    try:
        parse_xsd_date(object_value)
        return Literal(object_value, datatype=TRIPLE_OBJECT_TYPE_TO_XSD[object_type])
    except ValueError:
        return Literal(object_value, datatype=XSD.string)
