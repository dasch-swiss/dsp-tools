"""
This module implements reading DSP groups.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString
from dsp_tools.legacy_models.langstring import create_lang_string
from dsp_tools.legacy_models.langstring import create_lang_string_from_json

PROJECT_MEMBER_GROUP = "http://www.knora.org/ontology/knora-admin#ProjectMember"
PROJECT_ADMIN_GROUP = "http://www.knora.org/ontology/knora-admin#ProjectAdmin"
GROUPS_ROUTE = "/admin/groups"


@dataclass(frozen=True)
class Group:
    """Represents a DSP group."""

    iri: str
    name: str
    project: str
    selfjoin: bool
    status: bool
    descriptions: LangString

    def to_definition_file_obj(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "descriptions": self.descriptions.to_definition_file_obj(),
            "selfjoin": self.selfjoin,
            "status": self.status,
        }


def create_group_from_json(json_obj: dict[str, Any]) -> Group:
    """Create a Group from a JSON object returned by DSP API."""
    group_id = json_obj.get("id")
    if group_id is None:
        raise BaseError('Group "id" is missing')
    name = json_obj.get("name")
    if name is None:
        raise BaseError('Group "name" is missing')
    descriptions = create_lang_string_from_json(json_obj.get("descriptions")) or create_lang_string()
    tmp = json_obj.get("project")
    if tmp is None:
        raise BaseError('Group "project" is missing')
    project = tmp.get("id")
    if project is None:
        raise BaseError('Group "project" has no "id"')
    selfjoin = json_obj.get("selfjoin")
    if selfjoin is None:
        raise BaseError("selfjoin is missing")
    status = json_obj.get("status")
    if status is None:
        raise BaseError("Status is missing")
    return Group(
        iri=group_id,
        name=name,
        descriptions=descriptions,
        project=project,
        selfjoin=selfjoin,
        status=status,
    )


def get_all_groups(con: Connection) -> list[Group]:
    """Get all groups from DSP."""
    result = con.get(GROUPS_ROUTE)
    return [create_group_from_json(group_item) for group_item in result["groups"]]


def get_all_groups_for_project(con: Connection, proj_iri: str) -> list[Group]:
    """Get all groups for a specific project."""
    return [g for g in get_all_groups(con) if g.project == proj_iri]
