from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ProjectDefinition:
    metadata: ProjectMetadata
    ontologies: list[dict[str, Any]]
    lists: list[dict[str, Any]] | None
    groups: list[dict[str, str]] | None
    users: list[dict[str, str]] | None


@dataclass
class ProjectMetadata:
    shortcode: str
    shortname: str
    longname: str
    keywords: list[str] | None
    descriptions: dict[str, str] | None
    enabled_licenses: list[str] | None
    default_permissions: str
    default_permissions_overrule: dict[str, str | list[str]] | None
