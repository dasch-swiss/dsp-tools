from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology


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
class DoapCategories:
    class_doaps: list[dict[str, Any]]
    prop_doaps: list[dict[str, Any]]
    has_img_all_classes_doaps: list[dict[str, Any]]
    has_img_specific_class_doaps: list[dict[str, Any]]


@dataclass
class CustomGroup:
    info: dict[str, Any]


@dataclass
class ParsedUser:
    info: dict[str, Any]


@dataclass
class ParsedList:
    info: dict[str, Any]
