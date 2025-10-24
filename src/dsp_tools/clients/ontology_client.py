from typing import Any
from typing import Protocol

from rdflib import Literal

from dsp_tools.clients.authentication_client import AuthenticationClient


class OntologyClient(Protocol):
    """
    Protocol class/interface for the ontology endpoint in the API.
    """

    server: str
    authentication_client: AuthenticationClient

    def get_last_modification_date(self, project_iri: str, onto_iri: str) -> str:
        """Get the last modification date of an ontology"""

    def post_resource_cardinalities(self, cardinality_graph: dict[str, Any]) -> Literal | None:
        """Add cardinalities to an existing resource class."""
