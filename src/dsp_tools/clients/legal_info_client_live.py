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

    def get_licenses_of_a_project(self, enabled_only: bool = True) -> list[dict[str, Any]]:
        logger.debug("GET enabled licenses of the project.")
        page_num = 1
        all_data = []
        is_last_page = False
        while not is_last_page:
            response = self._get_one_license_page(page_num, enabled_only)
            response_dict = response.json()
            all_data.extend(response_dict["data"])
            is_last_page = _is_last_page(response_dict)
        return all_data

    def _get_one_license_page(self, page_num: int, enabled_only: bool) -> Response:
        enabled = str(enabled_only).lower()
        url = (
            f"{self.server}/admin/projects/shortcode/{self.project_shortcode}/"
            f"legal-info/licenses?page={page_num}&page-size=25&order=Asc&showOnlyEnabled={enabled}"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        params = RequestParameters(method="GET", url=url, timeout=TIMEOUT, headers=headers)
        log_request(params)
        try:
            response = requests.get(
                url=params.url,
                headers=params.headers,
                timeout=params.timeout,
            )
            log_response(response)
        except (TimeoutError, ReadTimeout) as err:
            log_and_raise_timeouts(err)
        if response.ok:
            return response
        elif response.status_code == HTTP_LACKING_PERMISSIONS:
            raise BadCredentialsError(
                "Only members of a project or system administrators can request the enabled licenses of a project."
                "Your permissions are insufficient for this action."
            )
        else:
            raise BaseError(
                f"An unexpected response with the status code {response.status_code} was received from the API. "
                f"Please consult 'warnings.log' for details."
            )

    def enable_unknown_license(self) -> None:
        escaped_license_iri = "http%3A%2F%2Frdfh.ch%2Flicenses%2Funknown"
        url = (
            f"{self.server}/admin/projects/shortcode/{self.project_shortcode}/"
            f"legal-info/licenses/{escaped_license_iri}/enable"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        params = RequestParameters("POST", url, TIMEOUT, headers=headers)
        log_request(params)
        response = requests.put(
            url=params.url,
            headers=params.headers,
            timeout=params.timeout,
        )
        log_response(response)
        if response.ok:
            pass
        elif response.status_code == HTTP_LACKING_PERMISSIONS:
            raise BadCredentialsError(
                "Only members of a project or system administrators can enable licenses. "
                "Your permissions are insufficient for this action."
            )
        else:
            raise BaseError(
                f"An unexpected response with the status code {response.status_code} was received from the API. "
                f"Please consult 'warnings.log' for details."
            )


def _is_last_page(response: dict[str, Any]) -> bool:
    current_page = response["pagination"]["currentPage"]
    total_page = response["pagination"]["totalPages"]
    return bool(current_page == total_page)
