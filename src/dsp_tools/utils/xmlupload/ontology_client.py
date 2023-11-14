from dataclasses import dataclass, field
from typing import Any, Protocol

from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


@dataclass
class Ontology:
    """This class saves the properties and the classes from an ontology."""

    ontology_name: str | None = None
    classes: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)
    is_default_onto: bool = False


class OntologyClient(Protocol):
    """Interface (protocol) for ontology-related requests to the DSP-API."""

    def get_ontology_iris(self) -> list[str]:
        """Get the ontology IRIs of the project to which the data is being uploaded."""

    def get_ontology_names_from_server(self) -> list[str]:
        """Returns the names of the project ontologies on the server."""

    def get_ontology_from_server(self) -> dict[str, Any]:
        """Returns the response from the server."""


@dataclass()
class OntologyClientLive:
    """Client handling ontology-related requests to the DSP-API."""

    con: ConnectionLive
    shortcode: str
    ontology_names: list[str] = field(default_factory=list)

    def get_all_ontologies_from_server(self) -> dict[str, Ontology]:
        """
        This function retrieves all ontologies from a project plus the knora-api ontology from a server.
        As the base ontology knora-api is saved in the dictionary with an empty string.

        Returns:
            Dictionary with the ontology names and an instance of Ontology.
        """
        self._get_ontology_names_from_server()
        project_ontos = dict()
        for onto in self.ontology_names:
            project_ontos[onto] = self.get_ontology(onto)
        project_ontos[""] = self._get_knora_api()
        return project_ontos

    def get_ontology(self, ontology_name: str) -> Ontology:
        """
        This function retrieves one ontology from a server based on its name.

        Args:
            ontology_name: name of the ontology

        Returns:
            The ontology saved as an instance of Ontology.
        """
        onto_graph = self._get_ontology_from_server(ontology_name)
        project_onto = self._format_ontology(onto_graph)
        return project_onto

    def _get_ontology_names_from_server(self) -> None:
        try:
            url = f"/admin/projects/shortcode/{self.shortcode}"
            res: dict[str, Any] = try_network_action(self.con.get, route=url)
        except BaseError as e:
            raise UserError(f"A project with shortcode {self.shortcode} could not be found on the DSP server") from e
        try:
            onto_iri: list[str] = res["project"]["ontologies"]
        except KeyError as e:
            raise BaseError(f"Unexpected response from server: {res}") from e
        onto_names: list[str] = [iri.split("/")[-2] for iri in onto_iri]
        self.ontology_names = onto_names

    def _get_ontology_from_server(self, ontology_name: str) -> list[dict[str, Any]]:
        try:
            url = f"/ontology/{self.shortcode}/{ontology_name}/v2"
            res: dict[str, Any] = try_network_action(self.con.get, route=url)
        except BaseError:
            raise BaseError(
                f"Ontologies for project {self.shortcode} could not be retrieved from the DSP server"
            ) from None
        try:
            onto_graph: list[dict[str, Any]] = res["@graph"]
        except KeyError as e:
            raise BaseError(f"Unexpected response from server: {res}") from e
        return onto_graph

    def _get_knora_api(self) -> Ontology:
        knora_graph = self._get_knora_api_from_server()
        knora_api = self._format_ontology(knora_graph)
        return knora_api

    def _get_knora_api_from_server(self) -> list[dict[str, Any]]:
        url = "/ontology/knora-api/v2#"
        try:
            res: dict[str, Any] = try_network_action(self.con.get, route=url)
        except BaseError:
            raise BaseError("Knora-api ontology could not be retrieved from the DSP server") from None
        try:
            onto_graph: list[dict[str, Any]] = res["@graph"]
        except KeyError as e:
            raise BaseError(f"Unexpected response from server when retrieving knora-api ontology: {res}") from e
        return onto_graph

    @staticmethod
    def _format_ontology(onto_graph: list[dict[str, Any]]) -> Ontology:
        onto = Ontology()
        for ele in onto_graph:
            if ele.get("knora-api:isResourceClass"):
                onto.classes.append(ele["@id"])
            else:
                onto.properties.append(ele["id"])
        return onto


def get_project_and_knora_ontology_from_server(con: ConnectionLive, project_shortcode: str) -> dict[str, Ontology]:
    """
    This function takes a connection to the server and the shortcode of a project.
    It retrieves the project ontologies and the knora-api ontology.
    Knora-api is saved with an empty string as key.

    Args:
        con: connection to the server
        project_shortcode: shortcode of the project

    Returns:
        Dictionary with the ontology names as keys and the ontology in a structured manner as values.
    """
    client = OntologyClientLive(con, project_shortcode)
    ontologies = client.get_all_ontologies_from_server()
    return ontologies
