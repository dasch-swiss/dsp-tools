from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

SCHEMA = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json"


@dataclass
class JsonHeader(Protocol):
    def serialise(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class EmptyJsonHeader(JsonHeader):
    def serialise(self) -> dict[str, Any]:
        return {
            "prefixes": {"": ""},
            "$schema": SCHEMA,
            "project": {
                "shortcode": "",
                "shortname": "",
                "longname": "",
                "descriptions": {"en": ""},
                "keywords": [""],
            },
        }


@dataclass
class FilledJsonHeader(JsonHeader):
    project: Project
    prefixes: Prefixes | None

    def serialise(self) -> dict[str, Any]:
        header_dict: dict[str, Any] = {}
        if self.prefixes:
            header_dict["prefixes"] = self.prefixes.serialise()
        header_dict.update({"$schema": SCHEMA, "project": self.project.serialise()})
        return header_dict


@dataclass
class Prefixes:
    prefixes: dict[str, str]

    def serialise(self) -> dict[str, Any]:
        return self.prefixes


@dataclass
class Project:
    shortcode: str
    shortname: str
    longname: str
    descriptions: Descriptions
    keywords: Keywords
    users: Users | None

    def serialise(self) -> dict[str, Any]:
        proj_dict: dict[str, Any] = {
            "shortcode": self.shortcode,
            "shortname": self.shortname,
            "longname": self.longname,
            "descriptions": self.descriptions.serialise(),
            "keywords": self.keywords.serialise(),
        }
        if self.users:
            proj_dict["users"] = self.users.serialise()
        return proj_dict


@dataclass
class Descriptions:
    descriptions: dict[str, str]

    def serialise(self) -> dict[str, str]:
        return self.descriptions


@dataclass
class Keywords:
    keywords: list[str]

    def serialise(self) -> list[str]:
        return sorted(self.keywords)


@dataclass
class Users:
    users: list[User]

    def serialise(self) -> list[dict[str, Any]]:
        return [x.serialise() for x in self.users]


@dataclass
class User:
    username: str
    email: str
    givenName: str
    familyName: str
    password: str
    lang: str
    role: UserRole

    def serialise(self) -> dict[str, Any]:
        usr_dict = {
            "username": self.username,
            "email": self.email,
            "givenName": self.givenName,
            "familyName": self.familyName,
            "password": self.password,
            "lang": self.lang,
            "status": True,
        } | self.role.serialise()
        return usr_dict


@dataclass
class UserRole:
    project_admin: bool = False
    sys_admin: bool = False

    def serialise(self) -> dict[str, list[str]]:
        if self.sys_admin:
            return {"groups": ["SystemAdmin"], "projects": [":admin", ":member"]}
        elif self.project_admin:
            return {"projects": [":admin", ":member"]}
        else:
            return {"projects": [":member"]}
