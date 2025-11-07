from dataclasses import dataclass
from typing import Any
from typing import cast

import requests
from requests import RequestException

from dsp_tools.clients.ontology_clients import OntologyGetClient
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode
from dsp_tools.error.exceptions import ProjectOntologyNotFound
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class OntologyGetClientLive(OntologyGetClient):
    api_url: str
    shortcode: str

    def get_knora_api(self) -> str:
        url = f"{self.api_url}/ontology/knora-api/v2#"
        headers = {"Accept": "text/turtle"}
        timeout = 60
        params = RequestParameters("GET", url, timeout=timeout, headers=headers)
        log_request(params)
        try:
            response = requests.get(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response, include_response_content=False)
        if response.ok:
            return response.text
        raise FatalNonOkApiResponseCode(params.url, response.status_code, response.text)

    def get_ontologies(self) -> tuple[list[str], list[str]]:
        """
        Returns a list of project ontologies as a string in turtle format.
        And a list of the ontology IRIs

        Returns:
            list of ontologies and IRIs
        """
        ontology_iris = self._get_ontology_iris()
        ontologies = [self._get_one_ontology(x) for x in ontology_iris]
        return ontologies, ontology_iris

    def _get_ontology_iris(self) -> list[str]:
        url = f"{self.api_url}/admin/projects/shortcode/{self.shortcode}"
        timeout = 10
        params = RequestParameters("GET", url, timeout=timeout)
        log_request(params)
        try:
            response = requests.get(url=params.url, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if not response.ok:
            raise FatalNonOkApiResponseCode(params.url, response.status_code, response.text)
        response_json = cast(dict[str, Any], response.json())
        if not (ontos := response_json.get("project", {}).get("ontologies")):
            raise ProjectOntologyNotFound(self.shortcode)
        output = cast(list[str], ontos)
        return output

    def _get_one_ontology(self, ontology_iri: str) -> str:
        url = ontology_iri
        headers = {"Accept": "text/turtle"}
        timeout = 30
        params = RequestParameters("GET", url, timeout=timeout, headers=headers)
        log_request(params)
        try:
            response = requests.get(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response, include_response_content=False)
        if response.ok:
            return response.text
        raise FatalNonOkApiResponseCode(params.url, response.status_code, response.text)
