from typing import Any
from typing import Protocol

from rdflib import Literal

from dsp_tools.clients.authentication_client import AuthenticationClient


class OntologyCreateClient(Protocol):
    """
    Protocol class/interface to create / update the ontology through the API.
    """

    server: str
    authentication_client: AuthenticationClient

    def get_last_modification_date(self, project_iri: str, onto_iri: str) -> str:
        """Get the last modification date of an ontology"""

    def post_resource_cardinalities(self, cardinality_graph: dict[str, Any]) -> Literal | None:
        """Add cardinalities to an existing resource class."""


class OntologyGetClient(Protocol):
    """
    Protocol class/interface to get ontologies from the API.
    """

    api_url: str
    shortcode: str

    def get_knora_api(self) -> str:
        """Get the knora-api ontology."""

    def get_ontologies(self) -> tuple[list[str], list[str]]:
        """Get all project ontologies."""
