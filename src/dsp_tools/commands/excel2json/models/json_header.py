from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

SCHEMA = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json"


@dataclass
class JsonHeader(Protocol):
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class EmptyJsonHeader(JsonHeader):
    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
        header_dict: dict[str, Any] = {}
        if self.prefixes:
            header_dict["prefixes"] = self.prefixes.to_dict()
        header_dict.update({"$schema": SCHEMA, "project": self.project.to_dict()})
        return header_dict


@dataclass
class Prefixes:
    prefixes: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return self.prefixes


@dataclass
class Project:
    shortcode: str
    shortname: str
    longname: str
    descriptions: Descriptions
    keywords: Keywords
    users: Users | None

    def to_dict(self) -> dict[str, Any]:
        proj_dict: dict[str, Any] = {
            "shortcode": self.shortcode,
            "shortname": self.shortname,
            "longname": self.longname,
            "descriptions": self.descriptions.to_dict(),
            "keywords": self.keywords.to_dict(),
        }
        if self.users:
            proj_dict["users"] = self.users.to_dict()
        return proj_dict


@dataclass
class Descriptions:
    descriptions: dict[str, str]

    def __post_init__(self) -> None:
        for k, v in self.descriptions.items():
            self.descriptions[k] = v.replace("\n", "<br/>")

    def to_dict(self) -> dict[str, str]:
        return self.descriptions


@dataclass
class Keywords:
    keywords: list[str]

    def to_dict(self) -> list[str]:
        return sorted(self.keywords)


@dataclass
class Users:
    users: list[User]

    def to_dict(self) -> list[dict[str, Any]]:
        return [x.to_dict() for x in self.users]


@dataclass
class User:
    username: str
    email: str
    givenName: str
    familyName: str
    password: str
    lang: str
    role: UserRole

    def to_dict(self) -> dict[str, Any]:
        usr_dict = {
            "username": self.username,
            "email": self.email,
            "givenName": self.givenName,
            "familyName": self.familyName,
            "password": self.password,
            "lang": self.lang,
            "status": True,
        } | self.role.to_dict()
        return usr_dict


@dataclass
class UserRole:
    project_admin: bool = False
    sys_admin: bool = False

    def to_dict(self) -> dict[str, list[str]]:
        if self.sys_admin:
            return {"groups": ["SystemAdmin"], "projects": [":admin", ":member"]}
        elif self.project_admin:
            return {"projects": [":admin", ":member"]}
        else:
            return {"projects": [":member"]}
