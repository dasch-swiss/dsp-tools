from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions


@dataclass
class ProcessedFileMetadata:
    license_iri: str | None
    copyright_holder: str | None
    authorships: list[str] | None
    permissions: Permissions | None = None

    def all_legal_info(self) -> bool:
        return all([self.license_iri, self.copyright_holder, self.authorships])


@dataclass
class ProcessedFileValue:
    value: str
    metadata: ProcessedFileMetadata
    res_id: str
    res_label: str


@dataclass
class ProcessedIIIFUri:
    value: str
    metadata: ProcessedFileMetadata
