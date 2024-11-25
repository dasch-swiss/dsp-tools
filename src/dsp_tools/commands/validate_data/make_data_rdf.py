from typing import Callable

from rdflib import XSD
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.data_deserialised import AbstractFileValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import AbstractResource
from dsp_tools.commands.validate_data.models.data_deserialised import AnnotationDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import AudioSegmentDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DataDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IIIFUriDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import LinkObjDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RegionDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import UriValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import VideoSegmentDeserialised
from dsp_tools.commands.validate_data.models.data_rdf import AbstractFileValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import BooleanValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ColorValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import DataRDF
from dsp_tools.commands.validate_data.models.data_rdf import DateValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import DecimalValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import GeonameValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import IntValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import LinkValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ListValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import MovingImageFileValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import RDFTriples
from dsp_tools.commands.validate_data.models.data_rdf import ResourceRDF
from dsp_tools.commands.validate_data.models.data_rdf import RichtextRDF
from dsp_tools.commands.validate_data.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.validate_data.models.data_rdf import TimeValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import UriValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ValueRDF
from dsp_tools.models.exceptions import InternalError

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")
DATA = Namespace("http://data/")


def make_data_rdf(data_deserialised: DataDeserialised) -> DataRDF:
    """
    Transforms the deserialised data into instances that can produce a RDF graph.

    Args:
        data_deserialised: Deserialised Data

    Returns:
        Instance with the data
    """
    all_triples: list[RDFTriples] = []
    for r in data_deserialised.resources:
        all_triples.extend(_transform_one_resource(r))
    file_values: list[RDFTriples] = [
        transformed for x in data_deserialised.file_values if (transformed := _transform_file_value(x))
    ]
    all_triples.extend(file_values)
    return DataRDF(all_triples)


def _transform_one_resource(res: AbstractResource) -> list[RDFTriples]:
    if isinstance(res, ResourceDeserialised):
        return _transform_one_project_resource(res)
    return [_transform_one_dsp_resource(res)]


def _transform_one_dsp_resource(res: AbstractResource) -> RDFTriples:
    res_type_mapper = {
        AnnotationDeserialised: KNORA_API.Annotation,
        RegionDeserialised: KNORA_API.Region,
        LinkObjDeserialised: KNORA_API.LinkObj,
        VideoSegmentDeserialised: KNORA_API.VideoSegment,
        AudioSegmentDeserialised: KNORA_API.AudioSegment,
    }
    return ResourceRDF(
        res_iri=DATA[res.res_id], res_class=res_type_mapper[type(res)], label=Literal(res.label, datatype=XSD.string)
    )


def _transform_one_project_resource(res: ResourceDeserialised) -> list[RDFTriples]:
    res_iri = DATA[res.res_id]
    all_triples: list[RDFTriples] = [
        ResourceRDF(res_iri=res_iri, res_class=URIRef(res.res_class), label=Literal(res.label, datatype=XSD.string))
    ]
    all_triples.extend([_transform_one_value(v, res_iri) for v in res.values])
    return all_triples


def _transform_one_value(val: ValueDeserialised, res_iri: URIRef) -> ValueRDF:  # noqa: PLR0911 (too many return statements)
    func_mapper = {
        ColorValueDeserialised: ColorValueRDF,
        DateValueDeserialised: DateValueRDF,
        GeonameValueDeserialised: GeonameValueRDF,
        IntValueDeserialised: IntValueRDF,
        SimpleTextDeserialised: SimpleTextRDF,
        RichtextDeserialised: RichtextRDF,
    }
    match val:
        case (
            ColorValueDeserialised()
            | DateValueDeserialised()
            | GeonameValueDeserialised()
            | SimpleTextDeserialised()
            | RichtextDeserialised()
        ):
            return _transform_into_xsd_string(val, res_iri, func_mapper[type(val)])
        case IntValueDeserialised():
            return _transform_into_xsd_integer(val, res_iri, func_mapper[type(val)])
        case BooleanValueDeserialised():
            return _transform_into_bool(val, res_iri)
        case DecimalValueDeserialised():
            return _transform_decimal_value(val, res_iri)
        case LinkValueDeserialised():
            return _transform_link_value(val, res_iri)
        case ListValueDeserialised():
            return _transform_list_value(val, res_iri)
        case TimeValueDeserialised():
            return _transform_time_value(val, res_iri)
        case UriValueDeserialised():
            return _transform_uri_value(val, res_iri)
        case _:
            raise InternalError(f"Unknown Value Type: {type(val)}")


