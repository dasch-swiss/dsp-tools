from dataclasses import dataclass
from http import HTTPStatus
from importlib.metadata import version
from typing import Any
from typing import cast

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


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
        timeout = 10
        url = f"{self.server}/v2/authentication"
        payload = {"email": self.email, "password": self.password}
        headers = {"User-Agent": f"DSP-TOOLS/{version('dsp-tools')}"}
        request_params = RequestParameters("POST", url, data=payload, timeout=timeout, headers=headers)
        log_request(request_params)
        try:
            response = requests.post(
                request_params.url,
                json=request_params.data,
                headers=request_params.headers,
                timeout=request_params.timeout,
            )
            log_response(response)
        except RequestException as err:
            log_and_raise_request_exception(err)

        if response.ok:
            res_json: dict[str, Any] = response.json()
            tkn = cast(str, res_json["token"])
            self._token = tkn
            return tkn
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise BadCredentialsError(
                f"Login to the API with the email '{self.email}' was not successful. "
                f"Please ensure that an account for this email exists and that the password is correct."
            )
        raise FatalNonOkApiResponseCode(url, response.status_code, response.text)
