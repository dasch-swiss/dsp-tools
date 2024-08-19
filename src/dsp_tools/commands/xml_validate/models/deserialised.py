from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Protocol


@dataclass
class ProjectDeserialised:
    shortcode: str
    default_onto: str
    permissions: list[PermissionsDeserialised]
    xml_data: list[ResourceDeserialised]


@dataclass
class PermissionsDeserialised:
    permission_id: str
    permission_dict: dict[str, str]


@dataclass
class ResourceDeserialised:
    res_id: str
    res_class: str
    label: str
    permissions: str
    values: list[ValueDeserialised]
    file_value: AbstractFileValue | None = None
    comments: str | None = None


@dataclass
class AbstractFileValue(Protocol):
    permissions: str


@dataclass
class FileValueDeserialised(AbstractFileValue):
    file_path: Path
    permissions: str


@dataclass
class ExternalFileValueDeserialised(AbstractFileValue):
    iiif_uri: str
    permissions: str


@dataclass
class ValueDeserialised(Protocol):
    prop_name: str
    prop_value: Any
    permissions: str
    comments: str | None


@dataclass
class SimpleTextDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    permissions: str
    comments: str | None = None


@dataclass
class RichtextDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    permissions: str
    comments: str | None = None


@dataclass
class ListDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    list_name: str
    permissions: str
    comments: str | None = None


@dataclass
class BooleanDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: bool
    permissions: str
    comments: str | None = None
