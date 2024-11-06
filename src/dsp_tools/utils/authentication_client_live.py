from dataclasses import dataclass
from importlib.metadata import version
from typing import Any

import requests
from loguru import logger

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.authentication_client import AuthenticationClient


@dataclass
class AuthenticationClientLive(AuthenticationClient):
    """
    Client that can authenticate with a DSP server and return a token.
    """

    server: str
    email: str
    password: str
    _token: str | None = None

    def get_token(self) -> str:
        """
        Returns a token. If no token is available, it will get one from the server.
        """
        if self._token:
            return self._token
        return self._get_token()

    def _get_token(self) -> str:
        url = f"{self.server}/v2/authentication"
        payload = {"email": self.email, "password": self.password}
        logger.debug(f"REQUEST: Requesting token from url '{url}' for user '{self.email}'.")
        headers = {"User-Agent": f'DSP-TOOLS/{version("dsp-tools")}'}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            logger.debug(f"RESPONSE: Requesting token responded with status {response.status_code}")
            res_json: dict[str, Any] = response.json()
        except BadCredentialsError:
            raise UserError(f"Username and/or password are not valid on server '{self.server}'") from None
        except PermanentConnectionError as e:
            raise UserError(e.message) from None
        match res_json.get("token"):
            case str(token):
                self._token = token
                return token
            case _:
                raise UserError("Unable to retrieve a token from the server with the provided credentials.")
