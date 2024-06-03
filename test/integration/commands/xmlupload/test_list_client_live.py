from dataclasses import dataclass
from typing import Any

import pytest

from dsp_tools.commands.xmlupload.list_client import List
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.list_client import ListNode
from dsp_tools.commands.xmlupload.list_client import _get_list_from_server
from dsp_tools.commands.xmlupload.list_client import _get_list_iris_from_server
from test.integration.commands.xmlupload.connection_mock import ConnectionMockBase


@dataclass
class ConnectionMock(ConnectionMockBase):
    get_responses: list[dict[str, Any]]

    def get(
        self,
        route: str,  # noqa: ARG002 (unused-method-argument)
        headers: dict[str, str] | None = None,  # noqa: ARG002 (unused-method-argument)
    ) -> dict[str, Any]:
        return self.get_responses.pop(0)


class TestGetListNodeLookup:
    def test_list_root_only(self) -> None:
        list_iris = {"lists": [{"id": "http://www.example.org/lists#a"}]}
        list_a = {
            "list": {
                "listinfo": {
                    "id": "http://www.example.org/lists#a",
                    "name": "list-a",
                },
                "children": [],
            }
        }
        con = ConnectionMock([list_iris, list_a])
        list_client = ListClientLive(con, "")
        lookup = list_client.get_list_node_id_to_iri_lookup()
        expected = {"list-a:list-a": "http://www.example.org/lists#a"}
        assert lookup == expected

    def test_list_with_children(self) -> None:
        list_iris = {"lists": [{"id": "http://www.example.org/lists#a"}]}
        list_a = {
            "list": {
                "listinfo": {
                    "id": "http://www.example.org/lists#a",
                    "name": "list-a",
                },
                "children": [
                    {
                        "id": "http://www.example.org/lists#a1",
                        "name": "node-a1",
                    },
                    {
                        "id": "http://www.example.org/lists#a2",
                        "name": "node-a2",
                    },
                ],
            }
        }
        con = ConnectionMock([list_iris, list_a])
        list_client = ListClientLive(con, "")
        lookup = list_client.get_list_node_id_to_iri_lookup()
        expected = {
            "list-a:list-a": "http://www.example.org/lists#a",
            "list-a:node-a1": "http://www.example.org/lists#a1",
            "list-a:node-a2": "http://www.example.org/lists#a2",
        }
        assert lookup == expected

    def test_multiple_lists(self) -> None:
        list_iris = {
            "lists": [
                {"id": "http://www.example.org/lists#a"},
                {"id": "http://www.example.org/lists#b"},
            ]
        }
        list_a = {
            "list": {
                "listinfo": {
                    "id": "http://www.example.org/lists#a",
                    "name": "list-a",
                },
                "children": [
                    {
                        "id": "http://www.example.org/lists#a1",
                        "name": "node-a1",
                    },
                ],
            }
        }
        list_b = {
            "list": {
                "listinfo": {
                    "id": "http://www.example.org/lists#b",
                    "name": "list-b",
                },
                "children": [
                    {
                        "id": "http://www.example.org/lists#b1",
                        "name": "node-b1",
                    },
                ],
            }
        }
        con = ConnectionMock([list_iris, list_a, list_b])
        list_client = ListClientLive(con, "")
        lookup = list_client.get_list_node_id_to_iri_lookup()
        expected = {
            "list-a:list-a": "http://www.example.org/lists#a",
            "list-a:node-a1": "http://www.example.org/lists#a1",
            "list-b:list-b": "http://www.example.org/lists#b",
            "list-b:node-b1": "http://www.example.org/lists#b1",
        }
        assert lookup == expected


class TestGetListFromServer:
    def test_no_name_no_children(self) -> None:
        list_response = {
            "list": {
                "listinfo": {
                    "id": "http://www.example.org/lists#a",
                    "labels": [{"value": "some label"}],
                },
                "children": [],
            }
        }
        con = ConnectionMock([list_response])
        result = _get_list_from_server(con, "")
        expected_node = ListNode(node_iri="http://www.example.org/lists#a", node_name="some label")
        expected = List(
            root_iri="http://www.example.org/lists#a",
            list_name="some label",
            nodes=[expected_node],
        )
        assert result == expected

    def test_name_no_children(self) -> None:
        list_response = {
            "list": {
                "listinfo": {
                    "id": "http://www.example.org/lists#a",
                    "name": "list-a",
                },
                "children": [],
            }
        }
        con = ConnectionMock([list_response])
        result = _get_list_from_server(con, "")
        expected_node = ListNode(node_iri="http://www.example.org/lists#a", node_name="list-a")
        expected = List(
            root_iri="http://www.example.org/lists#a",
            list_name="list-a",
            nodes=[expected_node],
        )
        assert result == expected

    def test_with_children(self) -> None:
        list_response = {
            "list": {
                "listinfo": {
                    "id": "http://www.example.org/lists#a",
                    "name": "list-a",
                },
                "children": [
                    {
                        "id": "http://www.example.org/lists#a1",
                        "name": "node-a1",
                    },
                    {
                        "id": "http://www.example.org/lists#a2",
                        "name": "node-a2",
                    },
                ],
            }
        }
        con = ConnectionMock([list_response])
        result = _get_list_from_server(con, "")
        expected_node_root = ListNode(node_iri="http://www.example.org/lists#a", node_name="list-a")
        expected_node_1 = ListNode(node_iri="http://www.example.org/lists#a1", node_name="node-a1")
        expected_node_2 = ListNode(node_iri="http://www.example.org/lists#a2", node_name="node-a2")
        expected = List(
            root_iri="http://www.example.org/lists#a",
            list_name="list-a",
            nodes=[expected_node_root, expected_node_1, expected_node_2],
        )
        assert result == expected

    def test_multiple_levels(self) -> None:
        list_response = {
            "list": {
                "listinfo": {
                    "id": "http://www.example.org/lists#a",
                    "name": "list-a",
                },
                "children": [
                    {
                        "id": "http://www.example.org/lists#a1",
                        "name": "node-a1",
                        "children": [
                            {
                                "id": "http://www.example.org/lists#a1.1",
                                "name": "node-a1.1",
                            },
                            {
                                "id": "http://www.example.org/lists#a1.2",
                                "name": "node-a1.2",
                            },
                        ],
                    }
                ],
            }
        }
        con = ConnectionMock([list_response])
        result = _get_list_from_server(con, "")
        expected_node_root = ListNode(node_iri="http://www.example.org/lists#a", node_name="list-a")
        expected_node_1 = ListNode(node_iri="http://www.example.org/lists#a1", node_name="node-a1")
        expected_node_1_1 = ListNode(node_iri="http://www.example.org/lists#a1.1", node_name="node-a1.1")
        expected_node_1_2 = ListNode(node_iri="http://www.example.org/lists#a1.2", node_name="node-a1.2")
        expected = List(
            root_iri="http://www.example.org/lists#a",
            list_name="list-a",
            nodes=[expected_node_root, expected_node_1, expected_node_1_1, expected_node_1_2],
        )
        assert result == expected


def test_get_list_iris_from_server() -> None:
    list_iris = {
        "lists": [
            {"id": "http://www.example.org/lists#a"},
            {"id": "http://www.example.org/lists#b"},
        ]
    }
    con = ConnectionMock([list_iris])
    result = _get_list_iris_from_server(con, "")
    expected = ["http://www.example.org/lists#a", "http://www.example.org/lists#b"]
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
