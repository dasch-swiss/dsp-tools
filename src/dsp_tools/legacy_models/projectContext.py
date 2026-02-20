from dataclasses import dataclass
from typing import Any

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError


@dataclass(frozen=True)
class ProjectContext:
    """Contains project context information for XML upload."""

    group_map: dict[str, str]
    project_name: str | None


def create_project_context(con: Connection, shortcode: str) -> ProjectContext:
    projects: list[dict[str, Any]] = con.get("/admin/projects")["projects"]
    project_iri_to_shortname: dict[str, str] = {p["id"]: p["shortname"] for p in projects}
    try:
        groups: list[dict[str, Any]] = con.get("/admin/groups")["groups"]
        group_map = {f"{project_iri_to_shortname[g['project']['id']]}:{g['name']}": g["id"] for g in groups}
    except BaseError:
        group_map = {}
    project_name = next((p["shortname"] for p in projects if p["shortcode"] == shortcode), None)
    return ProjectContext(group_map=group_map, project_name=project_name)
