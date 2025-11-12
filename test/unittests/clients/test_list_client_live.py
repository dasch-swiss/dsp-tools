import json
from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests
from requests import JSONDecodeError

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.list_client_live import ListCreateClientLive
from dsp_tools.clients.list_client_live import ListGetClientLive
from dsp_tools.error.custom_warnings import DspToolsUnexpectedStatusCodeWarning
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import DspToolsRequestException
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode

PROJECT_IRI = "http://rdfh.ch/projects/projectIRI"
PARENT_NODE_IRI = "http://rdfh.ch/lists/0001/parent-iri"


@pytest.fixture
def response_all_list_one_project() -> dict[str, Any]:
    return {
        "lists": [
            {
                "id": "http://rdfh.ch/lists/9999/list1",
                "projectIri": PROJECT_IRI,
                "name": "firstList",
                "labels": [{"value": "List 1", "language": "en"}],
                "comments": [{"value": "This is the first list", "language": "en"}],
                "isRootNode": True,
            },
            {
                "id": "http://rdfh.ch/lists/9999/list2",
                "projectIri": PROJECT_IRI,
                "name": "secondList",
                "labels": [{"value": "List", "language": "en"}],
                "comments": [{"value": "This is the second list", "language": "en"}],
                "isRootNode": True,
            },
        ]
    }


@pytest.fixture
def response_all_list_one_project_no_lists() -> dict[str, Any]:
    return {"lists": []}


@pytest.fixture
def response_one_list() -> dict[str, Any]:
    return {
        "type": "ListGetResponseADM",
        "list": {
            "listinfo": {
                "id": "http://rdfh.ch/lists/9999/list1",
                "projectIri": PROJECT_IRI,
                "name": "firstList",
                "labels": [{"value": "List 1", "language": "en"}],
                "comments": [{"value": "This is the first list", "language": "en"}],
                "isRootNode": True,
            },
            "children": [
                {
                    "id": "http://rdfh.ch/lists/9999/n1",
                    "name": "n1",
                    "labels": [{"value": "Node 1", "language": "en"}],
                    "comments": [],
                    "position": 0,
                    "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                    "children": [
                        {
                            "id": "http://rdfh.ch/lists/9999/n11",
                            "name": "n1.1",
                            "labels": [{"value": "Node 1.1", "language": "en"}],
                            "comments": [],
                            "position": 0,
                            "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                            "children": [
                                {
                                    "id": "http://rdfh.ch/lists/9999/n111",
                                    "name": "n1.1.1",
                                    "labels": [{"value": "Node 1.1.1", "language": "en"}],
                                    "comments": [],
                                    "position": 0,
                                    "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                                    "children": [],
                                },
                                {
                                    "id": "http://rdfh.ch/lists/9999/n112",
                                    "name": "n1.1.2",
                                    "labels": [{"value": "Node 1.1.2", "language": "en"}],
                                    "comments": [],
                                    "position": 1,
                                    "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                                    "children": [],
                                },
                            ],
                        }
                    ],
                }
            ],
        },
    }


@pytest.fixture
def api_url() -> str:
    return "http://0.0.0.0:3333"


@pytest.fixture
def list_client(api_url: str) -> ListGetClientLive:
    return ListGetClientLive(api_url, "9999")


@pytest.fixture
def mock_auth() -> Mock:
    auth = Mock(spec=AuthenticationClient)
    auth.get_token.return_value = "test-token-123"
    auth.server = "http://0.0.0.0:3333"
    return auth


@pytest.fixture
def list_create_client(api_url: str, mock_auth: Mock) -> ListCreateClientLive:
    return ListCreateClientLive(api_url=api_url, project_iri=PROJECT_IRI, auth=mock_auth)


