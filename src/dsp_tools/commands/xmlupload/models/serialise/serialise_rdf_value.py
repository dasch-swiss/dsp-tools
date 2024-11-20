from __future__ import annotations

from dataclasses import dataclass

from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


@dataclass
class TransformedValue:
    value: Literal | URIRef
    prop_name: URIRef
    permissions: str | None
    comment: str | None


@dataclass
class RDFPropTypeInfo:
    knora_type: URIRef
    knora_prop: URIRef


@dataclass
class Interval:
    start: Literal
    end: Literal


rdf_prop_type_mapper = {
    "boolean": RDFPropTypeInfo(KNORA_API.BooleanValue, KNORA_API.booleanValueAsBoolean),
    "color": RDFPropTypeInfo(KNORA_API.ColorValue, KNORA_API.colorValueAsColor),
    "decimal": RDFPropTypeInfo(KNORA_API.DecimalValue, KNORA_API.decimalValueAsDecimal),
    "geometry": RDFPropTypeInfo(KNORA_API.GeomValue, KNORA_API.geometryValueAsGeometry),
    "geoname": RDFPropTypeInfo(KNORA_API.GeonameValue, KNORA_API.geonameValueAsGeonameCode),
    "integer": RDFPropTypeInfo(KNORA_API.IntValue, KNORA_API.intValueAsInt),
    "link": RDFPropTypeInfo(KNORA_API.LinkValue, KNORA_API.linkValueHasTargetIri),
    "list": RDFPropTypeInfo(KNORA_API.ListValue, KNORA_API.listValueAsListNode),
    "simpletext": RDFPropTypeInfo(KNORA_API.TextValue, KNORA_API.valueAsString),
    "time": RDFPropTypeInfo(KNORA_API.TimeValue, KNORA_API.timeValueAsTimeStamp),
    "uri": RDFPropTypeInfo(KNORA_API.UriValue, KNORA_API.uriValueAsUri),
}
