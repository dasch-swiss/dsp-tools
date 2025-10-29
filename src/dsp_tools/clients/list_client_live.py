from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from typing import cast
from urllib.parse import quote_plus

import requests
from loguru import logger
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.list_client import ListCreateClient
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.clients.list_client import OneList
from dsp_tools.clients.list_client import OneNode
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UnexpectedApiResponseError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 60


@dataclass
class ListGetClientLive(ListGetClient):
    """Client to request and reformat the lists of a project."""

    api_url: str
    shortcode: str

    def get_all_lists_and_nodes(self) -> list[OneList]:
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
        timeout = 10
        log_request(RequestParameters("GET", url, timeout))
        response = requests.get(url=url, timeout=timeout)
        log_response(response)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        json_response = cast(dict[str, Any], response.json())
        return json_response

    def _extract_list_iris(self, response_json: dict[str, Any]) -> list[str]:
        return [x["id"] for x in response_json["lists"]]

    def _get_one_list(self, list_iri: str) -> dict[str, Any]:
        encoded_list_iri = quote_plus(list_iri)
        url = f"{self.api_url}/admin/lists/{encoded_list_iri}"
        timeout = 30
        log_request(RequestParameters("GET", url, timeout))
        response = requests.get(url=url, timeout=timeout)
        log_response(response, include_response_content=False)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        response_json = cast(dict[str, Any], response.json())
        return response_json

    def _reformat_one_list(self, response_json: dict[str, Any]) -> OneList:
        list_name = response_json["list"]["listinfo"]["name"]
        list_id = response_json["list"]["listinfo"]["id"]
        nodes = response_json["list"]["children"]
        all_nodes = []
        for child in nodes:
            all_nodes.append(OneNode(child["name"], child["id"]))
            if node_child := child.get("children"):
                self._reformat_children(node_child, all_nodes)
        return OneList(list_iri=list_id, list_name=list_name, nodes=all_nodes)

    def _reformat_children(self, list_child: list[dict[str, Any]], current_nodes: list[OneNode]) -> None:
        for child in list_child:
            current_nodes.append(OneNode(child["name"], child["id"]))
            if grand_child := child.get("children"):
                self._reformat_children(grand_child, current_nodes)


@dataclass
class ListCreateClientLive(ListCreateClient):
    api_url: str
    project_iri: str
    auth: AuthenticationClient

    def create_new_list(self, list_info: dict[str, Any]) -> str | None:
        url = f"{self.api_url}/admin/lists"
        logger.debug(f"POST create new list: {list_info['name']}")
        try:
            headers = self._get_request_header()
            response = _post_and_log_request(url, list_info, headers)
        except Exception as err:  # noqa: BLE001
            logger.error(err)
            return None
        if response.ok:
            try:
                result = response.json()
                list_iri = cast(str, result["list"]["listinfo"]["id"])
                return list_iri
            except (KeyError, ValueError) as e:
                raise UnexpectedApiResponseError(f"Unexpected response format when creating list: {e}") from None
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a project or system administrator can create lists. "
                "Your permissions are insufficient for this action."
            )
        logger.error(
            f"Failed to create list '{list_info.get('name', 'unnamed')}': "
            f"Status {response.status_code}, {response.text}"
        )
        return None

    def add_list_node(self, node_info: dict[str, Any], parent_iri: str) -> str | None:
        encoded_parent_iri = quote_plus(parent_iri)
        url = f"{self.api_url}/admin/lists/{encoded_parent_iri}"
        logger.debug(f"POST add list node: {node_info['name']} to parent {parent_iri}")

        try:
            headers = self._get_request_header()
            response = _post_and_log_request(url, node_info, headers)
        except Exception as err:  # noqa: BLE001
            logger.error(err)
            return None
        if response.ok:
            try:
                result = response.json()
                node_iri = cast(str, result["nodeinfo"]["id"])
                return node_iri
            except (KeyError, ValueError) as e:
                raise UnexpectedApiResponseError(f"Unexpected response format when creating list: {e}") from None
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a project or system administrator can add nodes to lists. "
                "Your permissions are insufficient for this action."
            )
        logger.error(f"Failed to add node '{node_info['name']}': Status {response.status_code}, {response.text}")
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
    params = RequestParameters("POST", url, TIMEOUT, data, headers)
    log_request(params)
    response = requests.post(
        url=params.url,
        headers=params.headers,
        data=params.data_serialized,
        timeout=params.timeout,
    )
    log_response(response)
    return response
