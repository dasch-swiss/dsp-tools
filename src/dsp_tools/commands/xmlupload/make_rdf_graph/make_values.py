from pathlib import Path
from typing import Any
from typing import Callable
from typing import assert_never
from typing import cast

from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import KNORA_API
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import rdf_prop_type_mapper
from dsp_tools.commands.xmlupload.make_rdf_graph.helpers import resolve_permission
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_serialiser import serialise_property_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import InputTypes
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import assert_is_string
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import rdf_literal_transformer
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_date
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_interval
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.commands.xmlupload.models.rdf_models import TransformedValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseArchiveFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseAudioFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseDocumentFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseMovingImageFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseStillImageFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseTextFileValue
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.date_util import DayMonthYearEra
from dsp_tools.utils.date_util import SingleDate
from dsp_tools.utils.date_util import StartEnd
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.logger_config import WARNINGS_SAVEPATH


def make_values(resource: XMLResource, res_bnode: BNode, lookup: Lookups) -> dict[str, Any]:
    """
    Serialise the values of a resource.

    Args:
        resource: XMLResource
        res_bnode: blank node of the resource
        lookup: lookups to resolve, permissions, IRIs, etc.

    Returns:
        Values serialised as a dict
    """
    properties_graph = Graph()
    # To frame the json-ld correctly, we need one property used in the graph. It does not matter which.
    last_prop_name = None

    for prop in resource.properties:
        single_prop_graph, last_prop_name = _make_one_prop_graph(
            prop=prop, restype=resource.restype, res_bnode=res_bnode, lookup=lookup
        )
        properties_graph += single_prop_graph

    if resource.iiif_uri:
        properties_graph += _make_iiif_uri_value(resource.iiif_uri, res_bnode, lookup.permissions)
        last_prop_name = KNORA_API.hasStillImageFileValue
    if last_prop_name:
        return serialise_property_graph(properties_graph, last_prop_name)
    return {}


def _make_one_prop_graph(prop: XMLProperty, restype: str, res_bnode: BNode, lookup: Lookups) -> tuple[Graph, URIRef]:
    prop_name = _get_absolute_prop_iri(prop.name, lookup.namespaces)
    match prop.valtype:
        case "boolean" | "color" | "decimal" | "geometry" | "geoname" | "integer" | "time" | "uri" as val_type:
            literal_info = rdf_prop_type_mapper[val_type]
            transformer = rdf_literal_transformer[val_type]
            properties_graph = _make_simple_prop_graph(
                prop=prop,
                res_bn=res_bnode,
                prop_name=prop_name,
                prop_type_info=literal_info,
                transformer=transformer,
                permissions_lookup=lookup.permissions,
            )
        case "list":
            properties_graph = _make_list_prop_graph(
                prop=prop,
                res_bn=res_bnode,
                prop_name=prop_name,
                permissions_lookup=lookup.permissions,
                listnode_lookup=lookup.listnodes,
            )
        case "resptr":
            prop_name = _get_link_prop_name(prop, restype, lookup.namespaces)
            properties_graph = _make_link_prop_graph(
                prop=prop,
                res_bn=res_bnode,
                prop_name=prop_name,
                permissions_lookup=lookup.permissions,
                iri_resolver=lookup.id_to_iri,
            )
        case "text":
            properties_graph = _make_text_prop_graph(
                prop=prop,
                res_bn=res_bnode,
                prop_name=prop_name,
                permissions_lookup=lookup.permissions,
                iri_resolver=lookup.id_to_iri,
            )
        case "date":
            properties_graph = _make_date_prop_graph(
                prop=prop,
                res_bn=res_bnode,
                prop_name=prop_name,
                permissions_lookup=lookup.permissions,
            )
        case "interval":
            properties_graph = _make_interval_prop_graph(
                prop=prop,
                res_bn=res_bnode,
                prop_name=prop_name,
                permissions_lookup=lookup.permissions,
            )
        case _:
            raise UserError(f"Unknown value type: {prop.valtype}")
    return properties_graph, prop_name


