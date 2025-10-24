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
from dsp_tools.error.exceptions import UnexpectedApiResponseError
from dsp_tools.utils.rdflib_constants import KNORA_API
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
    authentication_client: AuthenticationClient

    def get_last_modification_date(self, project_iri: str, onto_iri: str) -> Literal:
        url = f"{self.server}/v2/ontologies/metadata"
        header = {"X-Knora-Accept-Project": project_iri}
        logger.debug("GET ontology metadata")
        try:
            response = self._get_and_log_request(url, header)
        except (TimeoutError, ReadTimeout) as err:
            log_and_raise_timeouts(err)
        if response.ok:
            date = _parse_last_modification_date(response.text, URIRef(onto_iri))
            if not date:
                raise UnexpectedApiResponseError(
                    f"Could not find the last modification date of the ontology '{onto_iri}' "
                    f"in the response: {response.text}"
                )
            return date
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You do not have sufficient credentials to retrieve ontology metadata.")
        else:
            raise UnexpectedApiResponseError(
                f"An unexpected response with the status code {response.status_code} was received from the API. "
                f"Please consult 'warnings.log' for details."
            )

    def post_resource_cardinalities(self, cardinality_graph: dict[str, Any]) -> Literal | None:
        url = f"{self.server}/v2/ontologies/cardinalities"

        logger.debug("POST resource cardinalities to ontology")
        try:
            response = self._post_and_log_request(url, cardinality_graph)
        except (TimeoutError, ReadTimeout) as err:
            log_and_raise_timeouts(err)
        if response.ok:
            date = _parse_last_modification_date(response.text)
            if not date:
                raise UnexpectedApiResponseError(
                    f"Could not find the last modification date in the response: {response.text}"
                )
            return date
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a project or system administrator can add cardinalities to resource classes. "
                "Your permissions are insufficient for this action."
            )
        else:
            logger.error(
                f"During cardinality creation an unexpected response with the status code {response.status_code} "
                f"was received from the API."
            )
            return None

    def _post_and_log_request(
        self,
        url: str,
        data: dict[str, Any] | None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        data_dict, generic_headers = self._prepare_request(data, headers)
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

    def _get_and_log_request(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> Response:
        _, generic_headers = self._prepare_request({}, headers)
        params = RequestParameters(method="GET", url=url, timeout=TIMEOUT, headers=generic_headers)
        log_request(params)
        response = requests.get(
            url=params.url,
            headers=params.headers,
            timeout=params.timeout,
        )
        log_response(response)
        return response

    def _prepare_request(
        self, data: dict[str, Any] | None, headers: dict[str, str] | None
    ) -> tuple[dict[str, Any] | None, dict[str, str]]:
        generic_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        data_dict = data if data else None
        if headers:
            generic_headers.update(headers)
        return data_dict, generic_headers


def _parse_last_modification_date(response_text: str, onto_iri: URIRef | None = None) -> Literal | None:
    g = Graph()
    g.parse(data=response_text, format="json-ld")
    result = next(g.objects(subject=onto_iri, predicate=KNORA_API.lastModificationDate), None)
    if isinstance(result, Literal):
        return result
    return None
