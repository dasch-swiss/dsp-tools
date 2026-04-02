from dataclasses import dataclass
from dataclasses import field
from http import HTTPStatus
from importlib.metadata import version
from typing import Any
from typing import cast

from requests import ReadTimeout
from requests import RequestException
from requests import Session

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_and_raise_timeouts
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT_1800 = 1800


@dataclass
class ResourceClientLive(ResourceClient):
    server: str
    auth: AuthenticationClient
    _session: Session = field(init=False, default_factory=Session)

    def __post_init__(self) -> None:
        self._session.headers["User-Agent"] = f"DSP-TOOLS/{version('dsp-tools')}"

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
            response = self._session.post(
                url=params.url,
                headers=params.headers,
                data=params.data_serialized,
                timeout=params.timeout,
            )
        except (TimeoutError, ReadTimeout) as err:
            log_and_raise_timeouts(err)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)

        match response.status_code:
            case HTTPStatus.OK:
                return cast(str, response.json()["@id"])
            case HTTPStatus.UNAUTHORIZED:
                raise BadCredentialsError(
                    "Authentication failed. Your credentials may be invalid or your token may have expired."
                )
            case HTTPStatus.FORBIDDEN:
                raise BadCredentialsError("You don't have permission to create resources in this project.")
            case _:
                return ResponseCodeAndText(response.status_code, response.text)
