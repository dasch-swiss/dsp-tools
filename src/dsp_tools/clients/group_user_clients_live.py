from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from typing import cast
from urllib.parse import quote_plus

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.group_user_clients import GroupClient
from dsp_tools.clients.group_user_clients import UserClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_and_warn_unexpected_non_ok_response
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 30


@dataclass
class UserClientLive(UserClient):
    api_url: str
    auth: AuthenticationClient

    def get_user_iri_by_username(self, username: str) -> str | None:
        url = f"{self.api_url}/admin/users/username/{username}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("GET", url, TIMEOUT, headers=headers)
        log_request(params)
        try:
            response = requests.get(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            result = response.json()
            return cast(str, result["user"]["id"])
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You do not have sufficient credentials to retrieve user information.")
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return None

    def post_new_user(self, user_dict: dict[str, Any]) -> str | None:
        url = f"{self.api_url}/admin/users"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        params = RequestParameters("POST", url, TIMEOUT, data=user_dict, headers=headers)
        log_request(params)
        try:
            response = requests.post(
                url=params.url, headers=params.headers, data=params.data_serialized, timeout=params.timeout
            )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            result = response.json()
            return cast(str, result["user"]["id"])
        if response.status_code == HTTPStatus.BAD_REQUEST:
            # if the user exists we get a 400, this should never happen through code design
            raise FatalNonOkApiResponseCode(url, response.status_code, response.text)
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You don't have permission to create users.")
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return None

    def add_user_as_project_member(self, user_iri: str, project_iri: str) -> bool:
        project_iri_encoded = quote_plus(project_iri)
        user_iri_encoded = quote_plus(user_iri)
        url = f"{self.api_url}/admin/users/iri/{user_iri_encoded}/project-memberships/{project_iri_encoded}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", url, TIMEOUT, headers=headers)
        log_request(params)
        try:
            response = requests.post(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            return True
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You don't have permission to add users to projects.")
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return False

    def add_user_as_project_admin(self, user_iri: str, project_iri: str) -> bool:
        project_iri_encoded = quote_plus(project_iri)
        user_iri_encoded = quote_plus(user_iri)
        url = f"{self.api_url}/admin/users/iri/{user_iri_encoded}/project-admin-memberships/{project_iri_encoded}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", url, TIMEOUT, headers=headers)
        log_request(params)
        try:
            response = requests.post(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            return True
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You don't have permission to add users as project admins.")
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return False

    def add_user_to_custom_groups(self, user_iri: str, groups: list[str]) -> bool:
        user_iri_encoded = quote_plus(user_iri)
        successes = []
        for gr in groups:
            result = self._add_user_to_one_group(user_iri_encoded, gr)
            successes.append(result)
        return all(successes)

    def _add_user_to_one_group(self, user_iri_encoded: str, group_iri: str) -> bool:
        group_iri_encoded = quote_plus(group_iri)
        url = f"{self.api_url}/admin/users/iri/{user_iri_encoded}/group-memberships/{group_iri_encoded}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", url, TIMEOUT, headers=headers)
        log_request(params)
        try:
            response = requests.post(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            return True
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You don't have permission to add users to groups.")
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return False


@dataclass
class GroupClientLive(GroupClient):
    api_url: str
    auth: AuthenticationClient

    def get_all_groups(self) -> list[dict[str, Any]]:
        url = f"{self.api_url}/admin/groups"
        params = RequestParameters("GET", url, TIMEOUT)
        log_request(params)
        try:
            response = requests.get(params.url, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            result = response.json()
            return cast(list[dict[str, Any]], result["groups"])
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return []

    def create_new_group(self, group_dict: dict[str, Any]) -> str | None:
        url = f"{self.api_url}/admin/groups"
        headers = {"Accept": "application/json", "Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", url, TIMEOUT, headers=headers, data=group_dict)
        log_request(params)
        try:
            response = requests.post(
                params.url, data=params.data_serialized, timeout=params.timeout, headers=params.headers
            )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            result = response.json()
            return cast(str, result["group"]["id"])
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a SystemAdmin or ProjectAdmin can create groups. "
                "Your permissions are insufficient for this action."
            )
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return None
