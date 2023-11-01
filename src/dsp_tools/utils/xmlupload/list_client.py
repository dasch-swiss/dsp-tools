from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol
from urllib.parse import quote_plus

import requests

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger

# pylint: disable=too-few-public-methods

logger = get_logger(__name__)


@dataclass(frozen=True)
class ListNode:
    """Information about a list node."""

    node_iri: str
    node_name: str


@dataclass(frozen=True)
class List:
    """Information about a list."""

    root_iri: str
    list_name: str
    children: list[ListNode]


@dataclass(frozen=True)
class ProjectLists:
    """Information about the lists of a project."""

    lists: list[List]


class ListClient(Protocol):
    """Interface (protocol) for list-related requests to the DSP-API."""

    def get_list_node_id_to_iri_lookup(self) -> dict[str, str]:
        """Get a lookup of list node names to IRIs."""


@dataclass
class ListClientLive:
    """Client handling list-related requests to the DSP-API."""

    server: str
    project_iri: str
    list_info: ProjectLists | None = field(init=False, default=None)

    def get_list_node_id_to_iri_lookup(self) -> dict[str, str]:
        """
        Get a mapping of list node IDs to their respective IRIs.
        A list node ID is structured as follows:
        <list name>:<node name> where the list name is the node name of the root node.
        """
        if not self.list_info:
            self.list_info = _get_list_info_from_server(self.server, self.project_iri)
        return dict(_get_node_tuples(self.list_info.lists))


def _get_node_tuples(lists: list[List]) -> Iterable[tuple[str, str]]:
    for l in lists:
        list_name = l.list_name
        for node in l.children:
            node_name = node.node_name
            node_id = f"{list_name}:{node_name}"
            yield node_id, node.node_iri


def _get_list_info_from_server(server: str, project_iri: str) -> ProjectLists:
    logger.info(f"Retrieving lists of project {project_iri}")
    list_iris = _get_list_iris_from_server(server, project_iri)
    lists = [_get_list_from_server(server, list_iri) for list_iri in list_iris]
    return ProjectLists(lists)


def _get_list_iris_from_server(server: str, project_iri: str) -> list[str]:
    iri = quote_plus(project_iri)
    res = requests.get(f"{server}/admin/lists?projectIri={iri}", timeout=5)
    if res.status_code != 200:
        raise BaseError(f"Could not retrieve lists of project {project_iri}")
    lists: list[dict[str, Any]] = res.json()["lists"]
    logger.info(f"Found {len(lists)} lists for project")
    return [l["id"] for l in lists]


def _get_list_from_server(server: str, list_iri: str) -> List:
    logger.info(f"Retrieving nodes of list {list_iri}")
    iri = quote_plus(list_iri)
    res = requests.get(f"{server}/admin/lists/{iri}", timeout=5)
    if res.status_code != 200:
        raise BaseError(f"Could not retrieve nodes of list {list_iri}")
    list_object: dict[str, Any] = res.json()["list"]
    list_info = list_object["listinfo"]
    children: list[dict[str, Any]] = list_object["children"]
    root_iri = list_info["id"]
    list_name = list_info["name"]
    root_node = ListNode(root_iri, list_name)
    nodes = [root_node] + _children_to_nodes(children)
    return List(root_iri, list_name, nodes)


def _children_to_nodes(children: list[dict[str, Any]]) -> list[ListNode]:
    nodes = []
    for child in children:
        node_iri = child["id"]
        node_name = child["name"]
        nodes.append(ListNode(node_iri=node_iri, node_name=node_name))
        if child["children"]:
            nodes.extend(_children_to_nodes(child["children"]))
    return nodes
