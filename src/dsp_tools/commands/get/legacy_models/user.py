"""
This module implements reading DSP users.
"""

from __future__ import annotations

import urllib.parse
from typing import Any

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.group import Group
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import Languages


class User:
    """
    This class represents a user in DSP.

    Attributes
    ----------

    username : str
        Unique identifier (not an IRI) of the user [readonly]

    email : str
        Email of the user [readonly]

    givenName : str
        Given name (firstname) of the user [readonly]

    familyName : str
        Family name of user (lastname) [readonly]

    lang : Language
        Preferred language of the user [readonly]

    status : bool
        Status of the user, If active, is set to True, otherwise false [readonly]

    in_groups : set[str]
        Set of group IRI's the user is member of [readonly]

    in_projects : dict[str, bool]
        Dict with project-IRI as key, boolean(True=project admin) as value [readonly]


    Methods
    -------

    getAllUsersForProject : list of users
        Get a list of all users for a project

    """

    _username: str
    _email: str
    _givenName: str | None
    _familyName: str | None
    _lang: Languages | None
    _status: bool
    _in_groups: set[str]
    _in_projects: dict[str, bool]

    def __init__(
        self,
        username: str,
        email: str,
        status: bool,
        givenName: str | None = None,
        familyName: str | None = None,
        lang: str | Languages | None = None,
        in_projects: dict[str, bool] | None = None,
        in_groups: set[str] | None = None,
    ):
        self._username = username
        self._email = email
        self._status = status
        self._givenName = givenName
        self._familyName = familyName
        if lang is not None:
            if isinstance(lang, Languages):
                self._lang = lang
            else:
                lmap = {a.value: a for a in Languages}
                if lmap.get(lang) is None:
                    raise BaseError('Invalid language string "' + lang + '"!')
                self._lang = lmap[lang]
        else:
            self._lang = None
        self._in_projects = in_projects or {}
        self._in_groups = in_groups or set()

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @property
    def givenName(self) -> str | None:
        return self._givenName

    @property
    def familyName(self) -> str | None:
        return self._familyName

    @property
    def lang(self) -> Languages | None:
        return self._lang

    @property
    def status(self) -> bool:
        return self._status

    @property
    def in_groups(self) -> set[str]:
        return self._in_groups

    @property
    def in_projects(self) -> dict[str, bool]:
        return self._in_projects

    @classmethod
    def _make_fromJsonObj(cls, json_obj: dict[str, Any]) -> User:
        User._check_if_jsonObj_has_required_info(json_obj)

        in_groups, in_projects = cls._update_permissions_and_groups(json_obj)

        return cls(
            username=json_obj["username"],
            email=json_obj["email"],
            status=json_obj["status"],
            givenName=json_obj.get("givenName"),
            familyName=json_obj.get("familyName"),
            lang=json_obj.get("lang"),
            in_projects=in_projects,
            in_groups=in_groups,
        )

    @staticmethod
    def _check_if_jsonObj_has_required_info(json_obj: dict[str, Any]) -> None:
        problems = []
        if json_obj.get("email") is None:
            problems.append('User "email" is missing in JSON from DSP')

        if json_obj.get("username") is None:
            problems.append('User "username" is missing in JSON from DSP')

        if json_obj.get("status") is None:
            problems.append('User "status" is missing in JSON from DSP')

        if problems:
            raise BaseError("\n".join(problems))

    @classmethod
    def _update_permissions_and_groups(cls, json_obj: dict[str, Any]) -> tuple[set[str], dict[str, bool]]:
        in_projects: dict[str, bool] = {}
        in_groups: set[str] = set()
        if json_obj.get("permissions") is not None and json_obj["permissions"].get("groupsPerProject") is not None:
            for project_iri, group_memberships in json_obj["permissions"]["groupsPerProject"].items():
                for group in group_memberships:
                    if group == Group.PROJECT_MEMBER_GROUP:
                        if in_projects.get(project_iri) is None:
                            in_projects[project_iri] = False
                    elif group == Group.PROJECT_ADMIN_GROUP:
                        in_projects[project_iri] = True
                    else:
                        in_groups.add(group)
            return in_groups, in_projects
        return in_groups, in_projects

    @staticmethod
    def getAllUsersForProject(con: Connection, proj_shortcode: str) -> list[User] | None:
        """
        Get a list of all users that belong to a project (static method)

        :param con: Connection instance
        :project_shortcode: Shortcode of the project
        :return: List of users belonging to that project
        """
        members = con.get(f"/admin/projects/shortcode/{proj_shortcode}/members")
        if members is None or len(members) < 1:
            return None
        res: list[User] = [User._make_fromJsonObj(a) for a in members["members"]]
        res.reverse()
        return res

    def createDefinitionFileObj(
        self,
        con: Connection,
        proj_shortname: str,
        proj_iri: str,
    ) -> dict[str, str | list[str] | bool | None]:
        """Create a JSON object that can be used to create a project definition file"""
        groups: list[str] = []
        for group_iri in self._in_groups:
            group_info = con.get(f"/admin/groups/{urllib.parse.quote_plus(group_iri)}")
            if "group" in group_info and "name" in group_info["group"]:
                groupname = group_info["group"]["name"]
                groups.append(f"{proj_shortname}:{groupname}")

        projects: list[str] = []
        for proj, is_admin in self._in_projects.items():
            if proj == proj_iri:
                if is_admin:
                    projects.append(f"{proj_shortname}:admin")
                else:
                    projects.append(f"{proj_shortname}:member")

        user: dict[str, str | list[str] | bool | None] = {
            "username": self.username,
            "email": self._email,
            "givenName": self._givenName,
            "familyName": self._familyName,
            "password": "",
            "groups": groups,
            "projects": projects,
            "status": self._status,
        }
        if self._lang:
            user["lang"] = self._lang.value
        return user
