from __future__ import annotations

from rdflib import XSD
from rdflib import Namespace

from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryColor
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDecimal
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeometry
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeoname
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInt
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryTime
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryUri
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")

# values that need special considerations during the graph construction
LIST_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.ListValue, KNORA_API.listValueAsListNode)
LINK_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.LinkValue, KNORA_API.linkValueHasTargetIri)
RICHTEXT_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.TextValue, KNORA_API.textValueAsXml, XSD.string)

# values suitable for the generic lookup
BOOLEAN_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.BooleanValue, KNORA_API.booleanValueAsBoolean, XSD.boolean)
COLOR_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.ColorValue, KNORA_API.colorValueAsColor, XSD.string)
DECIMAL_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.DecimalValue, KNORA_API.decimalValueAsDecimal, XSD.decimal)
GEOMETRY_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.GeomValue, KNORA_API.geometryValueAsGeometry, XSD.string)
GEONAME_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.GeonameValue, KNORA_API.geonameValueAsGeonameCode, XSD.string)
INT_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.IntValue, KNORA_API.intValueAsInt, XSD.integer)
SIMPLE_TEXT_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.TextValue, KNORA_API.valueAsString, XSD.string)
TIME_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.TimeValue, KNORA_API.timeValueAsTimeStamp, XSD.dateTimeStamp)
URI_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.UriValue, KNORA_API.uriValueAsUri, XSD.anyURI)

RDF_LITERAL_PROP_TYPE_MAPPER = {
    IntermediaryBoolean: BOOLEAN_PROP_TYPE_INFO,
    IntermediaryColor: COLOR_PROP_TYPE_INFO,
    IntermediaryDecimal: DECIMAL_PROP_TYPE_INFO,
    IntermediaryGeometry: GEOMETRY_PROP_TYPE_INFO,
    IntermediaryGeoname: GEONAME_PROP_TYPE_INFO,
    IntermediaryInt: INT_PROP_TYPE_INFO,
    IntermediarySimpleText: SIMPLE_TEXT_PROP_TYPE_INFO,
    IntermediaryTime: TIME_PROP_TYPE_INFO,
    IntermediaryUri: URI_PROP_TYPE_INFO,
}

# file values
ARCHIVE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.ArchiveFileValue, KNORA_API.hasArchiveFileValue, XSD.string)
AUDIO_FILE_VALUE = RDFPropTypeInfo(KNORA_API.AudioFileValue, KNORA_API.hasAudioFileValue, XSD.string)
DOCUMENT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.DocumentFileValue, KNORA_API.hasDocumentFileValue, XSD.string)
MOVING_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.MovingImageFileValue, KNORA_API.hasMovingImageFileValue, XSD.string)
STILL_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.StillImageFileValue, KNORA_API.hasStillImageFileValue, XSD.string)
TEXT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.TextFileValue, KNORA_API.hasTextFileValue, XSD.string)
IIIF_URI_VALUE = RDFPropTypeInfo(KNORA_API.StillImageExternalFileValue, KNORA_API.hasStillImageFileValue, XSD.anyURI)
