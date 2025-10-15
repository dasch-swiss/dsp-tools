from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.project.models.permissions_models import DoapCategories


class ParsedProject:
    prefixes: dict[str, str]
    project_metadata: ParsedProjectMetadata
    doaps: DoapCategories
    groups: list[CustomGroup]
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
class CustomGroup:
    info: dict[str, Any]


@dataclass
class ParsedUser:
    info: dict[str, Any]


@dataclass
class ParsedList:
    info: dict[str, Any]
