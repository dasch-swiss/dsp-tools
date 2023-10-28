import json
import sys
from pathlib import Path
from typing import Any, assert_never

import regex

from dsp_tools.connection.connection import Connection
from dsp_tools.models.exceptions import UserError
from dsp_tools.models.permission import Permissions
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
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
    res = _make_resource(
        resource=resource,
        bitstream_information=bitstream_information,
        permission_lookup=permissions_lookup,
        json_ld_context=json_ld_context,
        project_iri=project_iri,
    )
    vals = _make_values(resource, id2iri_mapping, permissions_lookup)
    res.update(vals)
    # TODO: upload resource
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
            "@value": str(resource.creation_date),
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
    return {prop.name: _make_value_for_property(prop, permissions_lookup) for prop in resource.properties}


def _make_value_for_property(
    prop: XMLProperty,
    permissions_lookup: dict[str, Permissions],
) -> list[dict[str, Any]]:
    return [_make_value(v, prop.valtype, permissions_lookup) for v in prop.values]


def _make_value(
    value: XMLValue,
    value_type: str,
    permissions_lookup: dict[str, Permissions],
) -> dict[str, Any]:
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
            res = _make_link_value(value)
        case "list":
            res = _make_list_value(value)
        case "text":
            res = _make_text_value(value)
        case "time":
            res = _make_time_value(value)
        case "uri":
            res = _make_uri_value(value)
        case _:
            raise UserError(f"Unknown value type: {value_type}")
    if value.comment:
        res["knora-api:valueHasComment"] = value.comment
    if value.permissions:
        res["knora-api:hasPermissions"] = str(permissions_lookup[value.permissions])
    return res


def _make_boolean_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:BooleanValue",
        "knora-api:booleanValueAsBoolean": bool(value.value),
    }


def _make_color_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:ColorValue",
        "knora-api:colorValueAsColor": value.value,
    }


def _make_date_value(value: XMLValue) -> dict[str, Any]:
    entire_pattern = r"""
    ^
    (?:(GREGORIAN|JULIAN|ISLAMIC):)?        # optional calendar
    (?:(CE|BCE|BC|AD):)?                    # optional era
    (\d{4}(?:-\d{1,2})?(?:-\d{1,2})?)       # date
    (?::(CE|BCE|BC|AD))?                    # optional era
    (?::(\d{4}(?:-\d{1,2})?(?:-\d{1,2})?))? # optional date
    $
"""
    assert isinstance(value.value, str)
    date_match = regex.search(entire_pattern, value.value, flags=regex.VERBOSE)
    assert date_match
    date_groups = date_match.groups()
    match date_groups:
        case (str() | None, str() | None, str(), str() | None, str() | None):
            pass
        case ("ISLAMIC", era, _, end_era, _) if era or end_era:
            raise UserError(f"ISLAMIC calendar does not support eras: {value.value}")
        case _:
            raise UserError(f"Could not parse date: {value.value}")

    res: dict[str, Any] = {"@type": "knora-api:DateValue"}
    calendar, start_era, start_date, end_era, end_date = date_groups

    year, month, day = _parse_date(start_date)
    res["knora-api:dateValueHasStartYear"] = int(year)
    if month:
        res["knora-api:dateValueHasStartMonth"] = int(month)
    if day:
        res["knora-api:dateValueHasStartDay"] = int(day)
    if end_era:
        res["knora-api:dateValueHasEndEra"] = end_era

    if calendar:
        res["knora-api:dateValueHasCalendar"] = calendar
    if start_era:
        res["knora-api:dateValueHasStartEra"] = start_era
    if end_date:
        year, month, day = _parse_date(end_date)
        res["knora-api:dateValueHasEndYear"] = int(year)
        if month:
            res["knora-api:dateValueHasEndMonth"] = int(month)
        if day:
            res["knora-api:dateValueHasEndDay"] = int(day)
    return res


def _parse_date(date: str) -> tuple[str, str | None, str | None]:
    date_pattern = r"(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?"
    date_match = regex.search(date_pattern, date)
    assert date_match
    match date_match.groups():
        case (year, month, day):
            assert year
            return year, month, day
    raise UserError(f"Could not parse date: {date}")


def _make_decimal_value(value: XMLValue) -> dict[str, Any]:
    assert isinstance(value.value, str)
    return {
        "@type": "knora-api:DecimalValue",
        "knora-api:decimalValueAsDecimal": {
            "@type": "xsd:decimal",
            "@value": str(float(value.value)),
        },
    }


def _make_geometry_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:GeometryValue",
        "knora-api:geometryValueHasGeometry": value.value,
    }


def _make_geoname_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:GeonameValue",
        "knora-api:geonameValueAsGeonameCode": value.value,
    }


def _make_integer_value(value: XMLValue) -> dict[str, Any]:
    assert isinstance(value.value, str)
    return {
        "@type": "knora-api:IntValue",
        "knora-api:intValueAsInt": int(value.value),
    }


def _make_interval_value(value: XMLValue) -> dict[str, Any]:
    match value.value:
        case str() as s:
            start, end = tuple(s.split(":", 1))
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
            raise UserError(f"Unexpected interval value: {value.value}")


def _make_link_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:LinkValue",
        "knora-api:linkValueHasTarget": {
            "@id": value.value,
        },
    }


def _make_list_value(value: XMLValue) -> dict[str, Any]:
    res = {
        "@type": "knora-api:ListValue",
        "knora-api:listValueAsListNode": {
            "@id": value.value,
        },  # XXX: make sure to get the actual list node IRI here
    }
    print(f"attempting to create list value: {res}")
    return res


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


def _make_time_value(value: XMLValue) -> dict[str, Any]:
    res = {
        "@type": "knora-api:TimeValue",
        "knora-api:timeValueAsTime": value.value,  # XXX: check if this is correct! probably not
    }
    print(f"attempting to create time value: {res}")
    return res


def _make_uri_value(value: XMLValue) -> dict[str, Any]:
    return {
        "@type": "knora-api:UriValue",
        "knora-api:uriValueAsUri": {
            "@type": "xsd:anyURI",
            "@value": value.value,
        },
    }
