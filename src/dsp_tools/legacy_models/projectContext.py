"""
TECHNICAL DEBT: This module depends on legacy models (get_all_projects,
get_all_groups) from commands/get/legacy_models/. These should be refactored
to use modern client patterns instead of the legacy model classes.
"""

from dataclasses import dataclass

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.group import get_all_groups
from dsp_tools.commands.get.legacy_models.project import get_all_projects
from dsp_tools.error.exceptions import BaseError


@dataclass(frozen=True)
class ProjectContext:
    """Contains project context information for XML upload."""

    group_map: dict[str, str]
    project_name: str | None


def create_project_context(con: Connection, shortcode: str) -> ProjectContext:
    projects = get_all_projects(con=con)
    inv_project_map: dict[str, str] = {x.iri: x.shortname for x in projects}
    try:
        groups = get_all_groups(con=con)
    except BaseError:
        groups = []
    if groups:
        group_map = {f"{inv_project_map[x.project]}:{x.name}": x.iri for x in groups}
    else:
        group_map = {}
    project_name = None
    for p in projects:
        if p.shortcode == shortcode:
            project_name = p.shortname
            break
    return ProjectContext(group_map=group_map, project_name=project_name)
