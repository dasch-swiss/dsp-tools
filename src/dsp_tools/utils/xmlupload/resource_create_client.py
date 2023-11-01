import json
from dataclasses import dataclass
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
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action
from dsp_tools.utils.xmlupload.ark2iri import convert_ark_v0_to_resource_iri

logger = get_logger(__name__)


@dataclass(frozen=True)
class ResourceCreateClient:
    """client class that creates resources on a DSP server."""

    con: Connection
    project_iri: str
    json_ld_context: dict[str, str]
    id2iri_mapping: dict[str, str]
    permissions_lookup: dict[str, Permissions]

    def create_resource(
        self,
        resource: XMLResource,
        bitstream_information: BitstreamInfo | None,
    ) -> tuple[str, str]:
        """Creates a resource on the DSP server."""
        logger.info(f"Attempting to create resource {resource.id} (label: {resource.label}, iri: {resource.iri})...")
        resource_json_ld = self._make_json_ld_resource(resource, bitstream_information)
        res = try_network_action(self.con.post, route="/v2/resources", jsondata=resource_json_ld)
        iri = res["@id"]
        label = res["rdfs:label"]
        return iri, label

    def _make_json_ld_resource(
        self,
        resource: XMLResource,
        bitstream_information: BitstreamInfo | None,
    ) -> str:
        return json.dumps(self._make_resource_with_values(resource, bitstream_information), ensure_ascii=False)

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
            res["knora-api:hasPermissions"] = str(self.permissions_lookup[resource.permissions])
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
            if p.valtype == "resptr":
                return p.name + "Value"
            return p.name

        return {
            prop_name(prop): self._make_value_for_property(prop)
            for prop in resource.properties
            if prop.valtype != "list"
        }

    def _make_value_for_property(self, prop: XMLProperty) -> list[dict[str, Any]]:
        return [self._make_value(v, prop.valtype) for v in prop.values]

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
                res = _make_link_value(value, self.id2iri_mapping)
            case "list":
                res = _make_list_value(value)
            case "text":
                res = _make_text_value(value, self.id2iri_mapping)
            case "time":
                res = _make_time_value(value)
            case "uri":
                res = _make_uri_value(value)
            case _:
                raise UserError(f"Unknown value type: {value_type}")
        if value.comment:
            res["knora-api:valueHasComment"] = value.comment
        if value.permissions:
            res["knora-api:hasPermissions"] = str(self.permissions_lookup[value.permissions])
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
            raise UserError(f"Unknown file ending: {file_ending} for file {local_file}")
    file_value = {
        "@type": f"knora-api:{value_type}",
        "knora-api:fileValueHasFilename": bitstream_info.internal_file_name,
    }
    if bitstream_info.permissions:
        file_value["knora-api:hasPermissions"] = str(bitstream_info.permissions)
    return {prop: file_value}


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
            # start_era cannot be None, and this provides a useful type hint
            pass
        case ("ISLAMIC", era, _, end_era, _) if era or end_era:
            raise UserError(f"ISLAMIC calendar does not support eras: {value.value}")
        case _:
            raise UserError(f"Could not parse date: {value.value}")
    res: dict[str, Any] = {"@type": "knora-api:DateValue"}
    calendar, start_era, start_date, end_era, end_date = date_groups
    if not calendar:
        calendar = "GREGORIAN"
    if not end_date:
        end_date = start_date
    if calendar != "ISLAMIC":
        if not start_era:
            start_era = "CE"
        if end_date and not end_era:
            end_era = "CE"

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
    assert isinstance(value.value, str)
    encoded_value = json.dumps(json.loads(value.value))
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


def _make_link_value(value: XMLValue, id_to_iri_mapping: dict[str, str]) -> dict[str, Any]:
    assert isinstance(value.value, str)
    iri = id_to_iri_mapping.get(value.value)
    if not iri:
        print(f"WARNING: could not find IRI for resource ID {value.value}")
        raise AssertionError(f"WARNING: could not find IRI for resource ID {value.value}")
    return {
        "@type": "knora-api:LinkValue",
        "knora-api:linkValueHasTargetIri": {
            "@id": iri,
        },
    }


def _make_list_value(value: XMLValue) -> dict[str, Any]:
    res = {
        "@type": "knora-api:ListValue",
        "knora-api:listValueAsListNode": {
            # "@id": value.value,
            "@id": "http://rdfh.ch/lists/0001/treeList",
        },  # XXX: make sure to get the actual list node IRI here
    }
    print(f"attempting to create list value: {res}")
    return res


def _make_text_value(value: XMLValue, id2iri_mapping: dict[str, str]) -> dict[str, Any]:
    match value.value:
        case str() as s:
            return {
                "@type": "knora-api:TextValue",
                "knora-api:valueAsString": s,
            }
        case KnoraStandoffXml() as xml:
            ids = set(regex.findall(pattern='href="IRI:(.*?):IRI"', string=str(xml)))
            xml_str = f'<?xml version="1.0" encoding="UTF-8"?>\n<text>{str(xml)}</text>'
            for internal_id in ids:
                iri = id2iri_mapping[internal_id]
                xml_str = xml_str.replace(f'href="IRI:{internal_id}:IRI"', f'href="{iri}"')
            return {
                "@type": "knora-api:TextValue",
                "knora-api:textValueAsXml": f'<?xml version="1.0" encoding="UTF-8"?>\n<text>{str(xml)}</text>',
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
