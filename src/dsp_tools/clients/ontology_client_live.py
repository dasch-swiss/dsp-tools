from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

import requests
from loguru import logger
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from requests import ReadTimeout
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.ontology_client import OntologyClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InternalError
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_utils import serialise_json
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_timeouts
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 60


@dataclass
class OntologyClientLive(OntologyClient):
    """
    Client for the ontology endpoint in the API.
    """

    server: str
    project_shortcode: str
    authentication_client: AuthenticationClient

    def get_last_modification_date(self, project_iri: str, onto_iri: str) -> Literal:
        url = f"{self.server}/v2/ontologies/metadata"
        header = {"X-Knora-Accept-Project": project_iri}
        logger.debug("GET ontology metadata")
        try:
            response = self._post_and_log_request(url, {}, header)
        except (TimeoutError, ReadTimeout) as err:
            log_and_raise_timeouts(err)
        if response.ok:
            date = _parse_last_modification_date(response.text, URIRef(onto_iri))
            if not date:
                raise InternalError(
                    f"Could not find the last modification date of the ontology '{onto_iri}' "
                    f"in the response: {response.text}"
                )
            return date
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You do not have sufficient credentials to retrieve ontology metadata.")
        else:
            raise BaseError(
                f"An unexpected response with the status code {response.status_code} was received from the API. "
                f"Please consult 'warnings.log' for details."
            )

    def post_resource_cardinalities(self, cardinality_graph: Graph) -> Literal | None:
        url = f"{self.server}/v2/ontologies/cardinalities"
        serialised = serialise_json(cardinality_graph)
        logger.debug("POST resource cardinalities to ontology")
        try:
            response = self._post_and_log_request(url, serialised)
        except (TimeoutError, ReadTimeout) as err:
            log_and_raise_timeouts(err)
        if response.ok:
            return _parse_last_modification_date(response.text)
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a project or system administrator can add cardinalities to resource classes. "
                "Your permissions are insufficient for this action."
            )
        else:
            raise BaseError(
                f"An unexpected response with the status code {response.status_code} was received from the API. "
                f"Please consult 'warnings.log' for details."
            )

    def _post_and_log_request(
        self, url: str, data: list[dict[str, Any]] | dict[str, Any] | None, headers: dict[str, str] | None = None
    ) -> Response:
        generic_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        data_dict = {"data": data} if data else None
        if headers:
            generic_headers.update(headers)
        params = RequestParameters("POST", url, TIMEOUT, data_dict, generic_headers)
        log_request(params)
        response = requests.post(
            url=params.url,
            headers=params.headers,
            data=params.data_serialized,
            timeout=params.timeout,
        )
        log_response(response)
        return response


def _parse_last_modification_date(response_text: str, onto_iri: URIRef | None = None) -> Literal | None:
    g = Graph()
    g.parse(data=response_text, format="json-ld")
    result = next(g.objects(subject=onto_iri, predicate=KNORA_API.lastModificationDate), None)
    if isinstance(result, Literal):
        return result
    return None
