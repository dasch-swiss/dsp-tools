from __future__ import annotations

from dataclasses import dataclass

from rdflib import Namespace
from rdflib import URIRef

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


# TODO: import this from the other file
@dataclass
class RDFPropTypeInfo:
    knora_type: URIRef
    knora_prop: URIRef


@dataclass
class AbstractFileValue:
    internal_filename: str
    metadata: FileValueMetadata


@dataclass
class FileValueMetadata:
    permissions: str | None


archive_file_value = RDFPropTypeInfo(KNORA_API.ArchiveFileValue, KNORA_API.hasArchiveFileValue)
audio_file_value = RDFPropTypeInfo(KNORA_API.AudioFileValue, KNORA_API.hasAudioFileValue)
document_file_value = RDFPropTypeInfo(KNORA_API.DocumentFileValue, KNORA_API.hasDocumentFileValue)
moving_image_file_value = RDFPropTypeInfo(KNORA_API.MovingImageFileValue, KNORA_API.hasMovingImageFileValue)
still_image_file_value = RDFPropTypeInfo(KNORA_API.StillImageFileValue, KNORA_API.hasStillImageFileValue)
text_file_value = RDFPropTypeInfo(KNORA_API.TextFileValue, KNORA_API.hasTextFileValue)

file_extension_to_type_mapper = {
    # ArchiveFileValue
    "zip": archive_file_value,
    "tar": archive_file_value,
    "gz": archive_file_value,
    "z": archive_file_value,
    "tgz": archive_file_value,
    "gzip": archive_file_value,
    "7z": archive_file_value,
    # AudioFileValue
    "mp3": audio_file_value,
    "wav": audio_file_value,
    # DocumentFileValue
    "pdf": document_file_value,
    "doc": document_file_value,
    "docx": document_file_value,
    "xls": document_file_value,
    "xlsx": document_file_value,
    "ppt": document_file_value,
    "pptx": document_file_value,
    # MovingImageFileValue
    "mp4": moving_image_file_value,
    # StillImageFileValue
    "jpg": still_image_file_value,
    "jpeg": still_image_file_value,
    "jp2": still_image_file_value,
    "png": still_image_file_value,
    "tif": still_image_file_value,
    "tiff": still_image_file_value,
    "jpx": still_image_file_value,
    # TextFileValue
    "odd": text_file_value,
    "rng": text_file_value,
    "txt": text_file_value,
    "xml": text_file_value,
    "xsd": text_file_value,
    "xsl": text_file_value,
    "csv": text_file_value,
}
