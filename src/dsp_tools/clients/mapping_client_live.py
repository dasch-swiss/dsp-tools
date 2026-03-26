from dataclasses import dataclass
from http import HTTPStatus
from urllib.parse import quote

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
    auth: AuthenticationClient

    def add_class_mapping(
        self, ontology_iri: str, class_iri: str, external_iris: list[str]
    ) -> str | ResponseCodeAndText:
        encoded_onto = quote(ontology_iri, safe="")
        encoded_class = quote(class_iri, safe="")
        url = f"{self.server}/v3/ontologies/{encoded_onto}/classes/{encoded_class}/mapping"
        return self._put(url, external_iris, class_iri)

    def add_property_mapping(
        self, ontology_iri: str, property_iri: str, external_iris: list[str]
    ) -> str | ResponseCodeAndText:
        encoded_onto = quote(ontology_iri, safe="")
        encoded_prop = quote(property_iri, safe="")
        url = f"{self.server}/v3/ontologies/{encoded_onto}/properties/{encoded_prop}/mapping"
        return self._put(url, external_iris, property_iri)

    def _put(self, url: str, external_iris: list[str], entity_iri: str) -> str | ResponseCodeAndText:
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
