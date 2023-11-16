from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import quote_plus

from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


@dataclass(frozen=True)
class ProjectInfo:
    """Information about a project."""

    project_iri: str
    ontology_iris: list[str]


class ProjectClient(Protocol):
    """Interface (protocol) for project-related requests to the DSP-API."""

    def get_project_iri(self) -> str:
        """Get the IRI of the project to which the data is being uploaded."""

    def get_ontology_iris(self) -> list[str]:
        """Get the ontology IRIs of the project to which the data is being uploaded."""

    def get_ontology_name_dict(self) -> dict[str, str]:
        """Returns a mapping of ontology names to ontology IRIs."""

    def get_ontology_iri_dict(self) -> dict[str, str]:
        """Returns a mapping of ontology IRIs to ontology names."""


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

    def get_ontology_iris(self) -> list[str]:
        """Get the ontology IRIs of the project to which the data is being uploaded."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.con, self.shortcode)
        return self.project_info.ontology_iris

    def get_ontology_name_dict(self) -> dict[str, str]:
        """Returns a mapping of ontology names to ontology IRIs."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.con, self.shortcode)
        return {_extract_name_from_onto_iri(iri): iri for iri in self.project_info.ontology_iris}

    def get_ontology_iri_dict(self) -> dict[str, str]:
        """Returns a mapping of ontology IRIs to ontology names."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.con, self.shortcode)
        return {iri: _extract_name_from_onto_iri(iri) for iri in self.project_info.ontology_iris}


def _get_project_info_from_server(con: Connection, shortcode: str) -> ProjectInfo:
    project_iri = _get_project_iri_from_server(con, shortcode)
    ontologies = _get_ontologies_from_server(con, project_iri)
    return ProjectInfo(project_iri=project_iri, ontology_iris=ontologies)


def _get_project_iri_from_server(con: Connection, shortcode: str) -> str:
    try:
        url = f"/admin/projects/shortcode/{shortcode}"
        res: dict[str, Any] = try_network_action(con.get, route=url)
        iri: str = res["project"]["id"]
    except BaseError as e:
        raise UserError(f"A project with shortcode {shortcode} could not be found on the DSP server") from e
    except KeyError as e:
        raise BaseError(f"Unexpected response from server: {res}") from e
    return iri


def _get_ontologies_from_server(con: Connection, project_iri: str) -> list[str]:
    try:
        iri = quote_plus(project_iri)
        url = f"/v2/ontologies/metadata/{iri}"
        res: dict[str, Any] = try_network_action(con.get, route=url)
        body = res.get("@graph", res)
        match body:
            case list():
                return [o["@id"] for o in body]
            case dict():
                return [body["@id"]]
            case _:
                raise BaseError(f"Unexpected response from server: {body}")
    except BaseError as e:
        logger.exception(e)
        raise BaseError(f"Ontologies for project {project_iri} could not be retrieved from the DSP server") from None


def _extract_name_from_onto_iri(iri: str) -> str:
    return iri.split("/")[-2]
