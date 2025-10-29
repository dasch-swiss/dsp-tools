from dataclasses import dataclass
from typing import Any
from typing import cast
from urllib.parse import quote_plus

import requests

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.list_client import ListCreateClient
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.clients.list_client import OneList
from dsp_tools.clients.list_client import OneNode
from dsp_tools.error.exceptions import InternalError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


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
        # TODO: add project IRI to list_info
        """Expected response:
                {
            "list": {
                "children": [],
                "listinfo": {
                    "comments": [{ "value": "New comment", "language": "en"}],
                    "id": "http://rdfh.ch/lists/0001/yWQEGXl53Z4C4DYJ-S2c5A",
                    "isRootNode": true,
                    "labels": [
                        {
                            "value": "New list with IRI",
                            "language": "en"
                        }
                    ],
                    "name": "a new list",
                    "projectIri": "http://rdfh.ch/projects/0001"
                }
            }
        }
        """
        # we return "id"

    def add_list_node(self, node_info: dict[str, Any]) -> str | None:
        # TODO: add project IRI to node_info
        """Expected response:

                {
            "nodeinfo": {
                "comments": [],
                "hasRootNode": "http://rdfh.ch/lists/0001/yWQEGXl53Z4C4DYJ-S2c5A",
                "id": "http://rdfh.ch/lists/0001/8u37MxBVMbX3XQ8-d31x6w",
                "labels": [
                    {
                        "value": "New List Node",
                        "language": "en"
                    }
                ],
                "name": "a new child",
                "position": 1
            }
        }
        """
        # we return "id"
