from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileValue
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryIIIFUri
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.models.datetimestamp import DateTimeStamp


@dataclass
class IntermediaryResource:
    res_id: str
    type_iri: str
    label: str
    permissions: Permissions | None
    values: list[IntermediaryValue]
    file_value: IntermediaryFileValue | None
    iiif_uri: IntermediaryIIIFUri | None
    migration_metadata: MigrationMetadata | None


@dataclass
class MigrationMetadata:
    iri_str: str
    creation_date: DateTimeStamp
