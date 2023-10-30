from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import quote_plus

import requests
from requests import Response

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.shared import try_network_action


@dataclass(frozen=True)
class ProjectInfo:
    """Information about a project."""

    project_iri: str
    ontologies: list[str]


class ProjectClient(Protocol):
    """Interface (protocol) for project-related requests to the DSP-API."""

    def get_project_iri(self) -> str:
        """Get the IRI of the project to which the data is being uploaded."""

    def get_ontologies(self) -> list[tuple[str, str]]:
        """Get the ontology IRIs and names of the project to which the data is being uploaded."""


@dataclass()
class ProjectClientLive:
    """Client handling project-related requests to the DSP-API."""

    server: str
    shortcode: str
    project_info: ProjectInfo | None = field(init=False, default=None)

    def get_project_iri(self) -> str:
        """Get the IRI of the project to which the data is being uploaded."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.server, self.shortcode)
        return self.project_info.project_iri

    def get_ontologies(self) -> list[str]:
        """Get the ontology IRIs and names of the project to which the data is being uploaded."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.server, self.shortcode)
        return self.project_info.ontologies

    def get_ontology_name_dict(self) -> dict[str, str]:
        """Returns a mapping of ontology names to ontology IRIs."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.server, self.shortcode)
        return {_extract_name_from_iri(iri): iri for iri in self.project_info.ontologies}

    def get_ontology_iri_dict(self) -> dict[str, str]:
        """Returns a mapping of ontology IRIs to ontology names."""
        if not self.project_info:
            self.project_info = _get_project_info_from_server(self.server, self.server)
        return {iri: _extract_name_from_iri(iri) for iri in self.project_info.ontologies}


def _get_project_info_from_server(server: str, shortcode: str) -> ProjectInfo:
    project_iri = _get_project_iri_from_server(server, shortcode)
    ontologies = _get_ontologies_from_server(server, project_iri)
    return ProjectInfo(project_iri=project_iri, ontologies=ontologies)


def _get_project_iri_from_server(server: str, shortcode: str) -> str:
    url = f"{server}/admin/projects/shortcode/{shortcode}"
    res: Response = try_network_action(requests.get, url=url, timeout=5)
    if res.status_code != 200:
        raise UserError(f"A project with shortcode {shortcode} could not be found on the DSP server")
    iri: str = res.json()["project"]["id"]
    return iri


def _get_ontologies_from_server(server: str, project_iri: str) -> list[str]:
    url = f"{server}/v2/ontologies/metadata/{quote_plus(project_iri)}"
    res: Response = try_network_action(requests.get, url=url, timeout=5)
    if res.status_code != 200:
        raise UserError(f"No ontology found for project {project_iri}")
    graph: list[dict[str, Any]] | dict[str, Any] = res.json()["@graph"]
    if isinstance(graph, dict):
        graph = [graph]
    return [o["@id"] for o in graph]


def _extract_name_from_iri(iri: str) -> str:
    return iri.split("/")[-2]
