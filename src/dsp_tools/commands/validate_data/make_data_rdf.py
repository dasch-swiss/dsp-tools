from uuid import uuid4

from rdflib import RDF
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.constants import API_SHAPES
from dsp_tools.commands.validate_data.constants import DATA
from dsp_tools.commands.validate_data.constants import DATATYPES_TO_XSD
from dsp_tools.commands.validate_data.constants import KNORA_API
from dsp_tools.commands.validate_data.models.data_deserialised import AbstractFileValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DataDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DataTypes
from dsp_tools.commands.validate_data.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IIIFUriDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import UnreifiedTripleObject
from dsp_tools.commands.validate_data.models.data_deserialised import UriValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ValueDeserialised
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import BOOLEAN_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import COLOR_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import DECIMAL_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import GEONAME_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import IIIF_URI_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import INT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import RICHTEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import SIMPLE_TEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import TIME_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import URI_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import get_file_type_info
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InternalError

RDF_LITERAL_PROP_TYPE_MAPPER = {
    BooleanValueDeserialised: BOOLEAN_PROP_TYPE_INFO,
    ColorValueDeserialised: COLOR_PROP_TYPE_INFO,
    DateValueDeserialised: RDFPropTypeInfo(KNORA_API.DateValue, KNORA_API.valueAsString, XSD.string),
    DecimalValueDeserialised: DECIMAL_PROP_TYPE_INFO,
    GeonameValueDeserialised: GEONAME_PROP_TYPE_INFO,
    IntValueDeserialised: INT_PROP_TYPE_INFO,
    SimpleTextDeserialised: SIMPLE_TEXT_PROP_TYPE_INFO,
    RichtextDeserialised: RICHTEXT_PROP_TYPE_INFO,
    TimeValueDeserialised: TIME_PROP_TYPE_INFO,
    UriValueDeserialised: URI_PROP_TYPE_INFO,
}


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
    for trpl in res.unreified_triples:
        object_val = _make_one_rdflib_object(trpl)
        g.add((res_iri, URIRef(trpl.prop_name), object_val))
    for v in res.values:
        g += _make_one_value(v, res_iri)
    return g


def _make_one_rdflib_object(triple_object: UnreifiedTripleObject) -> Literal | URIRef:
    if not triple_object.object_value:
        return Literal("", datatype=XSD.string)
    if triple_object.data_type == DataTypes.iri:
        return URIRef(triple_object.object_value)
    return Literal(triple_object.object_value, datatype=DATATYPES_TO_XSD[triple_object.data_type])


def _make_one_value(val: ValueDeserialised, res_iri: URIRef) -> Graph:
    match val:
        case (
            BooleanValueDeserialised()
            | ColorValueDeserialised()
            | DateValueDeserialised()
            | DecimalValueDeserialised()
            | GeonameValueDeserialised()
            | IntValueDeserialised()
            | SimpleTextDeserialised()
            | RichtextDeserialised()
            | TimeValueDeserialised()
            | UriValueDeserialised()
        ):
            return _make_one_value_with_xsd_data_type(
                val=val,
                res_iri=res_iri,
                prop_type_info=RDF_LITERAL_PROP_TYPE_MAPPER[type(val)],
            )
        case LinkValueDeserialised():
            return _make_link_value(val, res_iri)
        case ListValueDeserialised():
            return _make_list_value(val, res_iri)
        case _:
            raise InternalError(f"Unknown Value Type: {type(val)}")


def _make_one_value_with_xsd_data_type(
    val: ValueDeserialised, res_iri: URIRef, prop_type_info: RDFPropTypeInfo
) -> Graph:
    g = Graph()
    val_iri = DATA[str(uuid4())]
    g.add((val_iri, RDF.type, prop_type_info.knora_type))
    if val.object_value:
        literal_value = Literal(val.object_value, datatype=prop_type_info.xsd_type)
    else:
        literal_value = Literal("", datatype=XSD.string)
    g.add((val_iri, prop_type_info.knora_prop, literal_value))
    g.add((res_iri, URIRef(val.prop_name), val_iri))
    return g


def _make_link_value(val: ValueDeserialised, res_iri: URIRef) -> Graph:
    object_value = val.object_value if val.object_value is not None else ""
    g = Graph()
    val_iri = DATA[str(uuid4())]
    g.add((val_iri, RDF.type, KNORA_API.LinkValue))
    g.add((val_iri, API_SHAPES.linkValueHasTargetID, DATA[object_value]))
    g.add((res_iri, URIRef(val.prop_name), val_iri))
    return g


def _make_list_value(val: ListValueDeserialised, res_iri: URIRef) -> Graph:
    node_name = val.object_value if val.object_value is not None else ""
    g = Graph()
    val_iri = DATA[str(uuid4())]
    g.add((val_iri, RDF.type, KNORA_API.ListValue))
    g.add((val_iri, API_SHAPES.listNodeAsString, Literal(node_name, datatype=XSD.string)))
    g.add((val_iri, API_SHAPES.listNameAsString, Literal(val.list_name, datatype=XSD.string)))
    g.add((res_iri, URIRef(val.prop_name), val_iri))
    return g


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
