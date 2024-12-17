from uuid import uuid4

from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.constants import API_SHAPES
from dsp_tools.commands.validate_data.constants import DATA
from dsp_tools.commands.validate_data.constants import KNORA_API
from dsp_tools.commands.validate_data.models.data_deserialised import AbstractFileValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DataDeserialised
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
from dsp_tools.commands.validate_data.models.data_deserialised import UriValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ValueDeserialised
from dsp_tools.commands.validate_data.models.data_rdf import FileValueRDF
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import ARCHIVE_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import AUDIO_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import BOOLEAN_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import COLOR_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import DECIMAL_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import DOCUMENT_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import GEONAME_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import IIIF_URI_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import INT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import MOVING_IMAGE_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import RICHTEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import SIMPLE_TEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import STILL_IMAGE_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import TEXT_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import TIME_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import URI_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
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
        g += _transform_file_value(f)
    return g


def _make_one_resource(res: ResourceDeserialised) -> Graph:
    res_iri = DATA[res.res_id]
    g = Graph()
    g.add((res_iri, RDF.type, URIRef(res.res_class)))
    g.add((res_iri, RDFS.label, Literal(res.label, datatype=XSD.string)))
    for v in res.values:
        g += _make_one_value(v, res_iri)
    return g


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
            return _transform_link_value(val, res_iri)
        case ListValueDeserialised():
            return _transform_list_value(val, res_iri)
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


def _transform_link_value(val: ValueDeserialised, res_iri: URIRef) -> Graph:
    object_value = val.object_value if val.object_value is not None else ""
    g = Graph()
    val_iri = DATA[str(uuid4())]
    g.add((val_iri, RDF.type, KNORA_API.LinkValue))
    g.add((val_iri, API_SHAPES.linkValueHasTargetID, DATA[object_value]))
    g.add((res_iri, URIRef(val.prop_name), val_iri))
    return g


def _transform_list_value(val: ListValueDeserialised, res_iri: URIRef) -> Graph:
    node_name = val.object_value if val.object_value is not None else ""
    g = Graph()
    val_iri = DATA[str(uuid4())]
    g.add((val_iri, RDF.type, KNORA_API.ListValue))
    g.add((val_iri, API_SHAPES.listNodeAsString, Literal(node_name, datatype=XSD.string)))
    g.add((val_iri, API_SHAPES.listNameAsString, Literal(val.list_name, datatype=XSD.string)))
    g.add((res_iri, URIRef(val.prop_name), val_iri))
    return g


def _transform_file_value(val: AbstractFileValueDeserialised) -> Graph:
    if isinstance(val, IIIFUriDeserialised):
        return FileValueRDF(
            res_iri=DATA[val.res_id],
            value=Literal(val.value, datatype=XSD.anyURI),
            prop_type_info=IIIF_URI_VALUE,
            prop_to_value=KNORA_API.stillImageFileValueHasExternalUrl,
        ).make_graph()
    return _map_into_correct_file_value(val)


def _map_into_correct_file_value(val: AbstractFileValueDeserialised) -> Graph:
    res_iri = DATA[val.res_id]
    file_literal = Literal(val.value, datatype=XSD.string)
    file_extension = _get_file_extension(val.value)
    match file_extension:
        case "zip" | "tar" | "gz" | "z" | "tgz" | "gzip" | "7z":
            file_type = ARCHIVE_FILE_VALUE
        case "mp3" | "wav":
            file_type = AUDIO_FILE_VALUE
        case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
            file_type = DOCUMENT_FILE_VALUE
        case "mp4":
            file_type = MOVING_IMAGE_FILE_VALUE
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "csv" | "json":
            file_type = TEXT_FILE_VALUE
        # jpx is the extension of the files returned by dsp-ingest
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff" | "jpx":
            file_type = STILL_IMAGE_FILE_VALUE
        case _:
            return Graph()
    return FileValueRDF(res_iri=res_iri, value=file_literal, prop_type_info=file_type).make_graph()


def _get_file_extension(value: str | None) -> str:
    file_extension = ""
    if value and "." in value:
        file_extension = value.split(".")[-1].lower()
    return file_extension
