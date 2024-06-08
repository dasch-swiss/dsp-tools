import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
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
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseProperty
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseURI
from dsp_tools.commands.xmlupload.models.serialise.serialise_value import SerialiseValue
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import PermissionNotExistsError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.date_util import parse_date_string
from dsp_tools.utils.iri_util import is_resource_iri

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
        res = self.con.post(route="/v2/resources", data=resource_dict, headers={"X-Asset-Ingested": "true"})
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

        for prop in resource.properties:
            match prop.valtype:
                case "uri":
                    properties_serialised.update(_serialise_uri_prop(prop, self.permissions_lookup))
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
                case _:
                    properties_serialised.update({prop_name(prop): make_values(prop)})
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

    def _make_value(self, value: XMLValue, value_type: str) -> dict[str, Any]:  # noqa: PLR0912 (too many branches)
        match value_type:
            case "color":
                res = _make_color_value(value)
            case "date":
                res = _make_date_value(value)
            case "decimal":
                res = _make_decimal_value(value)
            case "geometry":
                res = _make_geometry_value(value)
            case "geoname":
                res = _make_geoname_value(value)
            case "interval":
                res = _make_interval_value(value)
            case "resptr":
                res = _make_link_value(value, self.iri_resolver)
            case "list":
                res = _make_list_value(value, self.listnode_lookup)
            case "text":
                res = _make_text_value(value, self.iri_resolver)
            case "time":
                res = _make_time_value(value)
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
    match file_ending.lower():
        case "zip" | "tar" | "gz" | "z" | "tgz" | "gzip" | "7z":
            prop = "knora-api:hasArchiveFileValue"
            value_type = "ArchiveFileValue"
        case "mp3" | "wav":
            prop = "knora-api:hasAudioFileValue"
            value_type = "AudioFileValue"
        case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
            prop = "knora-api:hasDocumentFileValue"
            value_type = "DocumentFileValue"
        case "mp4":
            prop = "knora-api:hasMovingImageFileValue"
            value_type = "MovingImageFileValue"
        # jpx is the extension of the files returned by dsp-ingest
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff" | "jpx":
            prop = "knora-api:hasStillImageFileValue"
            value_type = "StillImageFileValue"
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "xslt" | "csv":
            prop = "knora-api:hasTextFileValue"
            value_type = "TextFileValue"
        case _:
            raise BaseError(f"Unknown file ending '{file_ending}' for file '{local_file}'")
    file_value = {
        "@type": f"knora-api:{value_type}",
        "knora-api:fileValueHasFilename": bitstream_info.internal_file_name,
    }
    if bitstream_info.permissions:
        file_value["knora-api:hasPermissions"] = str(bitstream_info.permissions)
    return {prop: file_value}


def _to_boolean(s: str | int | bool) -> bool:
    match s:
        case "True" | "true" | "1" | 1 | True:
            return True
        case "False" | "false" | "0" | 0 | False:
            return False
        case _:
            raise BaseError(f"Could not parse boolean value: {s}")


def _make_color_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:ColorValue",
        "knora-api:colorValueAsColor": value.value,
    }


def _make_date_value(value: XMLValue) -> dict[str, Any]:
    string_value = _assert_is_string(value.value)
    date = parse_date_string(string_value)
    res: dict[str, Any] = {
        "@type": "knora-api:DateValue",
        "knora-api:dateValueHasStartYear": date.start.year,
    }
    if month := date.start.month:
        res["knora-api:dateValueHasStartMonth"] = month
    if day := date.start.day:
        res["knora-api:dateValueHasStartDay"] = day
    if era := date.start.era:
        res["knora-api:dateValueHasStartEra"] = era.value
    if calendar := date.calendar:
        res["knora-api:dateValueHasCalendar"] = calendar.value
    if date.end:
        res["knora-api:dateValueHasEndYear"] = date.end.year
        if month := date.end.month:
            res["knora-api:dateValueHasEndMonth"] = month
        if day := date.end.day:
            res["knora-api:dateValueHasEndDay"] = day
        if era := date.end.era:
            res["knora-api:dateValueHasEndEra"] = era.value
    return res


def _make_decimal_value(value: XMLValue) -> dict[str, Any]:
    s = _assert_is_string(value.value)
    return {
        "@type": "knora-api:DecimalValue",
        "knora-api:decimalValueAsDecimal": {
            "@type": "xsd:decimal",
            "@value": str(float(s)),
        },
    }


