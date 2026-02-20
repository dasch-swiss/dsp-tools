"""
This module implements reading DSP users.
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import Any

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.group import PROJECT_ADMIN_GROUP
from dsp_tools.commands.get.legacy_models.group import PROJECT_MEMBER_GROUP
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import Languages


@dataclass(frozen=True)
class User:
    """Represents a DSP user."""

    username: str
    email: str
    status: bool
    given_name: str | None
    family_name: str | None
    lang: Languages | None
    in_projects: dict[str, bool]
    in_groups: frozenset[str]

    def to_definition_file_obj(
        self,
        con: Connection,
        proj_shortname: str,
        proj_iri: str,
    ) -> dict[str, str | list[str] | bool | None]:
        """Create a JSON object that can be used to create a project definition file."""
        groups: list[str] = []
        for group_iri in self.in_groups:
            group_info = con.get(f"/admin/groups/{urllib.parse.quote_plus(group_iri)}")
            if "group" in group_info and "name" in group_info["group"]:
                groupname = group_info["group"]["name"]
                groups.append(f"{proj_shortname}:{groupname}")

        projects: list[str] = []
        for proj, is_admin in self.in_projects.items():
            if proj == proj_iri:
                if is_admin:
                    projects.append(f"{proj_shortname}:admin")
                else:
                    projects.append(f"{proj_shortname}:member")

        user: dict[str, str | list[str] | bool | None] = {
            "username": self.username,
            "email": self.email,
            "givenName": self.given_name,
            "familyName": self.family_name,
            "password": "",
            "groups": groups,
            "projects": projects,
            "status": self.status,
        }
        if self.lang:
            user["lang"] = self.lang.value
        return user


def create_user_from_json(json_obj: dict[str, Any]) -> User:
    """Create a User from a JSON object returned by DSP API."""
    _check_json_obj_has_required_info(json_obj)
    in_groups, in_projects = _extract_permissions_and_groups(json_obj)
    lang = _parse_language(json_obj.get("lang"))
    return User(
        username=json_obj["username"],
        email=json_obj["email"],
        status=json_obj["status"],
        given_name=json_obj.get("givenName"),
        family_name=json_obj.get("familyName"),
        lang=lang,
        in_projects=in_projects,
        in_groups=in_groups,
    )


def _check_json_obj_has_required_info(json_obj: dict[str, Any]) -> None:
    problems: list[str] = []
    if json_obj.get("email") is None:
        problems.append('User "email" is missing in JSON from DSP')
    if json_obj.get("username") is None:
        problems.append('User "username" is missing in JSON from DSP')
    if json_obj.get("status") is None:
        problems.append('User "status" is missing in JSON from DSP')
    if problems:
        raise BaseError("\n".join(problems))


def _parse_language(lang: str | None) -> Languages | None:
    if lang is None:
        return None
    lang_map = {a.value: a for a in Languages}
    if lang_map.get(lang) is None:
        raise BaseError(f'Invalid language string "{lang}"!')
    return lang_map[lang]


def _extract_permissions_and_groups(json_obj: dict[str, Any]) -> tuple[frozenset[str], dict[str, bool]]:
    in_projects: dict[str, bool] = {}
    in_groups: set[str] = set()
    if json_obj.get("permissions") is not None and json_obj["permissions"].get("groupsPerProject") is not None:
        for project_iri, group_memberships in json_obj["permissions"]["groupsPerProject"].items():
            for group in group_memberships:
                if group == PROJECT_MEMBER_GROUP:
                    if in_projects.get(project_iri) is None:
                        in_projects[project_iri] = False
                elif group == PROJECT_ADMIN_GROUP:
                    in_projects[project_iri] = True
                else:
                    in_groups.add(group)
    return frozenset(in_groups), in_projects


def get_all_users_for_project(con: Connection, proj_shortcode: str) -> list[User] | None:
    """
    Get a list of all users that belong to a project.

    Args:
        con: Connection instance
        proj_shortcode: Shortcode of the project

    Returns:
        List of users belonging to that project, or None if no users found
    """
    members = con.get(f"/admin/projects/shortcode/{proj_shortcode}/members")
    if not members or "members" not in members or not members["members"]:
        return None
    res: list[User] = [create_user_from_json(a) for a in members["members"]]
    res.reverse()
    return res
