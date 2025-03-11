from typing import TypeAlias
from typing import Union

from rdflib import XSD
from rdflib import Namespace
from rdflib.term import IdentifiedNode
from rdflib.term import Literal
from rdflib.term import Node
from rdflib.term import Variable

from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo

# rdflib typing
PropertyTypeAlias: TypeAlias = Union[IdentifiedNode, Variable]
SubjectObjectTypeAlias: TypeAlias = Union[IdentifiedNode, Literal, Variable, Node]

# Namespaces as string
KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
API_SHAPES_STR = "http://api.knora.org/ontology/knora-api/shapes/v2#"

LINKOBJ_RESOURCE = KNORA_API_STR + "LinkObj"
VIDEO_SEGMENT_RESOURCE = KNORA_API_STR + "VideoSegment"
AUDIO_SEGMENT_RESOURCE = KNORA_API_STR + "AudioSegment"

# rdflib Namespaces
DASH = Namespace("http://datashapes.org/dash#")
KNORA_API = Namespace(KNORA_API_STR)
API_SHAPES = Namespace(API_SHAPES_STR)

DATA = Namespace("http://data/")


ARCHIVE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.ArchiveFileValue, KNORA_API.fileValueHasFilename, XSD.string)
AUDIO_FILE_VALUE = RDFPropTypeInfo(KNORA_API.AudioFileValue, KNORA_API.fileValueHasFilename, XSD.string)
DOCUMENT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.DocumentFileValue, KNORA_API.fileValueHasFilename, XSD.string)
MOVING_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.MovingImageFileValue, KNORA_API.fileValueHasFilename, XSD.string)
STILL_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.StillImageFileValue, KNORA_API.fileValueHasFilename, XSD.string)
TEXT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.TextFileValue, KNORA_API.fileValueHasFilename, XSD.string)
IIIF_URI_VALUE = RDFPropTypeInfo(
    KNORA_API.StillImageExternalFileValue, KNORA_API.stillImageFileValueHasExternalUrl, XSD.anyURI
)


# validation results

FILE_VALUE_PROPERTIES = {
    KNORA_API.hasArchiveFileValue,
    KNORA_API.hasAudioFileValue,
    KNORA_API.hasDocumentFileValue,
    KNORA_API.hasMovingImageFileValue,
    KNORA_API.hasTextFileValue,
    KNORA_API.hasStillImageFileValue,
    KNORA_API.hasLicense,
    KNORA_API.hasCopyrightHolder,
    KNORA_API.hasAuthorship,
}


FILEVALUE_DETAIL_INFO = {
    API_SHAPES.hasArchiveFileValue: ("bitstream", "'zip', 'tar', 'gz', 'z', 'tgz', 'gzip', '7z'"),
    API_SHAPES.hasAudioFileValue: ("bitstream", "'mp3', 'wav'"),
    API_SHAPES.hasDocumentFileValue: ("bitstream", "'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'"),
    API_SHAPES.hasMovingImageFileValue: ("bitstream", "'mp4'"),
    API_SHAPES.hasTextFileValue: ("bitstream", "'odd', 'rng', 'txt', 'xml', 'xsd', 'xsl', 'csv', 'json'"),
    API_SHAPES.hasStillImageFileValue: (
        "bitstream / iiif-uri",
        "'jpg', 'jpeg', 'png', 'tif', 'tiff', 'jp2' or a IIIF-URI",
    ),
}
