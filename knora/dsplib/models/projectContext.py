from typing import Optional

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.group import Group
from knora.dsplib.models.helpers import BaseError
from knora.dsplib.models.project import Project


class ProjectContext:
    """Represents the project context"""

    _projects: list[Project]
    _project_map: dict[str, str]  # dictionary of (project name:project IRI) pairs
    _inv_project_map: dict[str, str]  # dictionary of (project IRI:project name) pairs
    _groups: Optional[list[Group]]
    _group_map: Optional[dict[str, str]]
    _shortcode: Optional[str]
    _project_name: Optional[str]

    def __init__(self, con: Connection, shortcode: Optional[str] = None):
        self._shortcode = shortcode
        self._projects = Project.getAllProjects(con=con)
        self._project_map: dict[str, str] = {x.shortname: x.id for x in self._projects}
        self._inv_project_map: dict[str, str] = {x.id: x.shortname for x in self._projects}
        try:
            self._groups = Group.getAllGroups(con=con)
        except BaseError:
            self._groups = None
        if self._groups:
            self._group_map: dict[str, str] = {self._inv_project_map[x.project] + ':' + x.name: x.id for x in
                                               self._groups}
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
