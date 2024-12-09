from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Protocol

from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.connection import Connection


@dataclass
class OntologyClient(Protocol):
    """Interface (protocol) for ontology-related requests to the DSP-API."""

    con: Connection
    shortcode: str
    default_ontology: str
    ontology_names: list[str] = field(default_factory=list)

    def get_all_project_ontologies_from_server(self) -> dict[str, list[dict[str, Any]]]:
        """Get all the ontologies for a project from the server."""

    def get_knora_api_ontology_from_server(self) -> list[dict[str, Any]]:
        """Get the knora-api ontology from the server."""


@dataclass
class OntologyClientLive:
    """Client handling ontology-related requests to the DSP-API."""

    con: Connection
    shortcode: str
    default_ontology: str
    ontology_names: list[str] = field(default_factory=list)

    def get_all_project_ontologies_from_server(self) -> dict[str, list[dict[str, Any]]]:
        """
        This function returns all the project ontologies that are on the server.

        Returns:
            a dictionary with the ontology name as key and the ontology as value.
        """
        self._get_ontology_names_from_server()
        return {onto: self._get_ontology_from_server(onto) for onto in self.ontology_names}

    def _get_ontology_names_from_server(self) -> None:
        try:
            url = f"/admin/projects/shortcode/{self.shortcode}"
            res = self.con.get(url)
        except BaseError as e:
            raise UserError(f"A project with shortcode {self.shortcode} could not be found on the DSP server") from e
        try:
            onto_iris: list[str] = res["project"]["ontologies"]
        except KeyError as e:
            raise BaseError(f"Unexpected response from server: {res}") from e
        onto_names: list[str] = [iri.split("/")[-2] for iri in onto_iris]
        self.ontology_names = onto_names

    def _get_ontology_from_server(self, ontology_name: str) -> list[dict[str, Any]]:
        try:
            url = f"/ontology/{self.shortcode}/{ontology_name}/v2"
            res = self.con.get(url)
        except BaseError:
            raise BaseError(
                f"Ontologies for project {self.shortcode} could not be retrieved from the DSP server"
            ) from None
        try:
            onto_graph: list[dict[str, Any]] = res["@graph"]
        except KeyError as e:
            raise BaseError(f"Unexpected response from server: {res}") from e
        return onto_graph

    def get_knora_api_ontology_from_server(self) -> list[dict[str, Any]]:
        """
        This function returns the knora-api ontology from the server.

        Returns:
            knora-api ontology in json format

        Raises:
            BaseError: if an unexpected response from the server occurred
        """
        url = "/ontology/knora-api/v2#"
        try:
            res = self.con.get(url)
        except BaseError:
            raise BaseError("Knora-api ontology could not be retrieved from the DSP server") from None
        try:
            onto_graph: list[dict[str, Any]] = res["@graph"]
        except KeyError as e:
            raise BaseError(f"Unexpected response from server when retrieving knora-api ontology: {res}") from e
        return onto_graph