def _get_link_prop_name(p: XMLProperty, restype: str, namespaces: dict[str, Namespace]) -> URIRef:
    if p.name == "knora-api:isSegmentOf" and restype == "knora-api:VideoSegment":
        return KNORA_API.isVideoSegmentOfValue
    elif p.name == "knora-api:isSegmentOf" and restype == "knora-api:AudioSegment":
        return KNORA_API.isAudioSegmentOfValue
    prop = f"{p.name}Value"
    return _get_absolute_prop_iri(prop, namespaces)


def _get_absolute_prop_iri(prefixed_prop: str, namespaces: dict[str, Namespace]) -> URIRef:
    prefix, prop = prefixed_prop.split(":", maxsplit=1)
    if not (namespace := namespaces.get(prefix)):
        raise InputError(f"Could not find namespace for prefix: {prefix}")
    return namespace[prop]


def _make_iiif_uri_value(iiif_uri: IIIFUriInfo, res_bnode: BNode, permissions_lookup: dict[str, Permissions]) -> Graph:
    g = Graph()
    iiif_bn = BNode()
    g.add((res_bnode, KNORA_API.hasStillImageFileValue, iiif_bn))
    g.add((iiif_bn, RDF.type, KNORA_API.StillImageExternalFileValue))
    g.add((iiif_bn, KNORA_API.fileValueHasExternalUrl, Literal(iiif_uri.value)))
    g += _add_optional_permission_triple(iiif_uri, iiif_bn, permissions_lookup)
    return g


def _make_bitstream_file_value(bitstream_info: BitstreamInfo) -> dict[str, Any]:
    local_file = Path(bitstream_info.local_file)
    file_ending = local_file.suffix[1:]
    internal_filename = bitstream_info.internal_file_name
    permissions = str(bitstream_info.permissions) if bitstream_info.permissions else None
    match file_ending.lower():
        case "zip" | "tar" | "gz" | "z" | "tgz" | "gzip" | "7z":
            return SerialiseArchiveFileValue(internal_filename, permissions).serialise()
        case "mp3" | "wav":
            return SerialiseAudioFileValue(internal_filename, permissions).serialise()
        case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
            return SerialiseDocumentFileValue(internal_filename, permissions).serialise()
        case "mp4":
            return SerialiseMovingImageFileValue(internal_filename, permissions).serialise()
        # jpx is the extension of the files returned by dsp-ingest
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff" | "jpx":
            return SerialiseStillImageFileValue(internal_filename, permissions).serialise()
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "csv" | "json":
            return SerialiseTextFileValue(internal_filename, permissions).serialise()
        case _:
            raise BaseError(f"Unknown file ending '{file_ending}' for file '{local_file}'")


def _make_simple_prop_graph(
    prop: XMLProperty,
    res_bn: BNode,
    prop_name: URIRef,
    prop_type_info: RDFPropTypeInfo,
    transformer: Callable[[InputTypes], Literal],
    permissions_lookup: dict[str, Permissions],
) -> Graph:
    g = Graph()
    for val in prop.values:
        transformed_val = transformer(val.value)
        resolved_permission = resolve_permission(val.permissions, permissions_lookup)
        transformed = TransformedValue(
            value=transformed_val, prop_name=prop_name, permissions=resolved_permission, comment=val.comment
        )
        g += _make_simple_value_graph(transformed, res_bn, prop_type_info)
    return g


def _make_simple_value_graph(
    val: TransformedValue,
    res_bn: BNode,
    prop_type_info: RDFPropTypeInfo,
) -> Graph:
    val_bn = BNode()
    g = _add_optional_triples(val_bn, val.permissions, val.comment)
    g.add((res_bn, val.prop_name, val_bn))
    g.add((val_bn, RDF.type, prop_type_info.knora_type))
    g.add((val_bn, prop_type_info.knora_prop, val.value))
    return g


