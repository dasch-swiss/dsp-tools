from __future__ import annotations

from rdflib import XSD

from dsp_tools.commands.xmlupload.models.processed.values import ProcessedBoolean
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedColor
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedDecimal
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeometry
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeoname
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedInt
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedTime
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedUri
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType

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
    ProcessedBoolean: BOOLEAN_PROP_TYPE_INFO,
    ProcessedColor: COLOR_PROP_TYPE_INFO,
    ProcessedDecimal: DECIMAL_PROP_TYPE_INFO,
    ProcessedGeometry: GEOMETRY_PROP_TYPE_INFO,
    ProcessedGeoname: GEONAME_PROP_TYPE_INFO,
    ProcessedInt: INT_PROP_TYPE_INFO,
    ProcessedSimpleText: SIMPLE_TEXT_PROP_TYPE_INFO,
    ProcessedTime: TIME_PROP_TYPE_INFO,
    ProcessedUri: URI_PROP_TYPE_INFO,
}

# file values
ARCHIVE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.ArchiveFileValue, KNORA_API.hasArchiveFileValue, XSD.string)
AUDIO_FILE_VALUE = RDFPropTypeInfo(KNORA_API.AudioFileValue, KNORA_API.hasAudioFileValue, XSD.string)
DOCUMENT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.DocumentFileValue, KNORA_API.hasDocumentFileValue, XSD.string)
MOVING_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.MovingImageFileValue, KNORA_API.hasMovingImageFileValue, XSD.string)
STILL_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.StillImageFileValue, KNORA_API.hasStillImageFileValue, XSD.string)
TEXT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.TextFileValue, KNORA_API.hasTextFileValue, XSD.string)
IIIF_URI_VALUE = RDFPropTypeInfo(KNORA_API.StillImageExternalFileValue, KNORA_API.hasStillImageFileValue, XSD.anyURI)


FILE_TYPE_TO_RDF_MAPPER = {
    KnoraValueType.ARCHIVE_FILE: ARCHIVE_FILE_VALUE,
    KnoraValueType.AUDIO_FILE: AUDIO_FILE_VALUE,
    KnoraValueType.DOCUMENT_FILE: DOCUMENT_FILE_VALUE,
    KnoraValueType.MOVING_IMAGE_FILE: MOVING_IMAGE_FILE_VALUE,
    KnoraValueType.STILL_IMAGE_FILE: STILL_IMAGE_FILE_VALUE,
    KnoraValueType.TEXT_FILE: TEXT_FILE_VALUE,
}
