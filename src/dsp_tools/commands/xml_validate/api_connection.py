from dataclasses import dataclass
from typing import Any
from typing import cast

import requests
from loguru import logger
from requests import ReadTimeout
from requests import RequestException
from requests import Response

from dsp_tools.models.exceptions import InternalError
from dsp_tools.models.exceptions import UserError


@dataclass
class OntologyConnection:
    api_url: str
    shortcode: str

    def _get(self, url: str, headers: dict[str, Any] | None = None) -> Response:
        """
        Sends a get request to the designated url

        Args:
            url: URL for the request
            headers: headers for the request

        Returns:
            Response of the request if it was a 200 response code

        Raises:
            InternalError: in case of errors raised by the requests library
            UserError: If a non-200 response was given
        """
        try:
            timeout = 100
            logger.debug(f"REQUEST: GET to {url}, timeout: {timeout}, headers: {headers}")
            response = requests.get(url, headers=headers, timeout=timeout)
            logger.debug(f"RESPONSE: {response.status_code}")
        except (TimeoutError, ReadTimeout) as err:
            logger.exception(err)
            raise InternalError("TimeoutError occurred. See logs for details.") from None
        except (ConnectionError, RequestException) as err:
            logger.exception(err)
            raise InternalError("ConnectionError occurred. See logs for details.") from None
        if not response.ok:
            msg = f"Non-ok response: {response.status_code}\nOriginal message: {response.text}"
            logger.exception(msg)
            raise UserError(msg)
        return response

    def get_ontologies(self) -> list[str]:
        """
        Returns a list of project ontologies as a string in turtle format.

        Returns:
            list of ontologies
        """
        ontology_iris = self._get_ontology_iris()
        return [self._get_one_ontology(x) for x in ontology_iris]

    def _get_ontology_iris(self) -> list[str]:
        endpoint = f"{self.api_url}/admin/projects/shortcode/{self.shortcode}"
        response = self._get(endpoint)
        response_json = cast(dict[str, Any], response.json())
        msg = f"The response from the API does not contain any ontologies.\nAPI response:{response.text}"
        if not (proj := response_json.get("project")):
            logger.exception(msg)
            raise UserError(msg)
        if not (ontos := proj.get("ontologies")):
            logger.exception(msg)
            raise UserError(msg)
        output = cast(list[str], ontos)
        return output

    def _get_one_ontology(self, ontology_iri: str) -> str:
        response = self._get(ontology_iri, headers={"Accept": "text/turtle"})
        return response.text
