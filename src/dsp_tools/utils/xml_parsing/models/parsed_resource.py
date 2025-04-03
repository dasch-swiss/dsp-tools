from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto


@dataclass
class ParsedResource:
    res_id: str
    res_type: str
    label: str
    permissions_id: str | None
    values: list[ParsedValue]
    file_value: ParsedFileValue | None
    migration_metadata: ParsedMigrationMetadata | None


@dataclass
class ParsedMigrationMetadata:
    iri: str | None
    ark: str | None
    creation_date: str | None


@dataclass
class ParsedValue:
    prop_name: str
    value: str | tuple[str | None, str | None] | None
    value_type: KnoraValueType
    permissions_id: str | None
    comment: str | None


@dataclass
class ParsedFileValue:
    value: str | None
    value_type: KnoraValueType | None
    metadata: ParsedFileValueMetadata


@dataclass
class ParsedFileValueMetadata:
    license_iri: str | None
    copyright_holder: str | None
    authorship_id: str | None
    permissions_id: str | None


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
