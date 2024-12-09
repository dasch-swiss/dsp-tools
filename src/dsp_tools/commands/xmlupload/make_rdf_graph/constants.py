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

LIST_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.ListValue, KNORA_API.listValueAsListNode)
LINK_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.LinkValue, KNORA_API.linkValueHasTargetIri)
RICHTEXT_PROP_TYPE_INFO = RDFPropTypeInfo(KNORA_API.TextValue, KNORA_API.textValueAsXml)

RDF_LITERAL_PROP_TYPE_MAPPER = {
    IntermediaryBoolean: RDFPropTypeInfo(KNORA_API.BooleanValue, KNORA_API.booleanValueAsBoolean, XSD.boolean),
    IntermediaryColor: RDFPropTypeInfo(KNORA_API.ColorValue, KNORA_API.colorValueAsColor, XSD.string),
    IntermediaryDecimal: RDFPropTypeInfo(KNORA_API.DecimalValue, KNORA_API.decimalValueAsDecimal, XSD.decimal),
    IntermediaryGeometry: RDFPropTypeInfo(KNORA_API.GeomValue, KNORA_API.geometryValueAsGeometry, XSD.string),
    IntermediaryGeoname: RDFPropTypeInfo(KNORA_API.GeonameValue, KNORA_API.geonameValueAsGeonameCode, XSD.string),
    IntermediaryInt: RDFPropTypeInfo(KNORA_API.IntValue, KNORA_API.intValueAsInt, XSD.integer),
    IntermediarySimpleText: RDFPropTypeInfo(KNORA_API.TextValue, KNORA_API.valueAsString, XSD.string),
    IntermediaryTime: RDFPropTypeInfo(KNORA_API.TimeValue, KNORA_API.timeValueAsTimeStamp, XSD.dateTimeStamp),
    IntermediaryUri: RDFPropTypeInfo(KNORA_API.UriValue, KNORA_API.uriValueAsUri, XSD.anyURI),
}


ARCHIVE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.ArchiveFileValue, KNORA_API.hasArchiveFileValue)
AUDIO_FILE_VALUE = RDFPropTypeInfo(KNORA_API.AudioFileValue, KNORA_API.hasAudioFileValue)
DOCUMENT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.DocumentFileValue, KNORA_API.hasDocumentFileValue)
MOVING_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.MovingImageFileValue, KNORA_API.hasMovingImageFileValue)
STILL_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.StillImageFileValue, KNORA_API.hasStillImageFileValue)
TEXT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.TextFileValue, KNORA_API.hasTextFileValue)
IIIF_URI_VALUE = RDFPropTypeInfo(KNORA_API.StillImageExternalFileValue, KNORA_API.hasStillImageFileValue)
