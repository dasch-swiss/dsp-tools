from __future__ import annotations

from dataclasses import dataclass, field
from itertools import chain, groupby
from typing import Any, Protocol
from urllib.parse import quote_plus

import requests

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ListNode:
    """Information about a list."""

    root_iri: str
    node_iri: str
    node_name: str


@dataclass(frozen=True)
class ProjectLists:
    """Information about the lists of a project."""

    lists: dict[str, list[ListNode]]


class ListClient(Protocol):
    """Interface (protocol) for list-related requests to the DSP-API."""

    def get_list_node_iri_lookup(self) -> dict[str, str]:
        """Get a lookup of list node names to IRIs."""


@dataclass
class ListClientLive:
    """Client handling list-related requests to the DSP-API."""

    server: str
    project_iri: str
    list_info: ProjectLists | None = field(init=False, default=None)

    def get_list_node_iri_lookup(self) -> dict[str, str]:
        """Get a lookup of list node names to IRIs."""
        if not self.list_info:
            self.list_info = _get_list_info_from_server(self.server, self.project_iri)
        return {node.node_name: node.node_iri for l in self.list_info.lists.values() for node in l}


def _get_list_info_from_server(server: str, project_iri: str) -> ProjectLists:
    logger.info(f"Retrieving lists of project {project_iri}")
    list_iris = _get_list_iris_from_server(server, project_iri)
    list_nodes = [_get_list_nodes_from_server(server, list_iri) for list_iri in list_iris]
    list_info = {k: list(v) for k, v in groupby(chain.from_iterable(list_nodes), lambda node: node.root_iri)}
    return ProjectLists(list_info)


def _get_list_iris_from_server(server: str, project_iri: str) -> list[str]:
    iri = quote_plus(project_iri)
    res = requests.get(f"{server}/admin/lists?projectIri={iri}", timeout=5)
    if res.status_code != 200:
        raise BaseError(f"Could not retrieve lists of project {project_iri}")
    lists: list[dict[str, Any]] = res.json()["lists"]
    logger.info(f"Found {len(lists)} lists for project")
    return [l["id"] for l in lists]


def _get_list_nodes_from_server(server: str, list_iri: str) -> list[ListNode]:
    logger.info(f"Retrieving nodes of list {list_iri}")
    iri = quote_plus(list_iri)
    res = requests.get(f"{server}/admin/lists/{iri}", timeout=5)
    if res.status_code != 200:
        raise BaseError(f"Could not retrieve nodes of list {list_iri}")
    list_object: dict[str, Any] = res.json()["list"]
    list_info = list_object["listinfo"]
    children: list[dict[str, Any]] = list_object["children"]
    root_iri = list_info["id"]
    root_node = ListNode(root_iri=root_iri, node_iri=root_iri, node_name=list_info["name"])
    child_nodes = _children_to_nodes(children, root_iri)
    return [root_node] + child_nodes


def _children_to_nodes(children: list[dict[str, Any]], root_iri: str) -> list[ListNode]:
    nodes = []
    for child in children:
        node_iri = child["id"]
        node_name = child["name"]
        nodes.append(ListNode(root_iri=root_iri, node_iri=node_iri, node_name=node_name))
        if child["children"]:
            nodes.extend(_children_to_nodes(child["children"], root_iri))
    return nodes
