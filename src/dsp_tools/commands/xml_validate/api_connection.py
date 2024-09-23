from dataclasses import dataclass
from typing import Any
from typing import cast

import requests
from loguru import logger
from requests import ReadTimeout
from requests import RequestException
from requests import Response

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import InternalError
from dsp_tools.models.exceptions import UserError


@dataclass
class Authentication:
    api_url: str
    user_email: str
    password: str
    bearer_tkn: str | None = None

    def get_bearer_token(self) -> str:
        response = self._request_token()
        if not response.ok:
            msg = f"Non-ok response code: {response.status_code}\nOriginal Message: {response.text}"
            logger.exception(msg)
            raise UserError(msg)
        json_response = cast(dict[str, Any], response.json())
        if not json_response.get("token"):
            msg = "Unable to retrieve a token from the server with the provided credentials."
            logger.exception(msg)
            raise InternalError(msg)
        tkn = f"Bearer {json_response["token"]}"
        self.bearer_tkn = tkn
        return tkn

    def _request_token(self) -> Response:
        try:
            return requests.post(
                url=f"{self.api_url}/v2/authentication",
                data={"email": self.user_email, "password": self.password},
                timeout=10,
            )
        except BadCredentialsError:
            msg = f"Username and/or password are not valid on server '{self.api_url}'"
            logger.exception(msg)
            raise UserError(msg) from None


@dataclass
class OntologyConnection:
    api_url: str
    shortcode: str

    def get(self, url: str, token: str, headers: dict[str, Any]) -> Response:
        """
        Sends a get request to the designated path

        Args:
            url: URL for the request
            token: bearer token
            headers: headers for the request

        Returns:
            Response of the request if it was a 200 response code

        Raises:
            InternalError: in case of errors raised by the requests library
            UserError: If a non-200 response was given
        """
        headers["Authorization"] = token
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

    def get_ontologies(self, token: str) -> list[str]:
        """
        Returns a list of project ontologies as a string in turtle format.

        Args:
            token: authentication token

        Returns:
            list of ontologies
        """
        ontology_iris = self._get_ontology_iris(token)
        return [self._get_one_ontology(x, token) for x in ontology_iris]

    def _get_one_ontology(self, ontology_iri: str, token: str) -> str:
        header = {"Accept": "text/turtle"}
        response = self.get(ontology_iri, token, header)
        return response.text

    def _get_ontology_iris(self, token: str) -> list[str]:
        endpoint = f"{self.api_url}/admin/projects/shortcode/{self.shortcode}"
        response = self.get(endpoint, token, {})
        response_json = cast(dict[str, Any], response.json())
        if not (ontos := response_json.get("ontologies")):
            msg = f"The response from the API does not contain any ontologies.\nAPI response:{response}"
            logger.exception(msg)
            raise UserError(msg)
        if isinstance(ontos, list):
            out_onto = ontos
        elif isinstance(ontos, str):
            out_onto = [ontos]
        else:
            msg = f"The response from the API does not contain any ontologies.\nAPI response:{response}"
            logger.exception(msg)
            raise UserError(msg)
        return out_onto