class TestListClient:
    def test_get_all_list_iris(self, list_client: ListGetClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"lists": []}
        with patch("dsp_tools.clients.list_client_live.requests.get", return_value=mock_response) as mock_get:
            result = list_client._get_all_list_iris()
        assert result == {"lists": []}
        assert mock_get.call_args_list[0][1]["url"] == f"{list_client.api_url}/admin/lists?projectShortcode=9999"

    def test_get_all_list_iris_non_ok_code(self, list_client: ListGetClientLive) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={}, text="")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.list_client_live.requests.get", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                list_client._get_all_list_iris()

    def test_get_all_list_iris_timeout(self, list_client: ListGetClientLive) -> None:
        with patch("dsp_tools.clients.list_client_live.requests.get", side_effect=requests.ReadTimeout("Timeout")):
            with pytest.raises(DspToolsRequestException):
                list_client._get_all_list_iris()

    def test_get_one_list(self, list_client: ListGetClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"type": "ListGetResponseADM", "list": {}}
        with patch("dsp_tools.clients.list_client_live.requests.get", return_value=mock_response) as mock_get:
            result = list_client._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")
        assert result == {"type": "ListGetResponseADM", "list": {}}
        url_expected = f"{list_client.api_url}/admin/lists/http%3A%2F%2Frdfh.ch%2Flists%2F9999%2FWWqeCEj8R_qrK5djsVcHvg"
        assert mock_get.call_args_list[0][1]["url"] == url_expected

    def test_get_one_list_non_ok_code(self, list_client: ListGetClientLive) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={}, text="")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.list_client_live.requests.get", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                list_client._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")

    def test_get_one_list_timeout(self, list_client: ListGetClientLive) -> None:
        with patch("dsp_tools.clients.list_client_live.requests.get", side_effect=requests.ReadTimeout("Timeout")):
            with pytest.raises(DspToolsRequestException):
                list_client._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")

    def test_extract_list_iris(
        self, list_client: ListGetClientLive, response_all_list_one_project: dict[str, Any]
    ) -> None:
        extracted = list_client._extract_list_iris(response_all_list_one_project)
        expected = {"http://rdfh.ch/lists/9999/list1", "http://rdfh.ch/lists/9999/list2"}
        assert set(extracted) == expected

    def test_extract_list_iris_no_lists(
        self, list_client: ListGetClientLive, response_all_list_one_project_no_lists: dict[str, Any]
    ) -> None:
        extracted = list_client._extract_list_iris(response_all_list_one_project_no_lists)
        assert not extracted

    def test_reformat_one_list(self, list_client: ListGetClientLive, response_one_list: dict[str, Any]) -> None:
        reformatted = list_client._reformat_one_list(response_one_list)
        sorted_nodes = sorted(reformatted.nodes, key=lambda x: x.name)
        assert reformatted.list_iri == "http://rdfh.ch/lists/9999/list1"
        assert reformatted.list_name == "firstList"
        names = [x.name for x in sorted_nodes]
        assert names == ["n1", "n1.1", "n1.1.1", "n1.1.2"]
        expected_iris = [
            "http://rdfh.ch/lists/9999/n1",
            "http://rdfh.ch/lists/9999/n11",
            "http://rdfh.ch/lists/9999/n111",
            "http://rdfh.ch/lists/9999/n112",
        ]
        iris = [x.iri for x in sorted_nodes]
        assert iris == expected_iris


