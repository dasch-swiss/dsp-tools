"""
This module implements reading DSP projects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString
from dsp_tools.legacy_models.langstring import create_lang_string
from dsp_tools.legacy_models.langstring import create_lang_string_from_json

PROJECTS_ROUTE = "/admin/projects"
PROJECTS_IRI_ROUTE = PROJECTS_ROUTE + "/iri/"


@dataclass(frozen=True)
class Project:
    """Represents a DSP project."""

    iri: str
    shortcode: str
    shortname: str
    longname: str
    description: LangString
    keywords: frozenset[str]
    enabled_licenses: frozenset[str]

    def to_definition_file_obj(self) -> dict[str, Any]:
        return {
            "shortcode": self.shortcode,
            "shortname": self.shortname,
            "longname": self.longname,
            "descriptions": self.description.to_definition_file_obj(),
            "keywords": list(self.keywords),
            "enabled_licenses": list(self.enabled_licenses),
        }


def create_project_from_json(json_obj: dict[str, Any]) -> Project:
    """Create a Project from a JSON object returned by DSP API."""
    iri = json_obj.get("id")
    if iri is None:
        raise BaseError("Project iri is missing")
    shortcode = json_obj.get("shortcode")
    if shortcode is None:
        raise BaseError("Shortcode is missing")
    shortname = json_obj.get("shortname")
    if shortname is None:
        raise BaseError("Shortname is missing")
    longname = json_obj.get("longname")
    if longname is None:
        raise BaseError("Longname is missing")
    description = create_lang_string_from_json(json_obj.get("description")) or create_lang_string()
    keywords = frozenset(json_obj.get("keywords", []))
    enabled_licenses = frozenset(json_obj.get("enabledLicenses", []))
    return Project(
        iri=iri,
        shortcode=shortcode,
        shortname=shortname,
        longname=longname,
        description=description,
        keywords=keywords,
        enabled_licenses=enabled_licenses,
    )


def read_project_by_iri(con: Connection, iri: str) -> Project:
    """Read a project from DSP by its IRI."""
    result = con.get(PROJECTS_IRI_ROUTE + quote_plus(iri))
    return create_project_from_json(result["project"])


def read_project_by_shortcode(con: Connection, shortcode: str) -> Project:
    """Read a project from DSP by its shortcode."""
    result = con.get(PROJECTS_ROUTE + "/shortcode/" + quote_plus(shortcode))
    return create_project_from_json(result["project"])


def read_project_by_shortname(con: Connection, shortname: str) -> Project:
    """Read a project from DSP by its shortname."""
    result = con.get(PROJECTS_ROUTE + "/shortname/" + quote_plus(shortname))
    return create_project_from_json(result["project"])


def get_all_projects(con: Connection) -> list[Project]:
    """Get all existing projects in DSP."""
    try:
        result = con.get(PROJECTS_ROUTE)
        return [create_project_from_json(a) for a in result["projects"]]
    except BaseError:
        return []
