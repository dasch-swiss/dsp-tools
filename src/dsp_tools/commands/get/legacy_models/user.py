"""
This module implements reading DSP users.
"""

from __future__ import annotations

import urllib.parse
from typing import Any
from typing import Optional
from typing import Union

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.group import Group
from dsp_tools.commands.get.legacy_models.model import Model
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import Languages


class User(Model):
    """
    This class represents a user in DSP.

    Attributes
    ----------

    iri : str
        IRI of the user [readonly]

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

    _iri: str
    _username: str
    _email: str
    _givenName: str
    _familyName: str
    _lang: Languages
    _status: bool
    _in_groups: set[str]
    _in_projects: dict[str, bool]

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        givenName: Optional[str] = None,
        familyName: Optional[str] = None,
        lang: Optional[Union[str, Languages]] = None,
        status: Optional[bool] = None,
        in_projects: Optional[dict[str, bool]] = None,
        in_groups: Optional[set[str]] = None,
    ):
        super().__init__(con)
        self._iri = iri
        self._username = str(username) if username is not None else None
        self._email = str(email) if email is not None else None
        self._givenName = str(givenName) if givenName is not None else None
        self._familyName = str(familyName) if familyName is not None else None
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
        self._status = None if status is None else bool(status)

        if in_projects is None or isinstance(in_projects, dict):
            self._in_projects = in_projects if in_projects is not None else {}
        else:
            raise BaseError("In_project must be tuple (project-iri: str, is-admin: bool)!")

        if in_groups is None or isinstance(in_groups, set):
            self._in_groups = in_groups if in_groups is not None else set()
        else:
            raise BaseError("In_groups must be a set of strings or None!")

    @property
    def iri(self) -> Optional[str]:
        return self._iri

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def email(self) -> Optional[str]:
        return self._email

    @property
    def givenName(self) -> Optional[str]:
        return self._givenName

    @property
    def familyName(self) -> Optional[str]:
        return self._familyName

    @property
    def lang(self) -> Optional[Languages]:
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
    def _make_fromJsonObj(cls, con: Connection, json_obj: dict[str, Any]) -> User:
        User._check_if_jsonObj_has_required_info(json_obj)

        in_groups, in_projects = cls._update_permissions_and_groups(json_obj)

        return cls(
            con=con,
            iri=json_obj["id"],
            username=json_obj["username"],
            email=json_obj["email"],
            givenName=json_obj.get("givenName"),
            familyName=json_obj.get("familyName"),
            lang=json_obj.get("lang"),
            status=json_obj["status"],
            in_projects=in_projects,
            in_groups=in_groups,
        )

    @staticmethod
    def _check_if_jsonObj_has_required_info(json_obj: dict[str, Any]) -> None:
        problems = []
        if json_obj.get("id") is None:
            problems.append('User "iri" is missing in JSON from DSP')

        if json_obj.get("email") is None:
            problems.append('User "email" is missing in JSON from DSP')

        if json_obj.get("username") is None:
            problems.append('User "email" is missing in JSON from DSP')

        if json_obj.get("status") is None:
            problems.append('User "email" is missing in JSON from DSP')

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
    def getAllUsersForProject(con: Connection, proj_shortcode: str) -> Optional[list[User]]:
        """
        Get a list of all users that belong to a project (static method)

        :param con: Connection instance
        :project_shortcode: Shortcode of the project
        :return: List of users belonging to that project
        """
        members = con.get(f"/admin/projects/shortcode/{proj_shortcode}/members")
        if members is None or len(members) < 1:
            return None
        res: list[User] = [User._make_fromJsonObj(con, a) for a in members["members"]]
        res.reverse()
        return res

    def createDefinitionFileObj(
        self,
        con: Connection,
        proj_shortname: str,
        proj_iri: str,
    ) -> dict[str, Union[str, list[str], bool, None]]:
        """Create a JSON object that can be used to create a project definition file"""
        user: dict[str, Union[str, list[str], bool, None]] = {
            "username": self.username,
            "email": self._email,
            "givenName": self._givenName,
            "familyName": self._familyName,
            "password": "",
        }
        if self._lang:
            user["lang"] = self._lang.value
        groups = list()
        for group_iri in self._in_groups:
            group_info = con.get(f"/admin/groups/{urllib.parse.quote_plus(group_iri)}")
            if "group" in group_info and "name" in group_info["group"]:
                groupname = group_info["group"]["name"]
                groups.append(f"{proj_shortname}:{groupname}")
        user["groups"] = groups
        user["projects"] = list()
        for proj, is_admin in self._in_projects.items():
            if proj == proj_iri:
                if is_admin:
                    user["projects"].append(f"{proj_shortname}:admin")
                else:
                    user["projects"].append(f"{proj_shortname}:member")
        user["status"] = self._status
        return user