class TestListCreateClient:
    def test_create_new_list_success(self, list_create_client: ListCreateClientLive) -> None:
        list_info = {
            "projectIri": PROJECT_IRI,
            "name": "test-list",
            "labels": [{"value": "Test List", "language": "en"}],
        }
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {
            "list": {
                "children": [],
                "listinfo": {
                    "id": "http://rdfh.ch/lists/0001/test-list-iri",
                    "name": "test-list",
                    "projectIri": PROJECT_IRI,
                    "labels": [{"value": "Test List", "language": "en"}],
                    "isRootNode": True,
                },
            }
        }
        with patch("dsp_tools.clients.list_client_live.requests.post", return_value=mock_response) as mock_post:
            result = list_create_client.create_new_list(list_info)
        assert result == "http://rdfh.ch/lists/0001/test-list-iri"
        assert mock_post.call_count == 1
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["url"] == f"{list_create_client.api_url}/admin/lists"
        assert call_kwargs["headers"]["Authorization"] == "Bearer test-token-123"
        # The data is serialized as bytes, so we need to decode and parse it
        assert json.loads(call_kwargs["data"]) == list_info

    def test_create_new_list_unauthorised(self, list_create_client: ListCreateClientLive) -> None:
        list_info = {
            "projectIri": PROJECT_IRI,
            "name": "test-list",
            "labels": [{"value": "Test List", "language": "en"}],
        }
        mock_response = Mock(status_code=401, ok=False, headers={}, text="Unauthorised")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.list_client_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError, match="Only a project or system administrator"):
                list_create_client.create_new_list(list_info)

    def test_create_new_list_timeout(self, list_create_client: ListCreateClientLive) -> None:
        list_info = {
            "projectIri": PROJECT_IRI,
            "name": "test-list",
            "labels": [{"value": "Test List", "language": "en"}],
        }
        with patch("dsp_tools.clients.list_client_live.requests.post", side_effect=requests.ReadTimeout("Timeout")):
            with pytest.raises(DspToolsRequestException):
                list_create_client.create_new_list(list_info)

    def test_create_new_list_server_error(self, list_create_client: ListCreateClientLive) -> None:
        list_info = {
            "projectIri": PROJECT_IRI,
            "name": "test-list",
            "labels": [{"value": "Test List", "language": "en"}],
        }
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.list_client_live.requests.post", return_value=mock_response):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = list_create_client.create_new_list(list_info)
        assert result is None

    def test_add_list_node_success(self, list_create_client: ListCreateClientLive) -> None:
        node_info = {
            "parentNodeIri": PARENT_NODE_IRI,
            "projectIri": PROJECT_IRI,
            "name": "test-node",
            "labels": [{"value": "Test Node", "language": "en"}],
        }
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {
            "nodeinfo": {
                "id": "http://rdfh.ch/lists/0001/test-node-iri",
                "name": "test-node",
                "hasRootNode": "http://rdfh.ch/lists/0001/root-iri",
                "labels": [{"value": "Test Node", "language": "en"}],
                "position": 1,
            }
        }
        with patch("dsp_tools.clients.list_client_live.requests.post", return_value=mock_response) as mock_post:
            result = list_create_client.add_list_node(node_info, PARENT_NODE_IRI)

        assert result == "http://rdfh.ch/lists/0001/test-node-iri"
        assert mock_post.call_count == 1
        call_kwargs = mock_post.call_args[1]
        expected_url = f"{list_create_client.api_url}/admin/lists/http%3A%2F%2Frdfh.ch%2Flists%2F0001%2Fparent-iri"
        assert call_kwargs["url"] == expected_url
        assert call_kwargs["headers"]["Authorization"] == "Bearer test-token-123"
        # The data is serialized as bytes, so we need to decode and parse it
        assert json.loads(call_kwargs["data"]) == node_info

    def test_add_list_node_unauthorised(self, list_create_client: ListCreateClientLive) -> None:
        node_info = {
            "parentNodeIri": PARENT_NODE_IRI,
            "projectIri": PROJECT_IRI,
            "name": "test-node",
            "labels": [{"value": "Test Node", "language": "en"}],
        }
        mock_response = Mock(status_code=401, ok=False, headers={}, text="Unauthorised")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.list_client_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError, match="Only a project or system administrator"):
                list_create_client.add_list_node(node_info, PARENT_NODE_IRI)

    def test_add_list_node_timeout(self, list_create_client: ListCreateClientLive) -> None:
        node_info = {
            "parentNodeIri": PARENT_NODE_IRI,
            "projectIri": PROJECT_IRI,
            "name": "test-node",
            "labels": [{"value": "Test Node", "language": "en"}],
        }
        with patch("dsp_tools.clients.list_client_live.requests.post", side_effect=requests.ReadTimeout("Timeout")):
            with pytest.raises(DspToolsRequestException):
                list_create_client.add_list_node(node_info, PARENT_NODE_IRI)

    def test_add_list_node_server_error(self, list_create_client: ListCreateClientLive) -> None:
        node_info = {
            "parentNodeIri": PARENT_NODE_IRI,
            "projectIri": PROJECT_IRI,
            "name": "test-node",
            "labels": [{"value": "Test Node", "language": "en"}],
        }
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.list_client_live.requests.post", return_value=mock_response):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = list_create_client.add_list_node(node_info, PARENT_NODE_IRI)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
