from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedIIIFUri
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedValue
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp


@dataclass
class ProcessedResource:
    res_id: str
    type_iri: str
    label: str
    permissions: Permissions | None
    values: list[ProcessedValue]
    file_value: ProcessedFileValue | None = None
    iiif_uri: ProcessedIIIFUri | None = None
    migration_metadata: MigrationMetadata | None = None


@dataclass
class MigrationMetadata:
    iri_str: str | None
    creation_date: DateTimeStamp | None
