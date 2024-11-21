from __future__ import annotations

from rdflib import Namespace

from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


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
