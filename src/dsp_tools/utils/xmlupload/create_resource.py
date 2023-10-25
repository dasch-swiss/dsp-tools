import json
import sys
from typing import Any

from dsp_tools.connection.connection import Connection
from dsp_tools.models.permission import Permissions
from dsp_tools.models.xmlresource import BitstreamInfo, XMLResource
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
    print(resource)
    res = _make_resource(
        resource=resource,
        bitstream_information=bitstream_information,
        permission_lookup=permissions_lookup,
        json_ld_context=json_ld_context,
        project_iri=project_iri,
    )
    print(json.dumps(res, indent=2))
    # TODO:
    # - turn bitstream into something useful with the bitstream info object
    # - add bitstream to json-ld object
    print("-" * 120)
    sys.exit(0)


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
    # TODO: add bitstream
    return res


def _make_bitstream_file_value(bitstream_info: BitstreamInfo) -> dict[str, Any]:
    file_ending = bitstream_info.local_file.rsplit(".", 1)[-1]
    match file_ending:
        case "jpg" | "jpeg" | "png" | "tif" | "tiff":
            return {
                "knora-api:hasStillImageFileValue": {
                    "@type": "knora-api:StillImageFileValue",
                    "knora-api:fileValueAsUrl": bitstream_info.internal_file_name,
                }
            }
        case _:
            print(f"!!! No idea how to handle this file type: .{file_ending} !!!")
            print(f"({bitstream_info.local_file} - {bitstream_info.internal_file_name})")
            sys.exit(-1)
