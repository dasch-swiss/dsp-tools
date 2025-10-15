from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology


@dataclass
class ParsedProject:
    prefixes: dict[str, str]
    project_metadata: ParsedProjectMetadata
    permissions: ParsedPermissions
    groups: list[ParsedGroups]
    users: list[ParsedUser]
    lists: list[ParsedList]
    ontologies: list[ParsedOntology]


@dataclass
class ParsedProjectMetadata:
    shortcode: str
    shortname: str
    longname: str
    descriptions: dict[str, str]
    keywords: list[str]
    enabled_licenses: list[str]


@dataclass
class ParsedPermissions:
    default_permissions: str
    default_permissions_overrule: dict[str, Any]


@dataclass
class ParsedGroups:
    info: dict[str, Any]


@dataclass
class ParsedUser:
    info: dict[str, Any]


@dataclass
class ParsedList:
    info: dict[str, Any]
