from pathlib import Path
from typing import Any
from typing import assert_never
from typing import cast

from rdflib import RDF
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_file_value_graph import make_iiif_uri_value_graph
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import AbstractFileValue
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import FileValueMetadata
from dsp_tools.commands.xmlupload.models.serialise.jsonld_serialiser import serialise_property_graph
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseArchiveFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseAudioFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseDocumentFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseMovingImageFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseStillImageFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseTextFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_rdf_value import BooleanValueRDF
from dsp_tools.commands.xmlupload.models.serialise.serialise_rdf_value import IntValueRDF
from dsp_tools.commands.xmlupload.models.serialise.serialise_resource import SerialiseMigrationMetadata
from dsp_tools.commands.xmlupload.models.serialise.serialise_resource import SerialiseResource
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseLink
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseList
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseProperty
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseRichtext
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseSimpletext
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import ValueSerialiser
from dsp_tools.commands.xmlupload.value_transformers import TransformationSteps
from dsp_tools.commands.xmlupload.value_transformers import assert_is_string
from dsp_tools.commands.xmlupload.value_transformers import transform_boolean
from dsp_tools.commands.xmlupload.value_transformers import transform_string
from dsp_tools.commands.xmlupload.value_transformers import value_to_transformations_mapper
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import PermissionNotExistsError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.logger_config import WARNINGS_SAVEPATH

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


def create_resource_with_values(
    resource: XMLResource, bitstream_information: BitstreamInfo | None, lookup: Lookups
) -> dict[str, Any]:
    """
    This function takes an XMLResource and serialises it into a json-ld type dict that can be sent to the API.

    Args:
        resource: XMLResource
        bitstream_information: if the resource has a FileValue
        lookup: Lookups to resolve IRIs, etc.

    Returns:
        A resource serialised in json-ld type format.
    """
    res_bnode = BNode()
    res = _make_resource(resource=resource, bitstream_information=bitstream_information, lookup=lookup)
    vals = _make_values(resource, res_bnode, lookup)
    res.update(vals)
    res.update(lookup.jsonld_context.serialise())
    return res


def _make_resource(
    resource: XMLResource, bitstream_information: BitstreamInfo | None, lookup: Lookups
) -> dict[str, Any]:
    migration_metadata = None
    res_iri = resource.iri
    creation_date = resource.creation_date
    if resource.ark:
        res_iri = convert_ark_v0_to_resource_iri(resource.ark)
    if any([creation_date, res_iri]):
        migration_metadata = SerialiseMigrationMetadata(iri=res_iri, creation_date=resource.creation_date)
    permission_str = _get_permission_str(resource.permissions, lookup.permissions)
    serialise_resource = SerialiseResource(
        res_id=resource.res_id,
        res_type=resource.restype,
        label=resource.label,
        permissions=permission_str,
        project_iri=lookup.project_iri,
        migration_metadata=migration_metadata,
    )
    res = serialise_resource.serialise()
    if bitstream_information:
        res.update(_make_bitstream_file_value(bitstream_information))
    return res


def _make_values(resource: XMLResource, res_bnode: BNode, lookup: Lookups) -> dict[str, Any]:
    def get_link_prop_name(p: XMLProperty) -> str:
        if p.name == "knora-api:isSegmentOf" and resource.restype == "knora-api:VideoSegment":
            return "knora-api:isVideoSegmentOfValue"
        elif p.name == "knora-api:isSegmentOf" and resource.restype == "knora-api:AudioSegment":
            return "knora-api:isAudioSegmentOfValue"
        else:
            return f"{p.name}Value"

    properties_serialised = {}
    properties_graph = Graph()
    # To frame the json-ld correctly, we need one property used in the graph. It does not matter which.
    last_prop_name = None

    for prop in resource.properties:
        match prop.valtype:
            # serialised as dict
            case "uri" | "color" | "geoname" | "time" | "decimal" | "geometry" | "date" | "interval" as val_type:
                transformations = value_to_transformations_mapper[val_type]
                transformed_prop = _transform_into_prop_serialiser(
                    prop=prop,
                    permissions_lookup=lookup.permissions,
                    transformations=transformations,
                )
                properties_serialised.update(transformed_prop.serialise())
            case "text":
                transformed_prop = _transform_text_prop(
                    prop=prop,
                    permissions_lookup=lookup.permissions,
                    iri_resolver=lookup.id_to_iri,
                )
                properties_serialised.update(transformed_prop.serialise())
            case "resptr":
                prop_name = get_link_prop_name(prop)
                transformed_prop = _transform_into_link_prop(
                    prop=prop,
                    prop_name=prop_name,
                    permissions_lookup=lookup.permissions,
                    iri_resolver=lookup.id_to_iri,
                )
                properties_serialised.update(transformed_prop.serialise())
            case "list":
                transformed_prop = _transform_into_list_prop(
                    prop=prop,
                    permissions_lookup=lookup.permissions,
                    listnode_lookup=lookup.listnodes,
                )
                properties_serialised.update(transformed_prop.serialise())
            # serialised with rdflib
            case "integer":
                int_prop_name = _get_absolute_prop_iri(prop.name, lookup.namespaces)
                int_graph = _make_integer_prop(prop, res_bnode, int_prop_name, lookup.permissions)
                properties_graph += int_graph
                last_prop_name = int_prop_name
            case "boolean":
                bool_prop_name = _get_absolute_prop_iri(prop.name, lookup.namespaces)
                bool_graph = _make_boolean_prop(prop, res_bnode, bool_prop_name, lookup.permissions)
                properties_graph += bool_graph
                last_prop_name = bool_prop_name
            case _:
                raise UserError(f"Unknown value type: {prop.valtype}")
    if resource.iiif_uri:
        resolved_permissions = _get_permission_str(resource.iiif_uri.permissions, lookup.permissions)
        metadata = FileValueMetadata(resolved_permissions)
        iiif_val = AbstractFileValue(resource.iiif_uri.value, metadata)
        properties_graph += make_iiif_uri_value_graph(iiif_val, res_bnode)
        last_prop_name = KNORA_API.hasStillImageFileValue
    if last_prop_name:
        serialised_graph_props = serialise_property_graph(properties_graph, last_prop_name)
        properties_serialised.update(serialised_graph_props)
    return properties_serialised


