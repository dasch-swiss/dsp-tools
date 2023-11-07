from dataclasses import dataclass
from test.unittests.helpers.connection_mock import ConnectionMockBase
from typing import Any

from dsp_tools.utils.xmlupload.list_client import ListClientLive

# pylint: disable=missing-class-docstring,missing-function-docstring,unused-argument


@dataclass
class ConnectionMock(ConnectionMockBase):
    get_responses: list[dict[str, Any]]

    def get(self, route: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        return self.get_responses.pop(0)


def test_list_root_without_name() -> None:
    list_iris = {"lists": [{"id": "http://www.example.org/lists#a"}]}
    list_a = {
        "list": {
            "listinfo": {
                "id": "http://www.example.org/lists#a",
                "labels": [{"value": "some label"}],
            },
            "children": [],
        }
    }
    con = ConnectionMock([list_iris, list_a])
    list_client = ListClientLive(con, "")
    lookup = list_client.get_list_node_id_to_iri_lookup()
    expected = {"some label:some label": "http://www.example.org/lists#a"}
    assert lookup == expected


def test_list_root_with_name() -> None:
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


def test_list_with_children() -> None:
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


def test_list_with_multiple_levels() -> None:
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
                    "children": [
                        {
                            "id": "http://www.example.org/lists#a2.1",
                            "name": "node-a2.1",
                        },
                        {
                            "id": "http://www.example.org/lists#a2.2",
                            "name": "node-a2.2",
                        },
                    ],
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
        "list-a:node-a2.1": "http://www.example.org/lists#a2.1",
        "list-a:node-a2.2": "http://www.example.org/lists#a2.2",
    }
    assert lookup == expected


def test_multiple_lists() -> None:
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
