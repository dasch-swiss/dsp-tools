from dataclasses import dataclass
from typing import Any

import requests

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.authentication_client import AuthenticationClient

# TODO: logging


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
        try:
            response: dict[str, Any] = requests.post(url, json=payload, timeout=10).json()
        except BadCredentialsError:
            raise UserError(f"Username and/or password are not valid on server '{self.server}'") from None
        except PermanentConnectionError as e:
            raise UserError(e.message) from None
        match response.get("token"):
            case str(token):
                self._token = token
                return token
            case _:
                raise UserError("Unable to retrieve a token from the server with the provided credentials.")