def _make_list_prop_graph(
    prop: XMLProperty,
    res_bn: BNode,
    prop_name: URIRef,
    permissions_lookup: dict[str, Permissions],
    listnode_lookup: dict[str, str],
) -> Graph:
    g = Graph()
    for val in prop.values:
        s = assert_is_string(val.value)
        if not (iri_str := listnode_lookup.get(s)):
            msg = (
                f"Could not resolve list node ID '{s}' to IRI. "
                f"This is probably because the list node '{s}' does not exist on the server."
            )
            raise BaseError(msg)

        resolved_permission = resolve_permission(val.permissions, permissions_lookup)
        transformed = TransformedValue(
            value=URIRef(iri_str),
            prop_name=prop_name,
            permissions=resolved_permission,
            comment=val.comment,
        )
        g += _make_simple_value_graph(transformed, res_bn, rdf_prop_type_mapper["list"])
    return g


def _make_date_prop_graph(
    prop: XMLProperty,
    res_bn: BNode,
    prop_name: URIRef,
    permissions_lookup: dict[str, Permissions],
) -> Graph:
    g = Graph()
    for val in prop.values:
        resolved_permission = resolve_permission(val.permissions, permissions_lookup)
        g += _make_date_value_graph(val, prop_name, resolved_permission, res_bn)
    return g


def _make_date_value_graph(
    val: XMLValue,
    prop_name: URIRef,
    resolved_permission: str | None,
    res_bn: BNode,
) -> Graph:
    date = transform_date(val.value)
    val_bn = BNode()
    g = _add_optional_triples(val_bn, resolved_permission, val.comment)
    g.add((res_bn, prop_name, val_bn))
    g.add((val_bn, RDF.type, KNORA_API.DateValue))
    if cal := date.calendar.value:
        g.add((val_bn, KNORA_API.dateValueHasCalendar, Literal(cal, datatype=XSD.string)))
    g += _make_single_date_graph(val_bn, date.start, StartEnd.START)
    if date.end:
        g += _make_single_date_graph(val_bn, date.end, StartEnd.END)
    return g


def _make_single_date_graph(val_bn: BNode, date: SingleDate, start_end: StartEnd) -> Graph:
    def get_prop(precision: DayMonthYearEra) -> URIRef:
        return KNORA_API[f"dateValueHas{start_end.value}{precision.value}"]

    g = Graph()
    if yr := date.year:
        g.add((val_bn, get_prop(DayMonthYearEra.YEAR), Literal(yr, datatype=XSD.integer)))
    if mnt := date.month:
        g.add((val_bn, get_prop(DayMonthYearEra.MONTH), Literal(mnt, datatype=XSD.integer)))
    if day := date.day:
        g.add((val_bn, get_prop(DayMonthYearEra.DAY), Literal(day, datatype=XSD.integer)))
    if era := date.era:
        g.add((val_bn, get_prop(DayMonthYearEra.ERA), Literal(era.value, datatype=XSD.string)))
    return g


def _make_interval_prop_graph(
    prop: XMLProperty,
    res_bn: BNode,
    prop_name: URIRef,
    permissions_lookup: dict[str, Permissions],
) -> Graph:
    g = Graph()
    for val in prop.values:
        resolved_permission = resolve_permission(val.permissions, permissions_lookup)
        g += _make_interval_value_graph(val, prop_name, resolved_permission, res_bn)
    return g


def _make_interval_value_graph(
    val: XMLValue,
    prop_name: URIRef,
    resolved_permission: str | None,
    res_bn: BNode,
) -> Graph:
    interval = transform_interval(val.value)
    val_bn = BNode()
    g = _add_optional_triples(val_bn, resolved_permission, val.comment)
    g.add((res_bn, prop_name, val_bn))
    g.add((val_bn, RDF.type, KNORA_API.IntervalValue))
    g.add((val_bn, KNORA_API.intervalValueHasStart, interval.start))
    g.add((val_bn, KNORA_API.intervalValueHasEnd, interval.end))
    return g


