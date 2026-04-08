from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.value_client import ValueClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT_600 = 600


@dataclass
class ValueClientLive(ValueClient):
    server: str
    auth: AuthenticationClient

    def post_new_value(self, value_json: dict[str, Any]) -> None | ResponseCodeAndText:
        url = f"{self.server}/v2/values"
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        params = RequestParameters("POST", url, TIMEOUT_600, value_json, headers)

        log_request(params)
        try:
            response = requests.post(
                url=params.url,
                headers=params.headers,
                data=params.data_serialized,
                timeout=params.timeout,
            )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)

        match response.status_code:
            case HTTPStatus.OK:
                return None
            case HTTPStatus.UNAUTHORIZED:
                raise BadCredentialsError(
                    "Authentication failed. Your credentials may be invalid or your token may have expired."
                )
            case HTTPStatus.FORBIDDEN:
                raise BadCredentialsError("You don't have permission to create values in this project.")
            case _:
                return ResponseCodeAndText(response.status_code, response.text)

    def replace_existing_value(self, value_json: dict[str, Any]) -> None | ResponseCodeAndText:
        url = f"{self.server}/v2/values"
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        params = RequestParameters("PUT", url, TIMEOUT_600, value_json, headers)

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
            case HTTPStatus.OK:
                return None
            case HTTPStatus.UNAUTHORIZED:
                raise BadCredentialsError(
                    "Authentication failed. Your credentials may be invalid or your token may have expired."
                )
            case HTTPStatus.FORBIDDEN:
                raise BadCredentialsError("You don't have permission to update values in this project.")
            case _:
                return ResponseCodeAndText(response.status_code, response.text)
