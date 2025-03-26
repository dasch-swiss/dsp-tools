from typing import Optional

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.project.legacy_models.group import Group
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.error.exceptions import BaseError


class ProjectContext:
    """Represents the project context"""

    _projects: list[Project]
    _inv_project_map: dict[str, str]  # dictionary of (project IRI:project name) pairs
    _groups: Optional[list[Group]]
    _group_map: Optional[dict[str, str]]
    _shortcode: Optional[str]
    _project_name: Optional[str]

    def __init__(self, con: Connection, shortcode: Optional[str] = None):
        self._shortcode = shortcode
        self._projects = Project.getAllProjects(con=con)
        self._inv_project_map: dict[str, str] = {x.iri: x.shortname for x in self._projects}
        try:
            self._groups = Group.getAllGroups(con=con)
        except BaseError:
            self._groups = None
        if self._groups:
            self._group_map: dict[str, str] = {
                f"{self._inv_project_map[x.project]}:{x.name}": x.iri for x in self._groups
            }
        else:
            self._group_map = None
        self._project_name = None
        # get the project name from the shortcode
        if self._shortcode:
            for p in self._projects:
                if p.shortcode == self._shortcode:
                    self._project_name = p.shortname
                    break

    @property
    def group_map(self) -> dict[str, str]:
        """Dictionary of (project:group name) and (group id) pairs of all groups in project"""
        return self._group_map

    @property
    def project_name(self) -> Optional[str]:
        """Name of the project"""
        return self._project_name