def _make_link_prop_graph(
    prop: XMLProperty,
    res_bn: BNode,
    prop_name: URIRef,
    permissions_lookup: dict[str, Permissions],
    iri_resolver: IriResolver,
) -> Graph:
    g = Graph()
    for val in prop.values:
        str_val = assert_is_string(val.value)
        iri_str = _resolve_id_to_iri(str_val, iri_resolver)
        resolved_permission = resolve_permission(val.permissions, permissions_lookup)
        transformed = TransformedValue(
            value=URIRef(iri_str),
            prop_name=prop_name,
            permissions=resolved_permission,
            comment=val.comment,
        )
        g += _make_simple_value_graph(transformed, res_bn, rdf_prop_type_mapper["link"])
    return g


def _resolve_id_to_iri(value: str, iri_resolver: IriResolver) -> str:
    if is_resource_iri(value):
        iri_str = value
    elif resolved_iri := iri_resolver.get(value):
        iri_str = resolved_iri
    else:
        msg = (
            f"Could not find the ID {value} in the id2iri mapping. "
            f"This is probably because the resource '{value}' could not be created. "
            f"See {WARNINGS_SAVEPATH} for more information."
        )
        raise BaseError(msg)
    return iri_str


def _make_text_prop_graph(
    prop: XMLProperty,
    res_bn: BNode,
    prop_name: URIRef,
    permissions_lookup: dict[str, Permissions],
    iri_resolver: IriResolver,
) -> Graph:
    g = Graph()
    for val in prop.values:
        resolved_permission = resolve_permission(val.permissions, permissions_lookup)
        match val.value:
            case str():
                transformed = TransformedValue(
                    value=Literal(val.value, datatype=XSD.string),
                    prop_name=prop_name,
                    permissions=resolved_permission,
                    comment=val.comment,
                )
                g += _make_simple_value_graph(
                    val=transformed, res_bn=res_bn, prop_type_info=rdf_prop_type_mapper["simpletext"]
                )
            case FormattedTextValue():
                g += _make_richtext_value_graph(
                    val=val,
                    prop_name=prop_name,
                    res_bn=res_bn,
                    permissions_lookup=permissions_lookup,
                    iri_resolver=iri_resolver,
                )
            case _:
                assert_never(val.value)
    return g


def _make_richtext_value_graph(
    val: XMLValue,
    prop_name: URIRef,
    res_bn: BNode,
    permissions_lookup: dict[str, Permissions],
    iri_resolver: IriResolver,
) -> Graph:
    val_bn = BNode()
    resolved_permission = resolve_permission(val.permissions, permissions_lookup)
    g = _add_optional_triples(val_bn, resolved_permission, val.comment)
    xml_val = cast(FormattedTextValue, val.value)
    val_str = _get_richtext_string(xml_val, iri_resolver)
    g.add((res_bn, prop_name, val_bn))
    g.add((val_bn, RDF.type, KNORA_API.TextValue))
    g.add((val_bn, KNORA_API.textValueAsXml, Literal(val_str, datatype=XSD.string)))
    g.add((val_bn, KNORA_API.textValueHasMapping, URIRef("http://rdfh.ch/standoff/mappings/StandardMapping")))
    return g


def _get_richtext_string(xml_val: FormattedTextValue, iri_resolver: IriResolver) -> str:
    xml_with_iris = xml_val.with_iris(iri_resolver)
    return xml_with_iris.as_xml()


def _add_optional_triples(val_bn: BNode, permissions: str | None, comment: str | None) -> Graph:
    g = Graph()
    if permissions:
        g.add((val_bn, KNORA_API.hasPermissions, Literal(permissions, datatype=XSD.string)))
    if comment:
        g.add((val_bn, KNORA_API.valueHasComment, Literal(comment, datatype=XSD.string)))
    return g


def _add_optional_permission_triple(
    value: XMLValue | IIIFUriInfo, val_bn: BNode, permissions_lookup: dict[str, Permissions]
) -> Graph:
    g = Graph()
    if per_str := resolve_permission(value.permissions, permissions_lookup):
        g.add((val_bn, KNORA_API.hasPermissions, Literal(per_str, datatype=XSD.string)))
    return g
