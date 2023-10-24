import json
from dataclasses import dataclass
from typing import Any, assert_never

from dsp_tools.connection.connection import Connection
from dsp_tools.models.sipi import Sipi
from dsp_tools.xml_upload.domain.model.resource import InputResource
from dsp_tools.xml_upload.domain.model.value import (
    BooleanValue,
    ColorValue,
    DateValue,
    DecimalValue,
    FormattedTextValue,
    GeometryValue,
    GeonamesValue,
    IntegerValue,
    IntervalValue,
    LinkValue,
    ListValue,
    TimeValue,
    UnformattedTextValue,
    UriValue,
    Value,
)


@dataclass(frozen=True)
class DspUploadRepoLive:
    """Live implementation of the DSP upload repository protocol, interacting with an instance of DSP-API."""

    connection: Connection
    sipi: Sipi

    def create_resource(self, resource: InputResource) -> None:
        """Creates an instance of a resource in DSP-API."""
        json_ld = _resource_to_json_ld(resource)
        print(json.dumps(json_ld, indent=2))
        quit()


def _resource_to_json_ld(res: InputResource) -> dict[str, Any]:
    context = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }
    json_ld: dict[str, Any] = {
        "@type": res.resource_type,
        "rdfs:label": res.label,
    }
    if res.bitstream_path:
        json_ld["bitstream"] = res.bitstream_path  # XXX: should actually be different, I suppose?
    if res.permissions:
        json_ld["knora-api:hasPermissions"] = res.permissions
    if res.iri:
        json_ld["@id"] = res.iri
    if res.ark:
        json_ld["ark"] = res.ark
    if res.creation_date:
        json_ld["creation_date"] = res.creation_date

    for val in res.values:
        json_ld.update(_value_to_json_ld(val))

    json_ld["@context"] = context

    return json_ld


def _value_to_json_ld(v: Value) -> dict[str, dict[str, Any]]:
    json_ld: dict[str, Any] = {"@type": "knora-api:TextValue"}
    json_ld.update(_serialize_value(v))
    if v.permissions:
        json_ld["knora-api:hasPermissions"] = v.permissions
    return {v.property_name: json_ld}


def _serialize_value(v: Value) -> dict[str, Any]:
    match v:
        case BooleanValue(_, value, _):
            return {"knora-api:booleanValueAsBoolean": value}
        case ColorValue(_, value, _):
            return {"knora-api:colorValueAsColor": value}
        case DateValue(_, value, _):
            return {"knora-api:dateValueAsDate": value}
        case DecimalValue(_, value, _):
            return {"knora-api:decimalValueAsDecimal": value}
        case GeometryValue(_, value, _):
            return {"knora-api:geometryValueAsGeometry": value}
        case GeonamesValue(_, value, _):
            return {"knora-api:geonameValueAsUri": value}
        case IntegerValue(_, value, _):
            return {"knora-api:integerValueAsInt": value}
        case IntervalValue(_, value, _):
            return {"knora-api:intervalValueAsInterval": value}
        case ListValue(_, value, _):
            return {"knora-api:listValueAsListNode": value}
        case LinkValue(_, value, _):
            return {"knora-api:linkValueAsUri": value}
        case UnformattedTextValue(_, value, _) | FormattedTextValue(_, value, _):
            return {"knora-api:textValueAsString": value}
        case TimeValue(_, value, _):
            return {"knora-api:timeValueAsTime": value}
        case UriValue(_, value, _):
            return {"knora-api:uriValueAsUri": value}
        case _:
            assert_never(v)
