import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Callable
from typing import assert_never
from typing import cast

from loguru import logger
from rdflib import RDF
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.namespace_context import get_json_ld_context_for_project
from dsp_tools.commands.xmlupload.models.namespace_context import make_namespace_dict_from_onto_names
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.serialise.jsonld_serialiser import serialise_property_graph
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseArchiveFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseAudioFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseDocumentFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseMovingImageFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseStillImageFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_file_value import SerialiseTextFileValue
from dsp_tools.commands.xmlupload.models.serialise.serialise_rdf_value import BooleanValueRDF
from dsp_tools.commands.xmlupload.models.serialise.serialise_rdf_value import IntValueRDF
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseColor
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseDate
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseDecimal
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseGeometry
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseGeoname
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseProperty
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseRichtext
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseSimpletext
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseTime
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseURI
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseValue
from dsp_tools.commands.xmlupload.models.value_transformers import DecimalTransformer
from dsp_tools.commands.xmlupload.models.value_transformers import ValueTransformer
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import PermissionNotExistsError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.date_util import parse_date_string
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.logger_config import WARNINGS_SAVEPATH

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


@dataclass(frozen=True)
class ResourceCreateClient:
    """client class that creates resources on a DSP server."""

    con: Connection
    project_iri: str
    iri_resolver: IriResolver
    project_onto_dict: dict[str, str]
    permissions_lookup: dict[str, Permissions]
    listnode_lookup: dict[str, str]
    media_previously_ingested: bool = False

    def create_resource(
        self,
        resource: XMLResource,
        bitstream_information: BitstreamInfo | None,
    ) -> str:
        """Creates a resource on the DSP server, and returns its IRI"""
        logger.info(
            f"Attempting to create resource {resource.res_id} (label: {resource.label}, iri: {resource.iri})..."
        )
        resource_dict = self._make_resource_with_values(resource, bitstream_information)
        headers = {"X-Asset-Ingested": "true"} if bitstream_information else None
        res = self.con.post(route="/v2/resources", data=resource_dict, headers=headers)
        return cast(str, res["@id"])

    def _make_resource_with_values(
        self,
        resource: XMLResource,
        bitstream_information: BitstreamInfo | None,
    ) -> dict[str, Any]:
        res_bnode = BNode()
        namespaces = make_namespace_dict_from_onto_names(self.project_onto_dict)
        res = self._make_resource(
            resource=resource,
            bitstream_information=bitstream_information,
        )
        vals = self._make_values(resource, res_bnode, namespaces)
        res.update(vals)
        return res

    def _make_resource(
        self,
        resource: XMLResource,
        bitstream_information: BitstreamInfo | None,
    ) -> dict[str, Any]:
        resource_iri = resource.iri
        if resource.ark:
            resource_iri = convert_ark_v0_to_resource_iri(resource.ark)
        context = get_json_ld_context_for_project(self.project_onto_dict)
        res = {
            "@type": resource.restype,
            "rdfs:label": resource.label,
            "knora-api:attachedToProject": {"@id": self.project_iri},
            "@context": context,
        }
        if resource_iri:
            res["@id"] = resource_iri
        if resource.permissions:
            if perm := self.permissions_lookup.get(resource.permissions):
                res["knora-api:hasPermissions"] = str(perm)
            else:
                raise PermissionNotExistsError(
                    f"Could not find permissions for resource {resource.res_id} with permissions {resource.permissions}"
                )
        if resource.creation_date:
            res["knora-api:creationDate"] = {
                "@type": "xsd:dateTimeStamp",
                "@value": str(resource.creation_date),
            }
        if bitstream_information:
            res.update(_make_bitstream_file_value(bitstream_information))
        return res

    def _make_values(self, resource: XMLResource, res_bnode: BNode, namespaces: dict[str, Namespace]) -> dict[str, Any]:
        def prop_name(p: XMLProperty) -> str:
            if p.valtype != "resptr":
                return p.name
            elif p.name == "knora-api:isSegmentOf" and resource.restype == "knora-api:VideoSegment":
                return "knora-api:isVideoSegmentOfValue"
            elif p.name == "knora-api:isSegmentOf" and resource.restype == "knora-api:AudioSegment":
                return "knora-api:isAudioSegmentOfValue"
            else:
                return f"{p.name}Value"

        def make_values(p: XMLProperty) -> list[dict[str, Any]]:
            return [self._make_value(v, p.valtype) for v in p.values]

        properties_serialised = {}
        properties_graph = Graph()
        # To frame the json-ld correctly, we need one property used in the graph. It does not matter which.
        last_prop_name = None

        str_value_to_serialiser_mapper = {
            "color": SerialiseColor,
            "geoname": SerialiseGeoname,
            "time": SerialiseTime,
            "uri": SerialiseURI,
        }

        value_with_transformer_mapper = {
            "decimal": (SerialiseDecimal, DecimalTransformer()),
        }

        for prop in resource.properties:
            match prop.valtype:
                # serialised as dict
                case "uri" | "color" | "geoname" | "time" as val_type:
                    transformed_prop = _transform_into_serialise_prop(
                        prop=prop,
                        permissions_lookup=self.permissions_lookup,
                        serialiser=str_value_to_serialiser_mapper[val_type],
                    )
                    properties_serialised.update(transformed_prop.serialise())
                case "decimal" as val_type:
                    serialiser, transformer = value_with_transformer_mapper[val_type]
                    transformed_prop = _transform_into_serialise_prop_with_transformer(
                        prop=prop,
                        permissions_lookup=self.permissions_lookup,
                        serialiser=serialiser,
                        transformer=transformer,
                    )
                    properties_serialised.update(transformed_prop.serialise())
                case "geometry":
                    transformed_prop = _transform_into_geometry_prop(
                        prop=prop, permissions_lookup=self.permissions_lookup
                    )
                    properties_serialised.update(transformed_prop.serialise())
                case "text":
                    transformed_prop = _transform_text_prop(
                        prop=prop,
                        permissions_lookup=self.permissions_lookup,
                        iri_resolver=self.iri_resolver,
                    )
                    properties_serialised.update(transformed_prop.serialise())
                case "date":
                    transformed_prop = _transform_into_date_prop(
                        prop=prop,
                        permissions_lookup=self.permissions_lookup,
                    )
                    properties_serialised.update(transformed_prop.serialise())
                # serialised with rdflib
                case "integer":
                    int_prop_name = self._get_absolute_prop_iri(prop.name, namespaces)
                    int_graph = _make_integer_prop(prop, res_bnode, int_prop_name, self.permissions_lookup)
                    properties_graph += int_graph
                    last_prop_name = int_prop_name
                case "boolean":
                    bool_prop_name = self._get_absolute_prop_iri(prop.name, namespaces)
                    bool_graph = _make_boolean_prop(prop, res_bnode, bool_prop_name, self.permissions_lookup)
                    properties_graph += bool_graph
                    last_prop_name = bool_prop_name
                # serialised as dict
                case _:
                    properties_serialised[prop_name(prop)] = make_values(prop)
        if resource.iiif_uri:
            properties_graph += _make_iiif_uri_value(resource.iiif_uri, res_bnode, self.permissions_lookup)
            last_prop_name = KNORA_API.hasStillImageFileValue
        if last_prop_name:
            serialised_graph_props = serialise_property_graph(properties_graph, last_prop_name)
            properties_serialised.update(serialised_graph_props)
        return properties_serialised

    def _get_absolute_prop_iri(self, prefixed_prop: str, namespaces: dict[str, Namespace]) -> URIRef:
        prefix, prop = prefixed_prop.split(":", maxsplit=1)
        if not (namespace := namespaces.get(prefix)):
            raise InputError(f"Could not find namespace for prefix: {prefix}")
        return namespace[prop]

    def _make_value(self, value: XMLValue, value_type: str) -> dict[str, Any]:
        match value_type:
            case "interval":
                res = _make_interval_value(value)
            case "resptr":
                res = _make_link_value(value, self.iri_resolver)
            case "list":
                res = _make_list_value(value, self.listnode_lookup)
            case _:
                raise UserError(f"Unknown value type: {value_type}")
        if value.comment:
            res["knora-api:valueHasComment"] = value.comment
        if value.permissions:
            if perm := self.permissions_lookup.get(value.permissions):
                res["knora-api:hasPermissions"] = str(perm)
            else:
                raise PermissionNotExistsError(f"Could not find permissions for value: {value.permissions}")
        return res


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


