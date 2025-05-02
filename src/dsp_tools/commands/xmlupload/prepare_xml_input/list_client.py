from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Protocol
from urllib.parse import quote_plus

from loguru import logger

from dsp_tools.clients.connection import Connection


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
    nodes: list[ListNode]


@dataclass(frozen=True)
class ProjectLists:
    """Information about the lists of a project."""

    lists: list[List]


class ListClient(Protocol):
    """Interface (protocol) for list-related requests to the DSP-API."""

    def get_list_node_id_to_iri_lookup(self) -> dict[tuple[str, str], str]:
        """Get a lookup of list node names to IRIs."""


@dataclass
class ListClientLive:
    """Client handling list-related requests to the DSP-API."""

    con: Connection
    project_iri: str
    list_info: ProjectLists | None = field(init=False, default=None)

    def get_list_node_id_to_iri_lookup(self) -> dict[tuple[str, str], str]:
        """
        Get a mapping of list node IDs to their respective IRIs.
        A list node ID is structured as follows:
        `("<list name>", "<node name>") where the list name is the node name of the root node.

        Returns:
            The mapping of list node IDs to IRIs.
        """
        if not self.list_info:
            self.list_info = _get_list_info_from_server(self.con, self.project_iri)
        lookup = dict(_get_node_tuples(self.list_info.lists))
        # Enable referencing list node IRIs in the XML:
        # add a reference of the list node IRIs to themselves (with empty list names)
        lookup.update({("", v): v for v in lookup.values()})
        return lookup


def _get_node_tuples(lists: list[List]) -> Iterable[tuple[tuple[str, str], str]]:
    for lst in lists:
        list_name = lst.list_name
        for node in lst.nodes:
            yield (list_name, node.node_name), node.node_iri


def _get_list_info_from_server(con: Connection, project_iri: str) -> ProjectLists:
    logger.info(f"Retrieving lists of project {project_iri}")
    list_iris = _get_list_iris_from_server(con, project_iri)
    lists = [_get_list_from_server(con, list_iri) for list_iri in list_iris]
    return ProjectLists(lists)


def _get_list_iris_from_server(con: Connection, project_iri: str) -> list[str]:
    iri = quote_plus(project_iri)
    res = con.get(f"/admin/lists?projectIri={iri}")
    lists: list[dict[str, Any]] = res["lists"]
    logger.info(f"Found {len(lists)} lists for project")
    return [lst["id"] for lst in lists]


def _get_list_from_server(con: Connection, list_iri: str) -> List:
    logger.info(f"Retrieving nodes of list {list_iri}")
    iri = quote_plus(list_iri)
    res = con.get(f"/admin/lists/{iri}")
    list_object: dict[str, Any] = res["list"]
    list_info = list_object["listinfo"]
    children: list[dict[str, Any]] = list_object["children"]
    root_iri = list_info["id"]
    # if the root node does not have a name, use the label instead
    list_name: str = list_info.get("name") or list_info["labels"][0]["value"]
    root_node = ListNode(root_iri, list_name)
    nodes = [root_node, *_children_to_nodes(children)]
    return List(root_iri, list_name, nodes)


def _children_to_nodes(children: list[dict[str, Any]]) -> list[ListNode]:
    nodes = []
    for child in children:
        node_iri = child["id"]
        node_name = child["name"]
        nodes.append(ListNode(node_iri=node_iri, node_name=node_name))
        if "children" in child:
            nodes.extend(_children_to_nodes(child["children"]))
    return nodes
