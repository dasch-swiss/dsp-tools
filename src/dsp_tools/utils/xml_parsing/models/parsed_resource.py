from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto

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


@dataclass
class FileValueMetadata:
    license_iri: str | None
    copyright_holder: str | None
    authorships: list[str] | None
    permissions: str | None


class KnoraValueType(Enum):
    """
    Maps to a knora value type, for example: BOOLEAN_VALUE -> knora-api:BooleanValue
    """

    BOOLEAN_VALUE = auto()
    COLOR_VALUE = auto()
    DATE_VALUE = auto()
    DECIMAL_VALUE = auto()
    GEONAME_VALUE = auto()
    GEOM_VALUE = auto()
    INT_VALUE = auto()
    INTERVAL_VALUE = auto()
    LINK_VALUE = auto()
    LIST_VALUE = auto()
    SIMPLETEXT_VALUE = auto()
    RICHTEXT_VALUE = auto()
    TIME_VALUE = auto()
    URI_VALUE = auto()

    ARCHIVE_FILE = auto()
    AUDIO_FILE = auto()
    DOCUMENT_FILE = auto()
    MOVING_IMAGE_FILE = auto()
    STILL_IMAGE_FILE = auto()
    STILL_IMAGE_IIIF = auto()
    TEXT_FILE = auto()
