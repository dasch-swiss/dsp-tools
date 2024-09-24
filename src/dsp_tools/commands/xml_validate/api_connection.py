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

STATUS_UNAUTHORIZED = 401


@dataclass
class OntologyConnection:
    api_url: str
    shortcode: str

    def get(self, url: str, headers: dict[str, Any]) -> Response:
        """
        Sends a get request to the designated path

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
            response = requests.request("POST", url, headers=headers, timeout=100)
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
        response = self.get(endpoint, {})
        response_json = cast(dict[str, Any], response.json())
        if not (ontos := response_json.get("ontologies")):
            msg = f"The response from the API does not contain any ontologies.\nAPI response:{response}"
            logger.exception(msg)
            raise UserError(msg)
        output = cast(list[str], ontos)
        return output

    def _get_one_ontology(self, ontology_iri: str) -> str:
        header = {"Accept": "text/turtle"}
        response = self.get(ontology_iri, header)
        return response.text
