from dataclasses import dataclass
from dataclasses import field
from typing import Protocol
from urllib.parse import quote_plus

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError


@dataclass(frozen=True)
class ProjectInfo:
    """Information about a project."""

    project_iri: str
    ontology_iris: list[str]


class ProjectClient(Protocol):
    """Interface (protocol) for project-related requests to the DSP-API."""

    con: Connection
    shortcode: str
    project_info: ProjectInfo | None

    def get_project_iri(self) -> str:
        """Get the IRI of the project to which the data is being uploaded."""

    def get_ontology_name_dict(self) -> dict[str, str]:
        """Returns a mapping of ontology names to ontology IRIs."""


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

    def get_ontology_name_dict(self) -> dict[str, str]:
        """Returns a mapping of ontology names to ontology IRIs."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.con, self.shortcode)
        onto_dict = {_extract_name_from_onto_iri(iri): iri for iri in self.project_info.ontology_iris}
        onto_dict["knora-api"] = "http://api.knora.org/ontology/knora-api/v2"
        return onto_dict


def _get_project_info_from_server(con: Connection, shortcode: str) -> ProjectInfo:
    project_iri = _get_project_iri_from_server(con, shortcode)
    ontologies = _get_ontologies_from_server(con, project_iri)
    return ProjectInfo(project_iri=project_iri, ontology_iris=ontologies)


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


def _get_ontologies_from_server(con: Connection, project_iri: str) -> list[str]:
    try:
        iri = quote_plus(project_iri)
        url = f"/v2/ontologies/metadata/{iri}"
        res = con.get(url)
        body = res.get("@graph", res)
        match body:
            case list():
                return [o["@id"] for o in body]
            case dict():
                return [body["@id"]]
            case _:
                raise BaseError("Unexpected response from server")
    except BaseError as e:
        raise BaseError(f"Ontologies for project {project_iri} could not be retrieved from the DSP server") from e


def _extract_name_from_onto_iri(iri: str) -> str:
    return iri.split("/")[-2]
