from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadata


@dataclass
class ParsedResource:
    res_id: str
    res_type: str
    label: str
    permissions: str | None
    values: list[ParsedValue]
    file_value: ParsedValue | None
    migration_metadata: MigrationMetadata


@dataclass
class ParsedValue:
    prop_name: str
    value: str | tuple[str, str] | None
    value_type: KnoraValueType
    permissions: str | None = None
    comment: str | None = None


@dataclass
class ParsedFileValue:
    value: str
    value_type: KnoraValueType
    metadata: FileValueMetadata
