
from rdflib import Graph
from rdflib import Literal

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.ontology_client import OntologyClient


class OntologyClientLive(OntologyClient):
    """
    Protocol class/interface for the ontology endpoint in the API.
    """

    project_shortcode: str
    authentication_client: AuthenticationClient

    def post_resource_cardinalities(self, cardinality_graph: Graph) -> Literal:
        """Add cardinalities to an existing resource class."""
