"""
This module implements the handling (CRUD) of DSP users.

CREATE:
    * Instantiate a new object of the class User with all required parameters
    * Call the ``create``-method on the instance to create the new user

READ:
    * Instantiate a new objects with ``iri`` given
    * Call the ``read``-method on the instance
    * Access the information that has been ptovided to the instance

In addition there is a static methods ``getAllProjects`` which returns a list of all projects
"""

from __future__ import annotations

import urllib.parse
from typing import Any
from typing import Optional
from typing import Union
from urllib.parse import quote_plus

from dsp_tools.commands.project.models.group import Group
from dsp_tools.commands.project.models.model import Model
from dsp_tools.commands.project.models.project import Project
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.langstring import Languages
from dsp_tools.utils.connection import Connection


class User(Model):
    """
    This class represents a user in DSP.

    Attributes
    ----------

    iri : str
        IRI of the user [readonly, cannot be modified after creation of instance]

    username : str
        Unique identifier (not an IRI) of the user [read/write]

    email : str
        Email of the user [read/write]

    givenName : str
        Given name (firstname) of the user [read/write]

    familyName : str
        Family name of user (lastname) [read/write]

    password : str
        Password of user [write only]

    lang : Language
        Preferred language of the user. For setting can be Language instance or string "EN", "DE", "FR", "IT"

    status : bool
        Status of the user, If active, is set to True, otherwise false [read/write]

    sysadmin : bool
        True, if user is system administrator [read/write]

    in_groups : set[str]
        Set of group IRI's the user is member of [readonly].

    in_projects : set[str]
        Set of project IRI's the user belongs to
        Use ``addToproject``and ``rmFromproject`` to modify project membership


    Methods
    -------

    create : DSP user information object
        Creates a new user and returns the information about this user as it is in DSP

    read : DSP user information object
        Read user data

    getAllUsers : list of user
        Get a list of all users

    print : None
        Prints the user information to stdout


    """

    ROUTE: str = "/admin/users"
    IRI: str = ROUTE + "/iri/"
    PROJECT_MEMBERSHIPS: str = "/project-memberships/"
    PROJECT_ADMIN_MEMBERSHIPS: str = "/project-admin-memberships/"
    GROUP_MEMBERSHIPS: str = "/group-memberships/"

    _iri: str
    _username: str
    _email: str
    _givenName: str
    _familyName: str
    _password: str
    _lang: Languages
    _status: bool
    _sysadmin: bool
    _in_groups: set[str]
    _in_projects: dict[str, bool]
    _add_to_project: dict[str, bool]
    _rm_from_project: dict[str, bool]
    _add_to_group: set[str]
    _rm_from_group: set[str]
    _change_admin: dict[str, bool]

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        givenName: Optional[str] = None,
        familyName: Optional[str] = None,
        password: Optional[str] = None,
        lang: Optional[Union[str, Languages]] = None,
        status: Optional[bool] = None,
        sysadmin: Optional[bool] = None,
        in_projects: Optional[dict[str, bool]] = None,
        in_groups: Optional[set[str]] = None,
    ):
        """
        Constructor for User

        The constructor is user internally or externally, when a new user should be created in DSP.

        :param con: Connection instance [required]
        :param iri: IRI of the user [required for CREATE, READ]
        :param username: Username [required for CREATE]
        :param email: Email address [required for CREATE]
        :param givenName: Given name (firstname) of user [required for CREATE]
        :param familyName: Family name (lastname) of user [required for CREATE]
        :param password: Password [required for CREATE]
        :param lang: Preferred language of the user [optional]
        :param status: Status (active = True, inactive/deleted = False) [optional]
        :param sysadmin: User has system administration privileges [optional]
        :param in_projects: Dict with project-IRI as key, boolean(True=project admin) as value [optional]
        :param in_groups: Set with group-IRI's the user should belong to [optional]
        """
        super().__init__(con)
        self._iri = iri
        self._username = str(username) if username is not None else None
        self._email = str(email) if email is not None else None
        self._givenName = str(givenName) if givenName is not None else None
        self._familyName = str(familyName) if familyName is not None else None
        self._password = str(password) if password is not None else None
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

        self._sysadmin = None if sysadmin is None else bool(sysadmin)

    @property
    def iri(self) -> Optional[str]:
        """IRI of this user"""
        return self._iri

    @property
    def username(self) -> Optional[str]:
        """Username of this user"""
        return self._username

    @username.setter
    def username(self, value: Optional[str]) -> None:
        if value is None:
            return
        self._username = str(value)
        self._changed.add("username")

    @property
    def email(self) -> Optional[str]:
        """Email address of this user"""
        return self._email

    @email.setter
    def email(self, value: Optional[str]) -> None:
        if value is None:
            return
        self._email = str(value)
        self._changed.add("email")

    @property
    def password(self) -> Optional[str]:
        """Password of this user"""
        return self._password

    @password.setter
    def password(self, value: Optional[str]) -> None:
        if value is None:
            return
        self._password = value
        self._changed.add("password")

    @property
    def givenName(self) -> Optional[str]:
        """Given name (firstname) of this user"""
        return self._givenName

    @givenName.setter
    def givenName(self, value: Optional[str]) -> None:
        if value is None:
            return
        self._givenName = str(value)
        self._changed.add("givenName")

    @property
    def familyName(self) -> Optional[str]:
        """Family name (lastname) of this user"""
        return self._familyName

    @familyName.setter
    def familyName(self, value: Optional[str]) -> None:
        if value is None:
            return
        self._familyName = str(value)
        self._changed.add("familyName")

    @property
    def lang(self) -> Optional[Languages]:
        """Language of this user"""
        return self._lang

    @lang.setter
    def lang(self, value: Optional[Union[str, Languages]]) -> None:
        if value is None:
            return
        if isinstance(value, Languages):
            self._lang = value
            self._changed.add("lang")
        else:
            lmap = {a.value: a for a in Languages}
            if lmap.get(value) is None:
                raise BaseError('Invalid language string "' + value + '"!')
            self._lang = lmap[value]
            self._changed.add("lang")

    @property
    def status(self) -> bool:
        """Status of this user (True=active, False=inactive)"""
        return self._status

    @status.setter
    def status(self, value: Optional[bool]) -> None:
        self._status = None if value is None else bool(value)
        if value is not None:
            self._changed.add("status")

    @property
    def sysadmin(self) -> bool:
        """True if the user is sysadmin"""
        return self._sysadmin

    @sysadmin.setter
    def sysadmin(self, value: bool) -> None:
        self._sysadmin = None if value is None else bool(value)
        if value is not None:
            self._changed.add("sysadmin")

    @property
    def in_groups(self) -> set[str]:
        """Set of group IRI's the user is member of"""
        return self._in_groups

    @property
    def in_projects(self) -> dict[str, bool]:
        """dict with project-IRI as key, boolean(True=project admin) as value"""
        return self._in_projects

    @classmethod
    def _make_fromJsonObj(cls, con: Connection, json_obj: dict[str, Any]) -> User:
        User._check_if_jsonObj_has_required_info(json_obj)

        sysadmin, in_groups, in_projects = cls._update_permissions_and_groups(json_obj)

        return cls(
            con=con,
            iri=json_obj["id"],
            username=json_obj["username"],
            email=json_obj["email"],
            givenName=json_obj.get("givenName"),
            familyName=json_obj.get("familyName"),
            lang=json_obj.get("lang"),
            status=json_obj["status"],
            sysadmin=sysadmin,
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
    def _update_permissions_and_groups(cls, json_obj: dict[str, Any]) -> tuple[bool | None, set[str], dict[str, bool]]:
        in_projects: dict[str, bool] = {}
        in_groups: set[str] = set()
        if json_obj.get("permissions") is not None and json_obj["permissions"].get("groupsPerProject") is not None:
            sysadmin = False
            for project_iri, group_memberships in json_obj["permissions"]["groupsPerProject"].items():
                if project_iri == Project.SYSTEM_PROJECT:
                    if Group.PROJECT_SYSTEMADMIN_GROUP in group_memberships:
                        sysadmin = True
                else:
                    for group in group_memberships:
                        if group == Group.PROJECT_MEMBER_GROUP:
                            if in_projects.get(project_iri) is None:
                                in_projects[project_iri] = False
                        elif group == Group.PROJECT_ADMIN_GROUP:
                            in_projects[project_iri] = True
                        else:
                            in_groups.add(group)
            return sysadmin, in_groups, in_projects
        return None, in_groups, in_projects

    def create(self) -> User:
        """
        Create new user in DSP

        :return: JSON-object from DSP
        """
        jsonobj = self._toJosonObj_create()
        result = self._con.post(User.ROUTE, jsonobj)
        iri = result["user"]["id"]
        if self._in_projects is not None:
            for project in self._in_projects:
                result = self._con.post(User.IRI + quote_plus(iri) + User.PROJECT_MEMBERSHIPS + quote_plus(project))
                if self._in_projects[project]:
                    result = self._con.post(
                        User.IRI + quote_plus(iri) + User.PROJECT_ADMIN_MEMBERSHIPS + quote_plus(project)
                    )
        if self._in_groups is not None:
            for group in self._in_groups:
                result = self._con.post(User.IRI + quote_plus(iri) + User.GROUP_MEMBERSHIPS + quote_plus(group))
        return User._make_fromJsonObj(self._con, result["user"])

    def _toJosonObj_create(self):
        tmp = {}
        if self._username is None:
            raise BaseError("There must be a valid username!")
        tmp["username"] = self._username
        if self._email is None:
            raise BaseError("'email' is mandatory!")
        tmp["email"] = self._email
        if self._givenName is None:
            raise BaseError("'givenName is mandatory!")
        tmp["givenName"] = self._givenName
        if self._familyName is None:
            raise BaseError("'familyName' is mandatory!")
        tmp["familyName"] = self._familyName
        if self._password is None:
            raise BaseError("'password' is mandatory!")
        tmp["password"] = self._password
        if self._lang is None:
            raise BaseError("'language' is mandatory!")
        tmp["lang"] = self._lang.value
        tmp["status"] = True if self._status is None else self._status
        tmp["systemAdmin"] = False if self._sysadmin is None else self._sysadmin
        return tmp

    def read(self) -> User:
        """
        Read the user information from DSP. The User object must have a valid iri or email!

        :return: JSON-object from DSP
        """
        if self._iri is not None:
            result = self._con.get(User.IRI + quote_plus(self._iri))
        elif self._email is not None:
            result = self._con.get(User.ROUTE + "/email/" + quote_plus(self._email))
        elif self._username is not None:
            result = self._con.get(User.ROUTE + "/username/" + quote_plus(self._username))
        else:
            raise BaseError("Either user-iri or email is required!")
        return User._make_fromJsonObj(self._con, result["user"])

    @staticmethod
    def getAllUsers(con: Connection) -> list[Any]:
        """
        Get a list of all users (static method)

        :param con: Connection instance
        :return: List of users
        """

        result = con.get(User.ROUTE)
        if "users" not in result:
            raise BaseError("Request got no users!")
        return [User._make_fromJsonObj(con, a) for a in result["users"]]

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
        if self._sysadmin:
            groups.append("SystemAdmin")
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
