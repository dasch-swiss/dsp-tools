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
    resources: list[ResourceDeserialised]


@dataclass
class PermissionsDeserialised:
    permission_id: str
    permission_dict: dict[str, str]


@dataclass
class ResourceDeserialised:
    res_id: str
    res_class: str
    label: str
    permissions: str | None
    values: list[ValueDeserialised]
    file_value: AbstractFileValue | None


@dataclass
class AbstractFileValue(Protocol):
    permissions: str | None


@dataclass
class FileValueDeserialised(AbstractFileValue):
    file_path: Path
    permissions: str | None


@dataclass
class ExternalFileValueDeserialised(AbstractFileValue):
    iiif_uri: str
    permissions: str | None


@dataclass
class ValueDeserialised(Protocol):
    prop_name: str
    prop_value: Any
    permissions: str | None
    comments: str | None


@dataclass
class SimpleTextDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    permissions: str | None
    comments: str | None


@dataclass
class RichtextDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    permissions: str | None
    comments: str | None


@dataclass
class ListDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    list_name: str
    permissions: str | None
    comments: str | None


@dataclass
class LinkValueDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    permissions: str | None
    comments: str | None
