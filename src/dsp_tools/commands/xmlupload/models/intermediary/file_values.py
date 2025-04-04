from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType


@dataclass
class IntermediaryFileMetadata:
    license_iri: str | None
    copyright_holder: str | None
    authorships: list[str] | None
    permissions: Permissions | None = None

    def all_legal_info(self) -> bool:
        return all([self.license_iri, self.copyright_holder, self.authorships])


@dataclass
class IntermediaryFileValue:
    value: str
    value_type: KnoraValueType
    metadata: IntermediaryFileMetadata
    res_id: str
    res_label: str


@dataclass
class IntermediaryIIIFUri:
    value: str
    metadata: IntermediaryFileMetadata
