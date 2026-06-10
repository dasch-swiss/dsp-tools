from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.utils.rdf_constants import URN_DASCH_PLACEHOLDER
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraFileValueType


@dataclass
class ProcessedFileMetadata:
    license_iri: str
    copyright_holder: str
    authorships: list[str]
    permissions: Permissions | None = None


@dataclass
class ProcessedFileValue:
    value: ProcessedFileValueValue
    value_type: KnoraFileValueType
    metadata: ProcessedFileMetadata


@dataclass
class ProcessedFileValueValue(ABC):
    value: str


@dataclass
class ProcessedFileBitstream(ProcessedFileValueValue):
    """Used for bitstream files, that require upload through ingest."""

    res_id: str


@dataclass
class ProcessedFileIIIFUri(ProcessedFileValueValue):
    """Used for the IIIF-URI, that do not require separate upload."""


@dataclass
class ProcessedFilePlaceholder(ProcessedFileValueValue):
    """Placeholder type"""

    def __init__(self) -> None:
        self.value = URN_DASCH_PLACEHOLDER
