from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from typing import cast
from urllib.parse import quote_plus

import requests
from loguru import logger
from requests import ReadTimeout
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.list_client import ListCreateClient
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.clients.list_client import OneList
from dsp_tools.clients.list_client import OneNode
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import InternalError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 30


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
        """
        Create a new list (root node) on the server.

        Args:
            list_info: Dictionary containing list information with keys:
                - projectIri: str
                - name: str
                - labels: list[dict[str, str]] with "value" and "language" keys
                - comments: list[dict[str, str]] (optional)

        Returns:
            The IRI of the newly created list, or None if creation failed.

        Raises:
            BadCredentialsError: If the user does not have sufficient permissions (HTTP 403).
        """
        url = f"{self.api_url}/admin/lists"
        logger.debug(f"POST create new list: {list_info.get('name', 'unnamed')}")

        try:
            response = self._post_and_log_request(url, list_info)
        except (TimeoutError, ReadTimeout) as err:
            logger.error(f"Timeout while creating list '{list_info.get('name', 'unnamed')}': {err}")
            return None

        if response.ok:
            try:
                result = response.json()
                list_iri = cast(str, result["list"]["listinfo"]["id"])
                return list_iri
            except (KeyError, ValueError) as e:
                logger.error(f"Unexpected response format when creating list: {e}")
                return None

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

    def add_list_node(self, node_info: dict[str, Any]) -> str | None:
        """
        Add a node to an existing list.

        Args:
            node_info: Dictionary containing node information with keys:
                - parentNodeIri: str
                - projectIri: str
                - name: str
                - labels: list[dict[str, str]] with "value" and "language" keys
                - comments: list[dict[str, str]] (optional)

        Returns:
            The IRI of the newly created node, or None if creation failed.

        Raises:
            BadCredentialsError: If the user does not have sufficient permissions (HTTP 403).
        """
        parent_iri = node_info.get("parentNodeIri")
        if not parent_iri:
            logger.error("Cannot add list node: parentNodeIri is missing")
            return None

        encoded_parent_iri = quote_plus(parent_iri)
        url = f"{self.api_url}/admin/lists/{encoded_parent_iri}"
        logger.debug(f"POST add list node: {node_info.get('name', 'unnamed')} to parent {parent_iri}")

        try:
            response = self._post_and_log_request(url, node_info)
        except (TimeoutError, ReadTimeout) as err:
            logger.error(f"Timeout while adding node '{node_info.get('name', 'unnamed')}': {err}")
            return None

        if response.ok:
            try:
                result = response.json()
                node_iri = cast(str, result["nodeinfo"]["id"])
                return node_iri
            except (KeyError, ValueError) as e:
                logger.error(f"Unexpected response format when adding node: {e}")
                return None

        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a project or system administrator can add nodes to lists. "
                "Your permissions are insufficient for this action."
            )

        logger.error(
            f"Failed to add node '{node_info.get('name', 'unnamed')}': Status {response.status_code}, {response.text}"
        )
        return None

    def _post_and_log_request(
        self,
        url: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> Response:
        """Make a POST request with authentication and logging."""
        data_dict, generic_headers = self._prepare_request(data, headers)
        params = RequestParameters("POST", url, TIMEOUT, data_dict, generic_headers)
        log_request(params)
        response = requests.post(
            url=params.url,
            headers=params.headers,
            json=params.data,
            timeout=params.timeout,
        )
        log_response(response)
        return response

    def _prepare_request(
        self, data: dict[str, Any] | None, headers: dict[str, str] | None
    ) -> tuple[dict[str, Any] | None, dict[str, str]]:
        """Prepare request headers with authentication token."""
        generic_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        data_dict = data if data else None
        if headers:
            generic_headers.update(headers)
        return data_dict, generic_headers
