from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from typing import cast

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT_1800 = 1800


@dataclass
class ResourceClientLive(ResourceClient):
    server: str
    auth: AuthenticationClient

    def post_resource(self, resource_json: dict[str, Any], resource_has_bitstream: bool) -> str | ResponseCodeAndText:
        url = f"{self.server}/v2/resources"
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        if resource_has_bitstream:
            headers["X-Asset-Ingested"] = "true"
        params = RequestParameters("POST", url, TIMEOUT_1800, resource_json, headers)

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
                return cast(str, response.json()["@id"])
            case HTTPStatus.FORBIDDEN:
                raise BadCredentialsError("You don't have permission to create resources in this project.")
            case _:
                return ResponseCodeAndText(response.status_code, response.text)
