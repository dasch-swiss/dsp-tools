import json
from loguru import logger
from requests import ReadTimeout
from requests import RequestException
from requests import Response
import requests
from typing import cast, Any
from dataclasses import dataclass

from dsp_tools.commands.xml_validate.models.data_rdf import IntValueRDF
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import BaseError, InternalError
from dsp_tools.models.exceptions import InvalidInputError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.models.exceptions import UserError


@dataclass
class Authentication:
    api_url: str
    user_email: str
    password: str
    bearer_tkn: str

    def get_tkn(self) -> None:
        try:
            response = requests.post(
                url=f"{self.api_url}/v2/authentication",
                data={"email": self.user_email, "password": self.password},
                timeout=10,
            )
        except BadCredentialsError:
            msg = f"Username and/or password are not valid on server '{self.api_url}'"
            logger.exception(msg)
            raise UserError(msg) from None
        if not response.ok:
            msg = f"Non-ok response code: {response.status_code}\nOriginal Message: {response.text}"
            logger.exception(msg)
            raise UserError(msg)
        json_response = cast(dict[str, Any], response.json())
        if not json_response.get("token"):
            msg = "Unable to retrieve a token from the server with the provided credentials."
            logger.exception(msg)
            raise UserError(msg)
        tkn = json_response["token"]
        self.bearer_tkn = f"Bearer {tkn}"


@dataclass
class OntologyConnection:
    api_url: str
    shortcode: str

    def get(self, url: str, token: str, headers: dict[str, Any]) -> dict[str, Any]:
        headers["Authorization"] = token
        try:
            response = requests.request("POST", url, headers=headers)
        except (TimeoutError, ReadTimeout) as err:
            logger.exception(err)
            raise InternalError("TimeoutError occurred. See logs for details.") from None
        except (ConnectionError, RequestException) as err:
            logger.exception(err)
            raise InternalError("ConnectionError occurred. See logs for details.") from None
        if not response.ok:
            msg = ""


    def get_ontologies(self, token: str) -> dict[str, Any]:
        pass

    def _get_ontology_names(self, token: str):
        pass
