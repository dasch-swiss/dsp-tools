from typing import Any

import requests
from rdflib import Graph
from rdflib import Literal
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.ontology_client import OntologyClient
from dsp_tools.utils.rdflib_utils import serialise_json
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 60

HTTP_LACKING_PERMISSIONS = 403


class OntologyClientLive(OntologyClient):
    """
    Protocol class/interface for the ontology endpoint in the API.
    """

    server: str
    project_shortcode: str
    authentication_client: AuthenticationClient

    def post_resource_cardinalities(self, cardinality_graph: Graph) -> Literal:
        url = f"{self.authentication_client.server}/v2/ontologies/cardinalities"
        serialised = serialise_json(cardinality_graph)
        response = self._post_and_log_request(url, serialised)
        if not response.ok:
            pass  # TODO implement

    def _post_and_log_request(self, url: str, data: list[dict[str, Any]] | dict[str, Any]) -> Response:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        params = RequestParameters("POST", url, TIMEOUT, {"data": data}, headers)
        log_request(params)
        response = requests.post(
            url=params.url,
            headers=params.headers,
            data=params.data_serialized,
            timeout=params.timeout,
        )
        log_response(response)
        return response
