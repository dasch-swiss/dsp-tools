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
class IntermediaryAbstractFileValue:
    value: str
    metadata: IntermediaryFileMetadata


@dataclass
class IntermediaryFileValue: ...


@dataclass
class IntermediaryIIIFUri: ...
