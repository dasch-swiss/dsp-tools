import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, assert_never

from dsp_tools.commands.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.xmlproperty import XMLProperty
from dsp_tools.commands.xmlupload.models.xmlresource import BitstreamInfo, XMLResource
from dsp_tools.commands.xmlupload.models.xmlvalue import XMLValue
from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.date_util import parse_date_string
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


@dataclass(frozen=True)
class ResourceCreateClient:
    """client class that creates resources on a DSP server."""

    con: Connection
    project_iri: str
    id_to_iri_resolver: IriResolver
    json_ld_context: dict[str, str]
    permissions_lookup: dict[str, Permissions]
    listnode_lookup: dict[str, str]

    def create_resource(
        self,
        resource: XMLResource,
        bitstream_information: BitstreamInfo | None,
    ) -> tuple[str, str]:
        """Creates a resource on the DSP server."""
        logger.info(f"Attempting to create resource {resource.id} (label: {resource.label}, iri: {resource.iri})...")
        resource_dict = self._make_resource_with_values(resource, bitstream_information)
        resource_json_ld = json.dumps(resource_dict, ensure_ascii=False)
        res = try_network_action(self.con.post, route="/v2/resources", jsondata=resource_json_ld)
        iri = res["@id"]
        label = res["rdfs:label"]
        return iri, label

    def _make_resource_with_values(
        self,
        resource: XMLResource,
        bitstream_information: BitstreamInfo | None,
    ) -> dict[str, Any]:
        res = self._make_resource(
            resource=resource,
            bitstream_information=bitstream_information,
        )
        vals = self._make_values(resource)
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
        res = {
            "@type": resource.restype,
            "rdfs:label": resource.label,
            "knora-api:attachedToProject": {"@id": self.project_iri},
            "@context": self.json_ld_context,
        }
        if resource_iri:
            res["@id"] = resource_iri
        if resource.permissions:
            if perm := self.permissions_lookup.get(resource.permissions):
                res["knora-api:hasPermissions"] = str(perm)
            else:
                raise BaseError(
                    f"Could not find permissions for resource {resource.id} with permissions {resource.permissions}"
                )
        if resource.creation_date:
            res["knora-api:creationDate"] = {
                "@type": "xsd:dateTimeStamp",
                "@value": str(resource.creation_date),
            }
        if bitstream_information:
            res.update(_make_bitstream_file_value(bitstream_information))
        return res

    def _make_values(self, resource: XMLResource) -> dict[str, Any]:
        def prop_name(p: XMLProperty) -> str:
            return f"{p.name}Value" if p.valtype == "resptr" else p.name

        def make_values(p: XMLProperty) -> list[dict[str, Any]]:
            return [self._make_value(v, p.valtype) for v in p.values]

        return {prop_name(prop): make_values(prop) for prop in resource.properties}

    def _make_value(self, value: XMLValue, value_type: str) -> dict[str, Any]:
        match value_type:
            case "boolean":
                res = _make_boolean_value(value)
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
            case "integer":
                res = _make_integer_value(value)
            case "interval":
                res = _make_interval_value(value)
            case "resptr":
                res = _make_link_value(value, self.id_to_iri_resolver)
            case "list":
                res = _make_list_value(value, self.listnode_lookup)
            case "text":
                res = _make_text_value(value, self.id_to_iri_resolver)
            case "time":
                res = _make_time_value(value)
            case "uri":
                res = _make_uri_value(value)
            case _:
                raise UserError(f"Unknown value type: {value_type}")
        if value.comment:
            res["knora-api:valueHasComment"] = value.comment
        if value.permissions:
            if perm := self.permissions_lookup.get(value.permissions):
                res["knora-api:hasPermissions"] = str(perm)
            else:
                raise BaseError(f"Could not find permissions for value: {value.permissions}")
        return res


def _make_bitstream_file_value(bitstream_info: BitstreamInfo) -> dict[str, Any]:
    local_file = Path(bitstream_info.local_file)
    file_ending = "".join(local_file.suffixes)[1:]
    match file_ending:
        case "zip" | "tar" | "gz" | "z" | "tar.gz" | "tgz" | "gzip" | "7z":
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
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff":
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


def _make_boolean_value(value: XMLValue) -> dict[str, Any]:
    string_value = _assert_is_string(value.value)
    boolean = _to_boolean(string_value)
    return {
        "@type": "knora-api:BooleanValue",
        "knora-api:booleanValueAsBoolean": boolean,
    }


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


def _make_integer_value(value: XMLValue) -> dict[str, Any]:
    s = _assert_is_string(value.value)
    return {
        "@type": "knora-api:IntValue",
        "knora-api:intValueAsInt": int(s),
    }


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


def _make_uri_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:UriValue",
        "knora-api:uriValueAsUri": {
            "@type": "xsd:anyURI",
            "@value": value.value,
        },
    }


def _assert_is_string(value: str | FormattedTextValue) -> str:
    match value:
        case str() as s:
            return s
        case FormattedTextValue() as xml:
            raise BaseError(f"Expected string value, but got XML value: {xml.as_xml()}")
        case _:
            assert_never(value)