def _make_geometry_value(value: XMLValue) -> dict[str, Any]:
    s = _assert_is_string(value.value)
    # this removes all whitespaces from the embedded json string
    encoded_value = json.dumps(json.loads(s))
    return {
        "@type": "knora-api:GeomValue",
        "knora-api:geometryValueAsGeometry": encoded_value,
    }


def _make_geoname_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:GeonameValue",
        "knora-api:geonameValueAsGeonameCode": value.value,
    }


def _make_boolean_prop(
    prop: XMLProperty, res_bn: BNode, prop_name: URIRef, permissions_lookup: dict[str, Permissions]
) -> Graph:
    g = Graph()
    for value in prop.values:
        single_val_bn = BNode()
        g.add((res_bn, prop_name, single_val_bn))
        g += _make_boolean_value(value, single_val_bn, permissions_lookup)
    return g


def _make_boolean_value(value: XMLValue, val_bn: BNode, permissions_lookup: dict[str, Permissions]) -> Graph:
    s = _assert_is_string(value.value)
    g = Graph()
    g.add((val_bn, RDF.type, KNORA_API.BooleanValue))
    g.add((val_bn, KNORA_API.booleanValueAsBoolean, Literal(_to_boolean(s))))
    _add_optional_permission_triple(value, val_bn, g, permissions_lookup)
    if value.comment:
        g.add((val_bn, KNORA_API.valueHasComment, Literal(value.comment)))
    return g


def _make_integer_prop(
    prop: XMLProperty, res_bn: BNode, prop_name: URIRef, permissions_lookup: dict[str, Permissions]
) -> Graph:
    g = Graph()
    for value in prop.values:
        single_val_bn = BNode()
        g.add((res_bn, prop_name, single_val_bn))
        g += _make_integer_value(value, single_val_bn, permissions_lookup)
    return g


def _make_integer_value(value: XMLValue, val_bn: BNode, permissions_lookup: dict[str, Permissions]) -> Graph:
    s = _assert_is_string(value.value)
    g = Graph()
    g.add((val_bn, RDF.type, KNORA_API.IntValue))
    g.add((val_bn, KNORA_API.intValueAsInt, Literal(int(s))))
    _add_optional_permission_triple(value, val_bn, g, permissions_lookup)
    if value.comment:
        g.add((val_bn, KNORA_API.valueHasComment, Literal(value.comment)))
    return g


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
        raise BaseError(f"Could not resolve ID {s} to IRI.")
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
        raise BaseError(f"Could not resolve list node ID {s} to IRI.")


def _make_text_value(value: XMLValue, iri_resolver: IriResolver) -> dict[str, Any]:
    match value.value:
        case str() as s:
            return {
                "@type": "knora-api:TextValue",
                "knora-api:valueAsString": s,
            }
        case FormattedTextValue() as xml:
            xml_with_iris = xml.with_iris(iri_resolver)
            return {
                "@type": "knora-api:TextValue",
                "knora-api:textValueAsXml": xml_with_iris.as_xml(),
                "knora-api:textValueHasMapping": {
                    "@id": "http://rdfh.ch/standoff/mappings/StandardMapping",
                },
            }
        case _:
            assert_never(value.value)


def _make_time_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:TimeValue",
        "knora-api:timeValueAsTimeStamp": {
            "@type": "xsd:dateTimeStamp",
            "@value": value.value,
        },
    }


def _serialise_uri_prop(prop: XMLProperty, permissions_lookup: dict[str, Permissions]) -> dict[str, Any]:
    uri_values: list[SerialiseValue] = []
    for v in prop.values:
        if v.permissions:
            if not (per := permissions_lookup.get(v.permissions)):
                raise PermissionNotExistsError(f"Could not find permissions for value: {v.permissions}")
            permission = str(per)
        else:
            permission = None
        uri = cast(str, v.value)
        uri_values.append(
            SerialiseURI(
                value=uri,
                permissions=permission,
                comment=v.comment,
            )
        )
    prop_serialise = SerialiseProperty(
        property_name=prop.name,
        values=uri_values,
    )
    return prop_serialise.serialise()


def _assert_is_string(value: str | FormattedTextValue) -> str:
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise BaseError(f"Expected string value, but got XML value: {xml.as_xml()}")
        case _:
            assert_never(value)
