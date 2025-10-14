from typing import Protocol

from rdflib import Graph

from dsp_tools.clients.authentication_client import AuthenticationClient


class OntologyClient(Protocol):
    """
    Protocol class/interface for the ontology endpoint in the API.
    """

    project_shortcode: str
    authentication_client: AuthenticationClient

    def post_resource_cardinalities(self, cardinality_graph: Graph) -> None:
        """Add cardinalities to an existing resource class."""
