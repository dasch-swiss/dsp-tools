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
class EmptyJsonHeader:
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
class ExcelJsonHeader:
    prefixes: Prefixes
    project: Project

    def make(self) -> dict[str, Any]:
        return {
            "prefixes": self.prefixes.get(),
            "$schema": SCHEMA,
            "project": self.project.get(),
        }


@dataclass
class JsonHeaderElement(Protocol):
    def get(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class Prefixes(JsonHeaderElement):
    prefixes: dict[str, str]

    def get(self) -> dict[str, Any]:
        return {"prefixes": self.prefixes}


@dataclass
class Project(JsonHeaderElement):
    shortcode: str
    shortname: str
    longname: str
    descriptions: Descriptions
    keywords: Keywords

    def get(self) -> dict[str, Any]:
        return {
            "shortcode": self.shortcode,
            "shortname": self.shortname,
            "longname": self.longname,
            "descriptions": self.descriptions.get(),
            "keywords": self.keywords.get(),
        }


@dataclass
class Descriptions(JsonHeaderElement):
    descriptions: list[Descriptions]

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
class Keywords(JsonHeaderElement):
    keywords: list[str]

    def get(self) -> dict[str, Any]:
        return {"keywords": self.keywords}


@dataclass
class Users(JsonHeaderElement):
    users: list[User]

    def get(self) -> dict[str, Any]:
        return {"users": [x.get() for x in self.users]}


@dataclass
class User:
    username: str
    email: str
    givenName: str
    familyName: str
    password: str
    lang: str
    groups: str
    projects: str

    def get(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "email": self.email,
            "givenName": self.givenName,
            "familyName": self.familyName,
            "password": self.password,
            "lang": self.lang,
            "groups": [self.groups],
            "projects": [self.projects],
        }
