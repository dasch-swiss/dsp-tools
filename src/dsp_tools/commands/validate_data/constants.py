from rdflib import XSD

from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.utils.rdflib_constants import KNORA_API

# paths for the validation files used by the docker container

ONTOLOGIES_DATA_TTL = "ONTOLOGIES_DATA.ttl"
ONTOLOGIES_SHACL_TTL = "ONTOLOGIES_SHACL.ttl"
ONTOLOGIES_REPORT_TTL = "ONTOLOGIES_REPORT.ttl"

CARDINALITY_DATA_TTL = "CARDINALITY_DATA.ttl"
CARDINALITY_SHACL_TTL = "CARDINALITY_SHACL.ttl"
CARDINALITY_REPORT_TTL = "CARDINALITY_REPORT.ttl"

CONTENT_DATA_TTL = "CONTENT_DATA.ttl"
CONTENT_SHACL_TTL = "CONTENT_SHACL.ttl"
CONTENT_REPORT_TTL = "CONTENT_REPORT.ttl"


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
    KNORA_API.hasArchiveFileValue: ("bitstream", "'zip', 'tar', 'gz', 'z', 'tgz', 'gzip', '7z'"),
    KNORA_API.hasAudioFileValue: ("bitstream", "'mp3', 'wav'"),
    KNORA_API.hasDocumentFileValue: ("bitstream", "'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'epub'"),
    KNORA_API.hasMovingImageFileValue: ("bitstream", "'mp4'"),
    KNORA_API.hasTextFileValue: ("bitstream", "'odd', 'rng', 'txt', 'xml', 'htm', 'html', 'xsd', 'xsl', 'csv', 'json'"),
    KNORA_API.hasStillImageFileValue: (
        "bitstream / iiif-uri",
        "'jpg', 'jpeg', 'png', 'tif', 'tiff', 'jp2' or a IIIF-URI",
    ),
}

LEGAL_INFO_PROPS = {KNORA_API.hasLicense, KNORA_API.hasCopyrightHolder, KNORA_API.hasAuthorship}