def _get_absolute_prop_iri(prefixed_prop: str, namepsaces: dict[str, Namespace]) -> URIRef:
    prefix, prop = prefixed_prop.split(":", maxsplit=1)
    if not (namespace := namepsaces.get(prefix)):
        raise InputError(f"Could not find namespace for prefix: {prefix}")
    return namespace[prop]


def _transform_into_prop_serialiser(
    prop: XMLProperty,
    permissions_lookup: dict[str, Permissions],
    transformations: TransformationSteps,
) -> SerialiseProperty:
    serialised_values = [_transform_into_value_serialiser(v, permissions_lookup, transformations) for v in prop.values]
    prop_serialise = SerialiseProperty(
        property_name=prop.name,
        values=serialised_values,
    )
    return prop_serialise


def _transform_into_value_serialiser(
    value: XMLValue,
    permissions_lookup: dict[str, Permissions],
    transformations: TransformationSteps,
) -> SerialiseValue:
    transformed = transformations.transformer(value.value)
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    return transformations.serialiser(transformed, permission_str, value.comment)


def _add_optional_permission_triple(
    value: XMLValue | IIIFUriInfo, val_bn: BNode, g: Graph, permissions_lookup: dict[str, Permissions]
) -> None:
    if value.permissions:
        if not (per := permissions_lookup.get(value.permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {value.permissions}")
        g.add((val_bn, KNORA_API.hasPermissions, Literal(str(per))))


def _make_iiif_uri_value(iiif_uri: IIIFUriInfo, res_bnode: BNode, permissions_lookup: dict[str, Permissions]) -> Graph:
    g = Graph()
    iiif_bn = BNode()
    g.add((res_bnode, KNORA_API.hasStillImageFileValue, iiif_bn))
    g.add((iiif_bn, RDF.type, KNORA_API.StillImageExternalFileValue))
    g.add((iiif_bn, KNORA_API.fileValueHasExternalUrl, Literal(iiif_uri.value)))
    _add_optional_permission_triple(iiif_uri, iiif_bn, g, permissions_lookup)
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
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "csv":
            return SerialiseTextFileValue(internal_filename, permissions).serialise()
        case _:
            raise BaseError(f"Unknown file ending '{file_ending}' for file '{local_file}'")


def _make_boolean_prop(
    prop: XMLProperty, res_bn: BNode, prop_name: URIRef, permissions_lookup: dict[str, Permissions]
) -> Graph:
    g = Graph()
    for value in prop.values:
        boolean_value = _make_boolean_value(value, prop_name, res_bn, permissions_lookup)
        g += boolean_value.as_graph()
    return g


def _make_boolean_value(
    value: XMLValue, prop_name: URIRef, res_bn: BNode, permissions_lookup: dict[str, Permissions]
) -> BooleanValueRDF:
    s = assert_is_string(value.value)
    as_bool = transform_boolean(s)
    permission_literal = None
    if permission_str := _get_permission_str(value.permissions, permissions_lookup):
        permission_literal = Literal(permission_str)
    return BooleanValueRDF(
        resource_bn=res_bn,
        prop_name=prop_name,
        value=Literal(as_bool),
        permissions=permission_literal,
        comment=Literal(value.comment) if value.comment else None,
    )


def _make_integer_prop(
    prop: XMLProperty, res_bn: BNode, prop_name: URIRef, permissions_lookup: dict[str, Permissions]
) -> Graph:
    g = Graph()
    for value in prop.values:
        int_value = _make_integer_value(value, prop_name, res_bn, permissions_lookup)
        g += int_value.as_graph()
    return g


def _make_integer_value(
    value: XMLValue, prop_name: URIRef, res_bn: BNode, permissions_lookup: dict[str, Permissions]
) -> IntValueRDF:
    s = assert_is_string(value.value)
    permission_literal = None
    if permission_str := _get_permission_str(value.permissions, permissions_lookup):
        permission_literal = Literal(permission_str)
    return IntValueRDF(
        resource_bn=res_bn,
        prop_name=prop_name,
        value=Literal(int(s)),
        permissions=permission_literal,
        comment=Literal(value.comment) if value.comment else None,
    )


def _transform_into_link_prop(
    prop: XMLProperty,
    prop_name: str,
    permissions_lookup: dict[str, Permissions],
    iri_resolver: IriResolver,
) -> SerialiseProperty:
    vals = [_transform_into_link_value(v, permissions_lookup, SerialiseLink, iri_resolver) for v in prop.values]
    return SerialiseProperty(property_name=prop_name, values=vals)


def _transform_into_link_value(
    value: XMLValue,
    permissions_lookup: dict[str, Permissions],
    serialiser: ValueSerialiser,
    iri_resolver: IriResolver,
) -> SerialiseValue:
    s = assert_is_string(value.value)
    if is_resource_iri(s):
        iri = s
    elif resolved_iri := iri_resolver.get(s):
        iri = resolved_iri
    else:
        msg = (
            f"Could not find the ID {s} in the id2iri mapping. "
            f"This is probably because the resource '{s}' could not be created. "
            f"See {WARNINGS_SAVEPATH} for more information."
        )
        raise BaseError(msg)
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    return serialiser(iri, permission_str, value.comment)


def _transform_into_list_prop(
    prop: XMLProperty, permissions_lookup: dict[str, Permissions], listnode_lookup: dict[str, str]
) -> SerialiseProperty:
    vals = [_transform_into_list_value(v, permissions_lookup, listnode_lookup) for v in prop.values]
    return SerialiseProperty(property_name=prop.name, values=vals)


def _transform_into_list_value(
    value: XMLValue, permissions_lookup: dict[str, Permissions], listnode_lookup: dict[str, str]
) -> SerialiseValue:
    s = assert_is_string(value.value)
    if not (iri := listnode_lookup.get(s)):
        msg = (
            f"Could not resolve list node ID '{s}' to IRI. "
            f"This is probably because the list node '{s}' does not exist on the server."
        )
        raise BaseError(msg)
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    return SerialiseList(iri, permission_str, value.comment)


def _transform_text_prop(
    prop: XMLProperty, permissions_lookup: dict[str, Permissions], iri_resolver: IriResolver
) -> SerialiseProperty:
    values = []
    for val in prop.values:
        match val.value:
            case str():
                values.append(
                    _transform_into_value_serialiser(
                        value=val,
                        permissions_lookup=permissions_lookup,
                        transformations=TransformationSteps(SerialiseSimpletext, transform_string),
                    )
                )
            case FormattedTextValue():
                values.append(_transform_into_richtext_value(val, permissions_lookup, iri_resolver))
            case _:
                assert_never(val.value)
    return SerialiseProperty(property_name=prop.name, values=values)


def _transform_into_richtext_value(
    val: XMLValue, permissions_lookup: dict[str, Permissions], iri_resolver: IriResolver
) -> SerialiseRichtext:
    xml_val = cast(FormattedTextValue, val.value)
    xml_with_iris = xml_val.with_iris(iri_resolver)
    val_str = xml_with_iris.as_xml()
    permission_str = _get_permission_str(val.permissions, permissions_lookup)
    return SerialiseRichtext(value=val_str, permissions=permission_str, comment=val.comment)


def _transform_into_serialise_prop(
    prop: XMLProperty,
    permissions_lookup: dict[str, Permissions],
    transformer: TransformationSteps,
) -> SerialiseProperty:
    serialised_values = [_transform_into_serialise_value(v, permissions_lookup, transformer) for v in prop.values]
    prop_serialise = SerialiseProperty(
        property_name=prop.name,
        values=serialised_values,
    )
    return prop_serialise


def _transform_into_serialise_value(
    value: XMLValue,
    permissions_lookup: dict[str, Permissions],
    transformer: TransformationSteps,
) -> SerialiseValue:
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    value_str = cast(str, value.value)
    return transformer.serialiser(value_str, permission_str, value.comment)


def _get_permission_str(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> str | None:
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return str(per)
    return None
