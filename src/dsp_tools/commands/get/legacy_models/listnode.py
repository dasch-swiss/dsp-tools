"""
This module implements reading list nodes and lists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString
from dsp_tools.legacy_models.langstring import create_lang_string
from dsp_tools.legacy_models.langstring import create_lang_string_from_json

LISTS_ROUTE = "/admin/lists"


@dataclass(frozen=True)
class ListNode:
    """Represents a DSP list node."""

    iri: str
    name: str
    project: str | None
    label: LangString
    comments: LangString
    children: tuple[ListNode, ...]

    def to_definition_file_obj(self) -> dict[str, Any]:
        """Create an object that corresponds to the syntax of the input to 'create_onto'."""
        listnode: dict[str, Any] = {
            "name": self.name,
            "labels": self.label.to_definition_file_obj(),
        }
        if not self.comments.is_empty():
            listnode["comments"] = self.comments.to_definition_file_obj()
        if self.children:
            listnode["nodes"] = _children_to_definition_file_obj(self.children)
        return listnode


def _children_to_definition_file_obj(children: tuple[ListNode, ...]) -> list[dict[str, Any]]:
    """Convert a tuple of ListNode children to definition file format."""
    listnodeobjs: list[dict[str, Any]] = []
    for listnode in children:
        listnodeobj: dict[str, Any] = {
            "name": listnode.name,
            "labels": listnode.label.to_definition_file_obj(),
        }
        if not listnode.comments.is_empty():
            listnodeobj["comments"] = listnode.comments.to_definition_file_obj()
        if listnode.children:
            listnodeobj["nodes"] = _children_to_definition_file_obj(listnode.children)
        listnodeobjs.append(listnodeobj)
    return listnodeobjs


def create_list_node_from_json(
    con: Connection,
    json_obj: dict[str, Any],
    project_iri: str | None = None,
) -> ListNode:
    """Create a ListNode from a JSON object returned by DSP API."""
    iri = json_obj.get("id")
    if iri is None:
        raise BaseError("ListNode id is missing")

    project = json_obj.get("projectIri") or project_iri
    label = create_lang_string_from_json(json_obj.get("labels"))
    comments = create_lang_string_from_json(json_obj.get("comments"))
    name = json_obj.get("name") or iri.rsplit("/", 1)[-1]

    child_info = json_obj.get("children")
    children = _get_children(con=con, parent_iri=iri, project_iri=project, children=child_info) if child_info else ()

    return ListNode(
        iri=iri,
        name=name,
        project=project,
        label=label or create_lang_string(),
        comments=comments or create_lang_string(),
        children=children,
    )


def _get_children(
    con: Connection,
    parent_iri: str,
    project_iri: str | None,
    children: list[Any],
) -> tuple[ListNode, ...]:
    """Get a recursive tuple of children nodes."""
    child_nodes: list[ListNode] = []
    for child in children:
        if "parentNodeIri" not in child:
            child["parentNodeIri"] = parent_iri
        if "projectIri" not in child and project_iri:
            child["projectIri"] = project_iri
        child_node = create_list_node_from_json(con, child, project_iri=project_iri)
        child_nodes.append(child_node)
    return tuple(child_nodes)


def read_all_nodes(con: Connection, iri: str) -> ListNode:
    """Read all nodes of a list by its IRI."""
    result = con.get(LISTS_ROUTE + "/" + quote_plus(iri))
    if "list" not in result:
        raise BaseError("Request got no list!")
    if "listinfo" not in result["list"]:
        raise BaseError("Request got no proper list information!")

    listinfo = result["list"]["listinfo"]
    root_iri = listinfo.get("id")
    root_project = listinfo.get("projectIri")

    children_data = result["list"].get("children")
    children = (
        _get_children(con=con, parent_iri=root_iri, project_iri=root_project, children=children_data)
        if children_data
        else ()
    )

    return ListNode(
        iri=root_iri,
        name=listinfo.get("name") or root_iri.rsplit("/", 1)[-1],
        project=root_project,
        label=create_lang_string_from_json(listinfo.get("labels")) or create_lang_string(),
        comments=create_lang_string_from_json(listinfo.get("comments")) or create_lang_string(),
        children=children,
    )


def get_all_lists(con: Connection, project_iri: str | None = None) -> list[ListNode]:
    """
    Get all lists. If a project IRI is given, it returns the lists of the specified project.

    Args:
        con: Connection instance
        project_iri: IRI of project (optional)

    Returns:
        list of ListNodes (root nodes only, without children populated)
    """
    if project_iri is None:
        result = con.get(LISTS_ROUTE)
    else:
        result = con.get(LISTS_ROUTE + "?projectIri=" + quote_plus(project_iri))
    if "lists" not in result:
        raise BaseError("Request got no lists!")
    return [create_list_node_from_json(con, item) for item in result["lists"]]
