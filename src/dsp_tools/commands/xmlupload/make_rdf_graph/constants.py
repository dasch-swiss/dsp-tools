from __future__ import annotations

from rdflib import Namespace

from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_geometry
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_any_uri
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_boolean
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_date_time
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_decimal
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_integer
from dsp_tools.commands.xmlupload.make_rdf_graph.value_transformers import transform_xsd_string
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")

RDF_LITERAL_TRANSFORMER_MAPPER = {
    "boolean": transform_xsd_boolean,
    "color": transform_xsd_string,
    "decimal": transform_xsd_decimal,
    "geometry": transform_geometry,
    "geoname": transform_xsd_string,
    "integer": transform_xsd_integer,
    "time": transform_xsd_date_time,
    "uri": transform_xsd_any_uri,
}


RDF_PROP_TYPE_MAPPER = {
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


ARCHIVE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.ArchiveFileValue, KNORA_API.hasArchiveFileValue)
AUDIO_FILE_VALUE = RDFPropTypeInfo(KNORA_API.AudioFileValue, KNORA_API.hasAudioFileValue)
DOCUMENT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.DocumentFileValue, KNORA_API.hasDocumentFileValue)
MOVING_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.MovingImageFileValue, KNORA_API.hasMovingImageFileValue)
STILL_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.StillImageFileValue, KNORA_API.hasStillImageFileValue)
TEXT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.TextFileValue, KNORA_API.hasTextFileValue)
IIIF_URI_VALUE = RDFPropTypeInfo(KNORA_API.StillImageExternalFileValue, KNORA_API.hasStillImageFileValue)
