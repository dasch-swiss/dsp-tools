from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryAbstractFileValue
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue


@dataclass
class IntermediaryResource:
    res_id: str
    type_iri: str
    label: str
    permissions: str | None
    values: list[IntermediaryValue]
    file_value: IntermediaryAbstractFileValue | None
    migration_metadata: MigrationMetadata | None


@dataclass
class MigrationMetadata:
    iri_str: str
    creation_date: str
