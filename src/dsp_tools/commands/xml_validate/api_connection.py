from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Protocol

from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import UserError

@dataclass
class OntologyClientLive:
    """Client handling ontology-related requests to the DSP-API."""

    con:
    shortcode: str
    default_ontology: str

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