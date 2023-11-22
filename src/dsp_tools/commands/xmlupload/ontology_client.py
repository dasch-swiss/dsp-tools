from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import OntoInfo
from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

# pylint: disable=too-few-public-methods

logger = get_logger(__name__)


@dataclass
class OntologyClient(Protocol):
    """Interface (protocol) for ontology-related requests to the DSP-API."""

    con: Connection
    shortcode: str
    default_ontology: str
    save_location: Path
    ontology_names: list[str] = field(default_factory=list)

    def get_all_ontologies_from_server(self) -> dict[str, OntoInfo]:
        """Get all the ontologies for a project and the knora-api ontology from the server."""


@dataclass
class OntologyClientLive:
    """Client handling ontology-related requests to the DSP-API."""

    con: Connection
    shortcode: str
    default_ontology: str
    save_location: Path
    ontology_names: list[str] = field(default_factory=list)

    def get_all_ontologies_from_server(self) -> dict[str, OntoInfo]:
        """
        This function returns all the project ontologies plus the knora-api ontology that are on the server.

        Returns:
            a dictionary with the ontology name as key and the ontology as value.
        """
        ontologies = self._get_all_ontology_jsons_from_server()
        return {onto_name: deserialize_ontology(onto_graph) for onto_name, onto_graph in ontologies.items()}

    def _get_all_ontology_jsons_from_server(self) -> dict[str, list[dict[str, Any]]]:
        self._get_ontology_names_from_server()
        project_ontos = {onto: self._get_ontology_from_server(onto) for onto in self.ontology_names}
        project_ontos["knora-api"] = self._get_knora_api_ontology_from_server()
        return project_ontos

    def _get_ontology_names_from_server(self) -> None:
        try:
            url = f"/admin/projects/shortcode/{self.shortcode}"
            res: dict[str, Any] = try_network_action(self.con.get, route=url)
        except BaseError as e:
            raise UserError(f"A project with shortcode {self.shortcode} could not be found on the DSP server") from e
        try:
            onto_iris: list[str] = res["project"]["ontologies"]
        except KeyError as e:
            raise BaseError(f"Unexpected response from server: {res}") from e
        onto_names: list[str] = [iri.split("/")[-1] for iri in onto_iris]
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

    def _get_knora_api_ontology_from_server(self) -> list[dict[str, Any]]:
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


def deserialize_ontology(onto_graph: list[dict[str, Any]]) -> OntoInfo:
    """
    This function takes an ontology graph from the DSP-API.
    It extracts the classes and properties.
    And saves them in an instance of the class Ontology.

    Args:
        onto_graph: graph from DSP-API

    Returns:
        Ontology instance with the classes and properties
    """
    classes = _get_all_cleaned_classes_from_graph(onto_graph)
    properties = _get_all_cleaned_properties_from_graph(onto_graph)
    return OntoInfo(classes, properties)


def _get_all_cleaned_classes_from_graph(onto_graph: list[dict[str, Any]]) -> list[str]:
    classes = _get_all_classes_from_graph(onto_graph)
    return _remove_prefixes(classes)


def _get_all_classes_from_graph(onto_graph: list[dict[str, Any]]) -> list[str]:
    return [elem["@id"] for elem in onto_graph if elem.get("knora-api:isResourceClass")]


def _get_all_cleaned_properties_from_graph(onto_graph: list[dict[str, Any]]) -> list[str]:
    props = _get_all_properties_from_graph(onto_graph)
    return _remove_prefixes(props)


def _get_all_properties_from_graph(onto_graph: list[dict[str, Any]]) -> list[str]:
    return [elem["@id"] for elem in onto_graph if not elem.get("knora-api:isResourceClass")]


def _remove_prefixes(ontology_elements: list[str]) -> list[str]:
    return [x.split(":")[1] for x in ontology_elements]
