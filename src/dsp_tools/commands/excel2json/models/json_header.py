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
    prefixes: Prefixes
    project: Project

    def make(self) -> dict[str, Any]:
        return {
            "prefixes": self.prefixes.get(),
            "$schema": SCHEMA,
            "project": self.project.get(),
        }


@dataclass
class Prefixes:
    prefixes: dict[str, str]

    def get(self) -> dict[str, Any]:
        return {"prefixes": self.prefixes}


@dataclass
class Project:
    shortcode: str
    shortname: str
    longname: str
    descriptions: Descriptions
    keywords: Keywords
    users: Users | None

    def get(self) -> dict[str, Any]:
        proj_dict = {
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

    def get(self) -> dict[str, Any]:
        description = {}
        for desc in self.descriptions:
            description.update(desc.get())
        return {"descriptions": description}


@dataclass
class Description:
    lang: str
    text: str

    def get(self) -> dict[str, str]:
        return {self.lang: self.text}


@dataclass
class Keywords:
    keywords: list[str]

    def get(self) -> dict[str, Any]:
        return {"keywords": self.keywords}


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
    projects: str | None
    groups: str | None

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
        if self.projects:
            usr_dict["projects"] = [self.projects]
        if self.groups:
            usr_dict["groups"] = [self.groups]
        return usr_dict
