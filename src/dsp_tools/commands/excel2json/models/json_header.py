from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

SCHEMA = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json"


@dataclass
class JsonHeader(Protocol):
    def make(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class EmptyJsonHeader(JsonHeader):
    def make(self) -> dict[str, Any]:
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
class ExcelJsonHeader(JsonHeader):
    project: Project
    prefixes: Prefixes | None

    def make(self) -> dict[str, Any]:
        header_dict: dict[str, Any] = {}
        if self.prefixes:
            header_dict["prefixes"] = self.prefixes.get()
        header_dict.update({"$schema": SCHEMA, "project": self.project.get()})
        return header_dict


@dataclass
class Prefixes:
    prefixes: dict[str, str]

    def get(self) -> dict[str, Any]:
        return self.prefixes


@dataclass
class Project:
    shortcode: str
    shortname: str
    longname: str
    descriptions: Descriptions
    keywords: Keywords
    users: Users | None

    def get(self) -> dict[str, Any]:
        proj_dict: dict[str, Any] = {
            "shortcode": self.shortcode,
            "shortname": self.shortname,
            "longname": self.longname,
            "descriptions": self.descriptions.get(),
            "keywords": self.keywords.get(),
        }
        if self.users:
            proj_dict["users"] = self.users.get()
        return proj_dict


@dataclass
class Descriptions:
    descriptions: list[Description]

    def get(self) -> dict[str, str]:
        return {x.lang: x.text for x in self.descriptions}


@dataclass
class Description:
    lang: str
    text: str


@dataclass
class Keywords:
    keywords: list[str]

    def get(self) -> list[str]:
        return self.keywords


@dataclass
class Users:
    users: list[User]

    def get(self) -> list[dict[str, Any]]:
        return [x.get() for x in self.users]


@dataclass
class User:
    username: str
    email: str
    givenName: str
    familyName: str
    password: str
    lang: str
    member: bool = False
    admin: bool = False
    sys_admin: bool = False

    def get(self) -> dict[str, Any]:
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
        elif self.member:
            usr_dict["projects"] = [":member"]
            return usr_dict
        elif self.admin:
            usr_dict["projects"] = [":admin", ":member"]
        return usr_dict