def _transform_into_xsd_string(
    val: ValueDeserialised, res_iri: URIRef, func: Callable[[URIRef, Literal, URIRef], ValueRDF]
) -> ValueRDF:
    new_str = val.object_value if val.object_value is not None else ""
    return func(URIRef(val.prop_name), Literal(new_str, datatype=XSD.string), res_iri)


def _transform_into_xsd_integer(
    val: ValueDeserialised, res_iri: URIRef, func: Callable[[URIRef, Literal, URIRef], ValueRDF]
) -> ValueRDF:
    content = (
        Literal(val.object_value, datatype=XSD.integer)
        if val.object_value is not None
        else Literal("", datatype=XSD.string)
    )
    return func(URIRef(val.prop_name), content, res_iri)


def _transform_into_bool(val: ValueDeserialised, res_iri: URIRef) -> ValueRDF:
    match val.object_value:
        case "1" | "true":
            content = Literal(True, datatype=XSD.boolean)
        case "0" | "false":
            content = Literal(False, datatype=XSD.boolean)
        case _:
            content = Literal("", datatype=XSD.string)
    return BooleanValueRDF(URIRef(val.prop_name), content, res_iri)


def _transform_decimal_value(val: ValueDeserialised, res_iri: URIRef) -> ValueRDF:
    content = (
        Literal(val.object_value, datatype=XSD.decimal)
        if val.object_value is not None
        else Literal("", datatype=XSD.string)
    )
    return DecimalValueRDF(URIRef(val.prop_name), content, res_iri)


def _transform_link_value(val: ValueDeserialised, res_iri: URIRef) -> ValueRDF:
    content = val.object_value if val.object_value is not None else ""
    return LinkValueRDF(URIRef(val.prop_name), DATA[content], res_iri)


def _transform_list_value(val: ListValueDeserialised, res_iri: URIRef) -> ValueRDF:
    node_name = val.object_value if val.object_value is not None else ""
    return ListValueRDF(
        prop_name=URIRef(val.prop_name),
        object_value=Literal(node_name, datatype=XSD.string),
        list_name=Literal(val.list_name, datatype=XSD.string),
        res_iri=res_iri,
    )


def _transform_time_value(val: ValueDeserialised, res_iri: URIRef) -> ValueRDF:
    content = (
        Literal(val.object_value, datatype=XSD.dateTimeStamp)
        if val.object_value is not None
        else Literal("", datatype=XSD.string)
    )
    return TimeValueRDF(URIRef(val.prop_name), content, res_iri)


def _transform_uri_value(val: ValueDeserialised, res_iri: URIRef) -> ValueRDF:
    content = (
        Literal(val.object_value, datatype=XSD.anyURI)
        if val.object_value is not None
        else Literal("", datatype=XSD.string)
    )
    return UriValueRDF(URIRef(val.prop_name), content, res_iri)


def _transform_file_value(val: AbstractFileValueDeserialised) -> AbstractFileValueRDF | None:
    if isinstance(val, IIIFUriDeserialised):
        return None
    return _map_into_correct_file_value(val)


def _map_into_correct_file_value(val: AbstractFileValueDeserialised) -> AbstractFileValueRDF | None:
    res_iri = DATA[val.res_id]
    file_literal = Literal(val.value)
    file_extension = _get_file_extension(val.value)
    match file_extension:
        case "mp4":
            return MovingImageFileValueRDF(res_iri=res_iri, value=file_literal)
        case _:
            return None


def _get_file_extension(value: str | None) -> str:
    file_extension = ""
    if value and "." in value:
        file_extension = value.split(".")[-1].lower()
    return file_extension
