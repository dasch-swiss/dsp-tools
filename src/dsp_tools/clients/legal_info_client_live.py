from dataclasses import dataclass
from typing import Any

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

    def get_enabled_licenses(self) -> list[dict[str, Any]]:
        logger.debug("GET enabled licenses of the project.")
        page_num = 1
        all_data = []
        has_items = True
        while has_items:
            try:
                response = self._get_one_enabled_license_page(page_num)
            except (TimeoutError, ReadTimeout) as err:
                log_and_raise_timeouts(err)
            if response.ok:
                response_dict = response.json()
                all_data.extend(response_dict["data"])
                has_items = _is_not_last_page(response_dict)
            elif response.status_code == HTTP_LACKING_PERMISSIONS:
                raise BadCredentialsError(
                    "Only a project or system administrator can create new copyright holders. "
                    "Your permissions are insufficient for this action."
                )
            else:
                raise BaseError(
                    f"An unexpected response with the status code {response.status_code} was received from the API. "
                    f"Please consult 'warnings.log' for details."
                )
        return all_data

    def _get_one_enabled_license_page(self, page_num: int) -> Response:
        url = (
            f"{self.server}/admin/projects/shortcode/{self.project_shortcode}/"
            f"legal-info/licenses?page={page_num}&page-size=25&order=Asc&showOnlyEnabled=true"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        params = RequestParameters(method="GET", url=url, timeout=TIMEOUT, headers=headers)
        log_request(params)
        response = requests.get(
            url=params.url,
            headers=params.headers,
            data=params.data_serialized,
            timeout=params.timeout,
        )
        log_response(response)
        return response


def _is_not_last_page(response: dict[str, Any]) -> bool:
    current_page = response["pagination"]["currentPage"]
    total_page = response["pagination"]["totalPages"]
    return bool(current_page != total_page)
