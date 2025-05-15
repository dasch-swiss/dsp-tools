from dataclasses import dataclass
from dataclasses import field
from typing import Protocol

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError


@dataclass(frozen=True)
class ProjectInfo:
    """Information about a project."""

    project_iri: str


class ProjectClient(Protocol):
    """Interface (protocol) for project-related requests to the DSP-API."""

    con: Connection
    shortcode: str
    project_info: ProjectInfo | None

    def get_project_iri(self) -> str:
        """Get the IRI of the project to which the data is being uploaded."""


@dataclass()
class ProjectClientLive:
    """Client handling project-related requests to the DSP-API."""

    con: Connection
    shortcode: str
    project_info: ProjectInfo | None = field(init=False, default=None)

    def get_project_iri(self) -> str:
        """Get the IRI of the project to which the data is being uploaded."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.con, self.shortcode)
        return self.project_info.project_iri


def _get_project_info_from_server(con: Connection, shortcode: str) -> ProjectInfo:
    project_iri = _get_project_iri_from_server(con, shortcode)
    return ProjectInfo(project_iri=project_iri)


def _get_project_iri_from_server(con: Connection, shortcode: str) -> str:
    url = f"/admin/projects/shortcode/{shortcode}"
    try:
        res = con.get(url)
    except BaseError as e:
        raise InputError(f"A project with shortcode {shortcode} could not be found on the DSP server") from e

    iri: str | None = res.get("project", {}).get("id")
    if not iri:
        raise BaseError(f"Unexpected response from server: {res}")
    return iri
