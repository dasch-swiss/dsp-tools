from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions


@dataclass
class IntermediaryFileMetadata:
    permissions: Permissions | None
    copyright_text: str | None
    license_text: str | None
    license_uri: str | None


@dataclass
class IntermediaryFileValue:
    value: str
    metadata: IntermediaryFileMetadata | None


@dataclass
class IntermediaryIIIFUri:
    value: str
    metadata: IntermediaryFileMetadata | None
