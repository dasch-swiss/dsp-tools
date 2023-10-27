import json
import sys
from pathlib import Path
from typing import Any, assert_never

from dsp_tools.connection.connection import Connection
from dsp_tools.models.exceptions import UserError
from dsp_tools.models.permission import Permissions
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlresource import BitstreamInfo, XMLResource
from dsp_tools.models.xmlvalue import XMLValue
from dsp_tools.utils.xmlupload.ark2iri import convert_ark_v0_to_resource_iri


def actually_crearte_resource(
    resource: XMLResource,
    bitstream_information: BitstreamInfo | None,
    con: Connection,
    permissions_lookup: dict[str, Permissions],
    id2iri_mapping: dict[str, str],
    json_ld_context: dict[str, str],
    project_iri: str,
) -> tuple[str, str]:
    print("-" * 120)
    res = _make_resource(
        resource=resource,
        bitstream_information=bitstream_information,
        permission_lookup=permissions_lookup,
        json_ld_context=json_ld_context,
        project_iri=project_iri,
    )
    vals = _make_values(resource, id2iri_mapping, permissions_lookup)
    res.update(vals)
    print(json.dumps(res, indent=2))
    print("-" * 120)
    # TODO: upload resource
    # sys.exit(0)
    return "TODO", "TODO"


def _make_resource(
    resource: XMLResource,
    bitstream_information: BitstreamInfo | None,
    permission_lookup: dict[str, Permissions],
    json_ld_context: dict[str, str],
    project_iri: str,
) -> dict[str, Any]:
    resource_iri = resource.iri
    if resource.ark:
        resource_iri = convert_ark_v0_to_resource_iri(resource.ark)
    res = {
        "@type": resource.restype,
        "rdfs:label": resource.label,
        "knora-api:attachedToProject": {"@id": project_iri},
        "@context": json_ld_context,
    }
    if resource_iri:
        res["@id"] = resource_iri
    if resource.permissions:
        res["knora-api:hasPermissions"] = str(permission_lookup[resource.permissions])
    if resource.creation_date:
        res["knora-api:creationDate"] = {
            "@type": "xsd:dateTimeStamp",
            "@value": resource.creation_date,
        }
    if bitstream_information:
        res.update(_make_bitstream_file_value(bitstream_information))
    return res


def _make_bitstream_file_value(bitstream_info: BitstreamInfo) -> dict[str, Any]:
    local_file = Path(bitstream_info.local_file)
    file_ending = "".join(local_file.suffixes)[1:]
    file_name = local_file.name
    match file_ending:
        case "zip" | "tar" | "gz" | "z" | "tar.gz" | "tgz" | "gzip" | "7z":
            file_value = {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:internalFileName": bitstream_info.internal_file_name,
                "knora-api:originalFilename": file_name,
            }
            if bitstream_info.permissions:
                file_value["knora-api:hasPermissions"] = str(bitstream_info.permissions)
            return {"knora-api:hasArchiveFileValue": file_value}
        case "mp3" | "wav":
            file_value = {
                "@type": "knora-api:AudioFileValue",
                "knora-api:internalFileName": bitstream_info.internal_file_name,
                "knora-api:originalFilename": file_name,
            }
            if bitstream_info.permissions:
                file_value["knora-api:hasPermissions"] = str(bitstream_info.permissions)
            return {"knora-api:hasAudioFileValue": file_value}
        case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
            file_value = {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:internalFileName": bitstream_info.internal_file_name,
                "knora-api:originalFilename": file_name,
            }
            if bitstream_info.permissions:
                file_value["knora-api:hasPermissions"] = str(bitstream_info.permissions)
            return {"knora-api:hasDocumentFileValue": file_value}
        case "mp4":
            file_value = {
                "@type": "knora-api:MovingImageFileValue",
                "knora-api:internalFileName": bitstream_info.internal_file_name,
                "knora-api:originalFilename": file_name,
            }
            if bitstream_info.permissions:
                file_value["knora-api:hasPermissions"] = str(bitstream_info.permissions)
            return {"knora-api:hasMovingImageFileValue": file_value}
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff":
            file_value = {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:internalFileName": bitstream_info.internal_file_name,
                "knora-api:originalFilename": file_name,
            }
            if bitstream_info.permissions:
                file_value["knora-api:hasPermissions"] = str(bitstream_info.permissions)
            return {"knora-api:hasStillImageFileValue": file_value}
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "xslt" | "csv":
            file_value = {
                "@type": "knora-api:TextFileValue",
                "knora-api:internalFileName": bitstream_info.internal_file_name,
                "knora-api:originalFilename": file_name,
            }
            if bitstream_info.permissions:
                file_value["knora-api:hasPermissions"] = str(bitstream_info.permissions)
            return {"knora-api:hasTextFileValue": file_value}
        case _:
            raise UserError(f"Unknown file ending: {file_ending} for file {local_file}")


def _make_values(
    resource: XMLResource,
    id2iri_mapping: dict[str, str],
    permissions_lookup: dict[str, Permissions],
) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for prop in resource.properties:
        values[prop.name] = [_make_value(v, prop.valtype) for v in prop.values]
    return values


def _make_value(value: XMLValue, value_type: str) -> dict[str, Any]:
    match value_type:
        case "text":
            return _make_text_value(value)
        case _:
            print(f"!!! No idea how to handle this value type: {value_type} !!!")
            sys.exit(-1)


def _make_text_value(value: XMLValue) -> dict[str, Any]:
    match value.value:
        case str() as s:
            return {
                "@type": "knora-api:TextValue",
                "knora-api:valueAsString": s,
            }
        case KnoraStandoffXml() as xml:
            return {
                "@type": "knora-api:TextValue",
                "knora-api:valueAsXml": str(xml),
                "knora-api:textValueHasMapping": {
                    "@id": "http://rdfh.ch/standoff/mappings/StandardMapping",
                },
            }
        case _:
            assert_never(value.value)
