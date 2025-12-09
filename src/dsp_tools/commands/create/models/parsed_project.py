from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology


@dataclass
class ParsedProject:
    prefixes: dict[str, str]
    project_metadata: ParsedProjectMetadata
    permissions: ParsedPermissions
    groups: list[ParsedGroup]
    users: list[ParsedUser]
    user_memberships: list[ParsedUserMemberShipInfo]
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


class DefaultPermissions(Enum):
    PUBLIC = "public"
    PRIVATE = "private"


@dataclass
class LimitedViewPermissions:
    all_limited: bool
    limited_selection: list[str] | None


@dataclass
class ParsedPermissions:
    default_permissions: DefaultPermissions
    overrule_private: list[str] | None
    overrule_limited_view: LimitedViewPermissions | None


@dataclass
class ParsedGroup:
    name: str
    descriptions: list[ParsedGroupDescription]


@dataclass
class ParsedGroupDescription:
    lang: str
    text: str


@dataclass
class ParsedUser:
    username: str
    email: str
    given_name: str
    family_name: str
    password: str
    lang: str


@dataclass
class ParsedUserMemberShipInfo:
    username: str
    is_admin: bool
    groups: list[str]


@dataclass
class ParsedList:
    list_info: ParsedNodeInfo
    children: list[ParsedListNode]


@dataclass
class ParsedNodeInfo:
    name: str
    labels: dict[str, str]
    comments: dict[str, str] | None


@dataclass
class ParsedListNode:
    node_info: ParsedNodeInfo
    children: list[ParsedListNode]
