from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions


@dataclass
class IntermediaryFileMetadata:
    license_iri: str | None
    copyright_holder: str | None
    authorships: list[str] | None
    permissions: Permissions | None = None


@dataclass
class IntermediaryFileValue:
    value: str
    metadata: IntermediaryFileMetadata
    res_id: str
    res_label: str


@dataclass
class IntermediaryIIIFUri:
    value: str
    metadata: IntermediaryFileMetadata
