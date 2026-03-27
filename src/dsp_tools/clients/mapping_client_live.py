from dataclasses import dataclass
from http import HTTPStatus
from urllib.parse import quote_plus

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.exceptions import InvalidInputError
from dsp_tools.clients.mapping_client import MappingClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT_60 = 60


@dataclass
class MappingClientLive(MappingClient):
    server: str
    encoded_ontology_iri: str
    auth: AuthenticationClient

    def add_class_mapping(self, class_iri: str, mapping_iris: list[str]) -> str | ResponseCodeAndText:
        encoded_class = quote_plus(class_iri)
        url = f"{self.server}/v3/ontologies/{self.encoded_ontology_iri}/classes/{encoded_class}/mapping"
        return self._put(url, class_iri, mapping_iris)

    def add_property_mapping(self, property_iri: str, mapping_iris: list[str]) -> str | ResponseCodeAndText:
        encoded_prop = quote_plus(property_iri)
        url = f"{self.server}/v3/ontologies/{self.encoded_ontology_iri}/properties/{encoded_prop}/mapping"
        return self._put(url, property_iri, mapping_iris)

    def _put(self, url: str, entity_iri: str, external_iris: list[str]) -> str | ResponseCodeAndText:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        params = RequestParameters("PUT", url, TIMEOUT_60, {"mappings": external_iris}, headers)
        log_request(params)
        try:
            response = requests.put(
                url=params.url,
                headers=params.headers,
                data=params.data_serialized,
                timeout=params.timeout,
            )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        # TODO: find out what happens when it does not exist
        match response.status_code:
            case HTTPStatus.OK | HTTPStatus.NO_CONTENT:
                return entity_iri
            case HTTPStatus.BAD_REQUEST:
                raise InvalidInputError(
                    f"The API rejected the mapping for '{entity_iri}' as invalid input (HTTP 400): {response.text}"
                )
            case HTTPStatus.FORBIDDEN:
                raise BadCredentialsError(
                    "You do not have permission to add mappings to this project. "
                    "Only a SystemAdmin or ProjectAdmin can perform this action."
                )
            case _:
                return ResponseCodeAndText(response.status_code, response.text)
