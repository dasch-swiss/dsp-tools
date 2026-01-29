from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from typing import cast
from urllib.parse import quote_plus

import requests
from requests import RequestException
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.list_client import ListCreateClient
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.clients.list_client import ListInfo
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_and_warn_unexpected_non_ok_response
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT_10 = 10
TIMEOUT_30 = 30
TIMEOUT_60 = 60


@dataclass
class ListGetClientLive(ListGetClient):
    """Client to request and reformat the lists of a project."""

    api_url: str
    shortcode: str

    def get_all_lists_and_nodes(self) -> list[ListInfo]:
        list_json = self._get_all_list_iris()
        all_iris = self._extract_list_iris(list_json)
        all_lists = [self._get_one_list(iri) for iri in all_iris]
        return [self._reformat_one_list(lst) for lst in all_lists]

    def get_all_list_iris_and_names(self) -> dict[str, str]:
        response_json = self._get_all_list_iris()
        iris = self._extract_list_iris(response_json)
        names = [x["name"] for x in response_json["lists"]]
        return dict(zip(names, iris))

    def _get_all_list_iris(self) -> dict[str, Any]:
        url = f"{self.api_url}/admin/lists?projectShortcode={self.shortcode}"
        log_request(RequestParameters("GET", url, TIMEOUT_10))
        try:
            response = requests.get(url=url, timeout=TIMEOUT_10)
        except RequestException as err:
            log_and_raise_request_exception(err)

        log_response(response)
        if response.ok:
            json_response = cast(dict[str, Any], response.json())
            return json_response
        raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def _extract_list_iris(self, response_json: dict[str, Any]) -> list[str]:
        return [x["id"] for x in response_json["lists"]]

    def _get_one_list(self, list_iri: str) -> dict[str, Any]:
        encoded_list_iri = quote_plus(list_iri)
        url = f"{self.api_url}/admin/lists/{encoded_list_iri}"
        log_request(RequestParameters("GET", url, TIMEOUT_30))
        try:
            response = requests.get(url=url, timeout=TIMEOUT_30)
        except RequestException as err:
            log_and_raise_request_exception(err)

        log_response(response, include_response_content=False)
        if response.ok:
            response_json = cast(dict[str, Any], response.json())
            return response_json
        raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def _reformat_one_list(self, response_json: dict[str, Any]) -> ListInfo:
        return ListInfo(response_json["list"]["listinfo"], response_json["list"]["children"])


@dataclass
class ListCreateClientLive(ListCreateClient):
    api_url: str
    project_iri: str
    auth: AuthenticationClient

    def create_new_list(self, list_info: dict[str, Any]) -> str | None:
        url = f"{self.api_url}/admin/lists"
        headers = self._get_request_header()
        try:
            response = _post_and_log_request(url, list_info, headers)
        except RequestException as err:
            log_and_raise_request_exception(err)

        if response.ok:
            result = response.json()
            list_iri = cast(str, result["list"]["listinfo"]["id"])
            return list_iri
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a SystemAdmin or ProjectAdmin can create lists. "
                "Your permissions are insufficient for this action."
            )
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return None

    def add_list_node(self, node_info: dict[str, Any], parent_iri: str) -> str | None:
        encoded_parent_iri = quote_plus(parent_iri)
        url = f"{self.api_url}/admin/lists/{encoded_parent_iri}"
        headers = self._get_request_header()
        try:
            response = _post_and_log_request(url, node_info, headers)
        except RequestException as err:
            log_and_raise_request_exception(err)

        if response.ok:
            result = response.json()
            node_iri = cast(str, result["nodeinfo"]["id"])
            return node_iri
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a SystemAdmin or ProjectAdmin can add nodes to lists. "
                "Your permissions are insufficient for this action."
            )
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return None

    def _get_request_header(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }


def _post_and_log_request(
    url: str,
    data: dict[str, Any],
    headers: dict[str, str] | None = None,
) -> Response:
    params = RequestParameters("POST", url, TIMEOUT_60, data, headers)
    log_request(params)
    response = requests.post(
        url=params.url,
        headers=params.headers,
        data=params.data_serialized,
        timeout=params.timeout,
    )
    log_response(response)
    return response