def _to_boolean(s: str | int | bool) -> bool:
    match s:
        case "True" | "true" | "1" | 1 | True:
            return True
        case "False" | "false" | "0" | 0 | False:
            return False
        case _:
            raise BaseError(f"Could not parse boolean value: {s}")


def _transform_into_date_prop(prop: XMLProperty, permissions_lookup: dict[str, Permissions]) -> SerialiseProperty:
    vals = [_transform_into_date_value(v, permissions_lookup) for v in prop.values]
    return SerialiseProperty(property_name=prop.name, values=vals)


def _transform_into_date_value(value: XMLValue, permissions_lookup: dict[str, Permissions]) -> SerialiseDate:
    string_value = _assert_is_string(value.value)
    date = parse_date_string(string_value)
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    return SerialiseDate(value=date, permissions=permission_str, comment=value.comment)


def _transform_into_decimal_prop(prop: XMLProperty, permissions_lookup: dict[str, Permissions]) -> SerialiseProperty:
    vals = [_transform_into_decimal_value(v, permissions_lookup) for v in prop.values]
    return SerialiseProperty(property_name=prop.name, values=vals)


def _transform_into_decimal_value(value: XMLValue, permissions_lookup: dict[str, Permissions]) -> SerialiseDecimal:
    s = _assert_is_string(value.value)
    val = str(float(s))
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    return SerialiseDecimal(value=val, permissions=permission_str, comment=value.comment)


