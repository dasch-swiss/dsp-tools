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
        return self.keywords


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
    project_member: bool = False
    project_admin: bool = False
    sys_admin: bool = False

    def serialise(self) -> dict[str, Any]:
        usr_dict = {
            "username": self.username,
            "email": self.email,
            "givenName": self.givenName,
            "familyName": self.familyName,
            "password": self.password,
            "lang": self.lang,
            "status": True,
        }
        if self.sys_admin:
            usr_dict["groups"] = ["SystemAdmin"]
            usr_dict["projects"] = [":admin", ":member"]
        elif self.project_member:
            usr_dict["projects"] = [":member"]
        elif self.project_admin:
            usr_dict["projects"] = [":admin", ":member"]
        return usr_dict
