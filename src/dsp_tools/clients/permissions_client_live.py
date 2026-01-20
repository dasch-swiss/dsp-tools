from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from urllib.parse import quote_plus

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.permissions_client import PermissionsClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT_10 = 10


@dataclass
class PermissionsClientLive(PermissionsClient):
    server: str
    auth: AuthenticationClient
    project_iri: str

    def get_project_doaps(self) -> list[dict[str, Any]] | ResponseCodeAndText:
        url = f"{self.server}/admin/permissions/doap/{quote_plus(self.project_iri)}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        params = RequestParameters("GET", url, TIMEOUT_10, headers=headers)
        log_request(params)
        try:
            response = requests.get(
                url=params.url,
                timeout=params.timeout,
                headers=params.headers,
            )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            response_json: dict[str, list[dict[str, Any]]] = response.json()
            return response_json["default_object_access_permissions"]
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "You don't have permission to view the default object access permissions for this project. "
                "Only users with appropriate project permissions can access DOAPs."
            )
        return ResponseCodeAndText(response.status_code, response.text)

    def delete_doap(self, doap_iri: str) -> ResponseCodeAndText | bool:
        url = f"{self.server}/admin/permissions/{quote_plus(doap_iri)}"
        headers = {
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        params = RequestParameters("DELETE", url, TIMEOUT_10, headers=headers)
        log_request(params)
        try:
            response = requests.delete(
                url=params.url,
                timeout=params.timeout,
                headers=params.headers,
            )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            return True
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "You don't have permission to delete default object access permissions. "
                "Only ProjectAdmin or SystemAdmin users can delete DOAPs."
            )
        return ResponseCodeAndText(response.status_code, response.text)

    def create_new_doap(self, payload: dict[str, Any]) -> ResponseCodeAndText | bool:
        url = f"{self.server}/admin/permissions/doap"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        params = RequestParameters("POST", url, TIMEOUT_10, data=payload, headers=headers)
        log_request(params)
        try:
            response = requests.post(
                url=params.url,
                timeout=params.timeout,
                headers=params.headers,
                data=params.data_serialized,
            )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            return True
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "You don't have permission to create default object access permissions. "
                "Only ProjectAdmin or SystemAdmin users can create DOAPs."
            )
        return ResponseCodeAndText(response.status_code, response.text)
