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


ARCHIVE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.ArchiveFileValue, KNORA_API.hasArchiveFileValue)
AUDIO_FILE_VALUE = RDFPropTypeInfo(KNORA_API.AudioFileValue, KNORA_API.hasAudioFileValue)
DOCUMENT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.DocumentFileValue, KNORA_API.hasDocumentFileValue)
MOVING_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.MovingImageFileValue, KNORA_API.hasMovingImageFileValue)
STILL_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.StillImageFileValue, KNORA_API.hasStillImageFileValue)
TEXT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.TextFileValue, KNORA_API.hasTextFileValue)
