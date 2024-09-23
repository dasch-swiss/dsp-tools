import json
from loguru import logger
from requests import ReadTimeout
from requests import RequestException
from requests import Response
import requests
from typing import cast, Any
from dataclasses import dataclass
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import BaseError
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
            raise UserError(f"Username and/or password are not valid on server '{self.api_url}'") from None
        except PermanentConnectionError as e:
            raise UserError(e.message) from None
        if not response.ok:
            raise UserError(f"Non-ok response code: {response.status_code}\nOriginal Message: {response.text}")
        json_response = cast(dict[str, Any], response.json())
        if not json_response.get("token"):
            raise UserError("Unable to retrieve a token from the server with the provided credentials.")
        tkn = json_response["token"]
        self.bearer_tkn = f"Bearer {tkn}"


@dataclass
class OntologyConnection:
    api_url: str
    shortcode: str

    def get(self, url: str, headers):
        pass

    def get_ontologies(self, token: str) -> dict[str, Any]:
        pass

    def _get_ontology_names(self, token: str):
        pass
