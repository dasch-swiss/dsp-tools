from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType


@dataclass
class ProcessedFileMetadata:
    license_iri: str
    copyright_holder: str
    authorships: list[str]
    permissions: Permissions | None = None


@dataclass
class ProcessedFileValue:
    value: str
    file_type: KnoraValueType
    metadata: ProcessedFileMetadata
    res_id: str
    res_label: str


@dataclass
class ProcessedIIIFUri:
    value: str
    metadata: ProcessedFileMetadata
