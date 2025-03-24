from dataclasses import dataclass

import requests
from loguru import logger
from requests import ReadTimeout
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import BaseError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_timeouts
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 60

HTTP_LACKING_PERMISSIONS = 403


@dataclass
class LegalInfoClientLive(LegalInfoClient):
    server: str
    project_shortcode: str
    authentication_client: AuthenticationClient

    def post_copyright_holders(self, copyright_holders: list[str]) -> None:
        """Send a list of new copyright holders to the API"""
        logger.debug(f"POST {len(copyright_holders)} new copyright holders")
        try:
            response = self._post_and_log_request("copyright-holders", copyright_holders)
        except (TimeoutError, ReadTimeout) as err:
            log_and_raise_timeouts(err)
        if response.ok:
            return
        if response.status_code == HTTP_LACKING_PERMISSIONS:
            raise BadCredentialsError(
                "Only a project or system administrator can create new copyright holders. "
                "Your permissions are insufficient for this action."
            )
        else:
            raise BaseError(
                f"An unexpected response with the status code {response.status_code} was received from the API. "
                f"Please consult 'warnings.log' for details."
            )

    def _post_and_log_request(self, endpoint: str, data: list[str]) -> Response:
        url = f"{self.server}/admin/projects/shortcode/{self.project_shortcode}/legal-info/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        params = RequestParameters("POST", url, TIMEOUT, {"data": data}, headers)
        log_request(params)
        response = requests.post(
            url=params.url,
            headers=params.headers,
            data=params.data_serialized,
            timeout=params.timeout,
        )
        log_response(response)
        return response
