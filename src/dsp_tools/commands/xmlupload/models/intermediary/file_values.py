from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions


@dataclass
class IntermediaryFileMetadata:
    permissions: Permissions | None


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