def _transform_into_geometry_prop(prop: XMLProperty, permissions_lookup: dict[str, Permissions]) -> SerialiseProperty:
    vals = [_transform_into_geometry_value(v, permissions_lookup) for v in prop.values]
    return SerialiseProperty(property_name=prop.name, values=vals)


def _transform_into_geometry_value(value: XMLValue, permissions_lookup: dict[str, Permissions]) -> SerialiseGeometry:
    s = _assert_is_string(value.value)
    # this removes all whitespaces from the embedded json string
    encoded_value = json.dumps(json.loads(s))
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    return SerialiseGeometry(value=encoded_value, permissions=permission_str, comment=value.comment)


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
    s = _assert_is_string(value.value)
    as_bool = _to_boolean(s)
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
    s = _assert_is_string(value.value)
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


def _make_interval_value(value: XMLValue) -> dict[str, Any]:
    s = _assert_is_string(value.value)
    match s.split(":", 1):
        case [start, end]:
            return {
                "@type": "knora-api:IntervalValue",
                "knora-api:intervalValueHasStart": {
                    "@type": "xsd:decimal",
                    "@value": str(float(start)),
                },
                "knora-api:intervalValueHasEnd": {
                    "@type": "xsd:decimal",
                    "@value": str(float(end)),
                },
            }
        case _:
            raise BaseError(f"Could not parse interval value: {s}")


def _make_link_value(value: XMLValue, iri_resolver: IriResolver) -> dict[str, Any]:
    s = _assert_is_string(value.value)
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
    return {
        "@type": "knora-api:LinkValue",
        "knora-api:linkValueHasTargetIri": {
            "@id": iri,
        },
    }


def _make_list_value(value: XMLValue, iri_lookup: dict[str, str]) -> dict[str, Any]:
    s = _assert_is_string(value.value)
    if iri := iri_lookup.get(s):
        return {
            "@type": "knora-api:ListValue",
            "knora-api:listValueAsListNode": {
                "@id": iri,
            },
        }
    else:
        msg = (
            f"Could not resolve list node ID '{s}' to IRI. "
            f"This is probably because the list node '{s}' does not exist on the server."
        )
        raise BaseError(msg)


def _transform_text_prop(
    prop: XMLProperty, permissions_lookup: dict[str, Permissions], iri_resolver: IriResolver
) -> SerialiseProperty:
    values = []
    for val in prop.values:
        match val.value:
            case str():
                values.append(_transform_into_serialise_value(val, permissions_lookup, SerialiseSimpletext))
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


def _transform_into_serialise_prop_with_transformer(
    prop: XMLProperty,
    permissions_lookup: dict[str, Permissions],
    serialiser: Callable[[str, str | None, str | None], SerialiseValue],
    transformer: ValueTransformer,
) -> SerialiseProperty:
    serialised_values = [
        _transform_into_serialise_value_with_transformer(v, permissions_lookup, serialiser, transformer)
        for v in prop.values
    ]
    prop_serialise = SerialiseProperty(
        property_name=prop.name,
        values=serialised_values,
    )
    return prop_serialise


def _transform_into_serialise_value_with_transformer(
    value: XMLValue,
    permissions_lookup: dict[str, Permissions],
    serialiser: Callable[[str, str | None, str | None], SerialiseValue],
    transformer: ValueTransformer,
) -> SerialiseValue:
    transformed = transformer.transform(value.value)
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    return serialiser(transformed, permission_str, value.comment)


def _transform_into_serialise_prop(
    prop: XMLProperty,
    permissions_lookup: dict[str, Permissions],
    serialiser: Callable[[str, str | None, str | None], SerialiseValue],
) -> SerialiseProperty:
    serialised_values = [_transform_into_serialise_value(v, permissions_lookup, serialiser) for v in prop.values]
    prop_serialise = SerialiseProperty(
        property_name=prop.name,
        values=serialised_values,
    )
    return prop_serialise


def _transform_into_serialise_value(
    value: XMLValue,
    permissions_lookup: dict[str, Permissions],
    serialiser: Callable[[str, str | None, str | None], SerialiseValue],
) -> SerialiseValue:
    permission_str = _get_permission_str(value.permissions, permissions_lookup)
    value_str = cast(str, value.value)
    return serialiser(value_str, permission_str, value.comment)


def _get_permission_str(value_permissions: str | None, permissions_lookup: dict[str, Permissions]) -> str | None:
    if value_permissions:
        if not (per := permissions_lookup.get(value_permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {value_permissions}")
        return str(per)
    return None


def _assert_is_string(value: str | FormattedTextValue) -> str:
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise BaseError(f"Expected string value, but got XML value: {xml.as_xml()}")
        case _:
            assert_never(value)
