"""
This module implements reading list nodes and lists.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString


class ListNode:
    """
    This class represents a list node

    Attributes
    ----------

    iri : str
        IRI of the list node [readonly]

    project : str
        IRI of project [readonly]

    label : LangString
        A LangString instance with language dependent labels [readonly]

    comments : LangString
        A LangString instance with language dependent comments [readonly]

    name : str
        A unique name for the ListNode (unique inside this list) [readonly]

    children : list[ListNode]
        Contains a list of child nodes [readonly]

    Methods
    -------

    getAllNodes : ListNode
        Get all nodes of a list. The IRI of the root node has to be supplied.

    getAllLists [static]:
        Returns all lists of a project.

    """

    ROUTE = "/admin/lists"
    ROUTE_SLASH = ROUTE + "/"

    _con: Connection
    _id: str
    _project: str | None
    _label: LangString
    _comments: LangString
    _name: str
    _children: list[ListNode]

    def __init__(
        self,
        con: Connection,
        iri: str,
        name: str,
        project: str | None = None,
        label: LangString | None = None,
        comments: LangString | None = None,
        children: list[ListNode] | None = None,
    ) -> None:
        self._con = con
        self._id = iri
        self._name = name
        self._project = project
        self._label = label or LangString()
        self._comments = comments or LangString()
        self._children = children or []

    @property
    def iri(self) -> str:
        return self._id

    @property
    def project(self) -> str | None:
        return self._project

    @property
    def label(self) -> LangString:
        return self._label

    @property
    def comments(self) -> LangString:
        return self._comments

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> list[ListNode]:
        return self._children

    @children.setter
    def children(self, value: list[ListNode]) -> None:
        self._children = value

    @classmethod
    def _getChildren(
        cls,
        con: Connection,
        parent_iri: str,
        project_iri: str | None,
        children: list[Any],
    ) -> list[ListNode]:
        """
        Internal method! Should not be used directly!

        Gets a recursive list of children nodes.

        :param con: Valid Connection instance
        :param children: json object of children
        :return: List of ListNode instances
        """
        child_nodes: list[ListNode] = []
        for child in children:
            if "parentNodeIri" not in child:
                child["parentNodeIri"] = parent_iri
            if "projectIri" not in child and project_iri:
                child["projectIri"] = project_iri
            child_node = cls.fromJsonObj(con, child)
            child_nodes.append(child_node)
        return child_nodes

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> ListNode:
        """
        Internal method! Should not be used directly!

        This method is used to create a ListNode instance from the JSON data returned by DSP

        :param con: Connection instance
        :param json_obj: JSON data returned by DSP as python3 object
        :return: ListNode instance
        """

        iri = json_obj.get("id")
        if iri is None:
            raise BaseError("ListNode id is missing")
        project = json_obj.get("projectIri")
        label = LangString.fromJsonObj(json_obj.get("labels"))
        comments = LangString.fromJsonObj(json_obj.get("comments"))
        name = json_obj.get("name") or iri.rsplit("/", 1)[-1]

        child_info = json_obj.get("children")
        children = (
            cls._getChildren(con=con, parent_iri=iri, project_iri=project, children=child_info) if child_info else []
        )

        return cls(
            con=con,
            iri=iri,
            name=name,
            project=project,
            label=label,
            comments=comments,
            children=children,
        )

    def getAllNodes(self) -> ListNode:
        """
        Get all nodes of the list. Must be called from a ListNode instance that has at least set the
        list iri!

        :return: Root node of list with recursive ListNodes ("children"-attributes)
        """
        return ListNode.read_all_nodes(self._con, self._id)

    @classmethod
    def read_all_nodes(cls, con: Connection, iri: str) -> ListNode:
        """Read all nodes of a list by its IRI."""
        result = con.get(cls.ROUTE_SLASH + quote_plus(iri))
        if "list" not in result:
            raise BaseError("Request got no list!")
        if "listinfo" not in result["list"]:
            raise BaseError("Request got no proper list information!")
        root = cls.fromJsonObj(con, result["list"]["listinfo"])
        if "children" in result["list"]:
            root.children = cls._getChildren(
                con=con, parent_iri=root.iri, project_iri=root.project, children=result["list"]["children"]
            )
        return root

    @staticmethod
    def getAllLists(con: Connection, project_iri: str | None = None) -> list[ListNode]:
        """
        Get all lists. If a project IRI is given, it returns the lists of the specified project

        :param con: Connection instance
        :param project_iri: Iri/id of project
        :return: list of ListNodes
        """
        if project_iri is None:
            result = con.get(ListNode.ROUTE)
        else:
            result = con.get(ListNode.ROUTE + "?projectIri=" + quote_plus(project_iri))
        if "lists" not in result:
            raise BaseError("Request got no lists!")
        return list(map(lambda a: ListNode.fromJsonObj(con, a), result["lists"]))

    def _createDefinitionFileObj(self, children: list[ListNode]) -> list[dict[str, Any]]:
        """
        Create an object that corresponds to the syntax of the input to "create_onto".
        Node: This method must be used only internally (for recursion)!!

        :param children: List of children nodes
        :return: A python object that can be jsonfied to correspond to the syntax of the input to "create_onto".
        """
        listnodeobjs: list[dict[str, Any]] = []
        for listnode in children:
            listnodeobj: dict[str, Any] = {
                "name": listnode.name,
                "labels": listnode.label.createDefinitionFileObj(),
            }
            if not listnode.comments.isEmpty():
                listnodeobj["comments"] = listnode.comments.createDefinitionFileObj()
            if listnode.children:
                listnodeobj["nodes"] = self._createDefinitionFileObj(listnode.children)
            listnodeobjs.append(listnodeobj)
        return listnodeobjs

    def createDefinitionFileObj(self) -> dict[str, Any]:
        """
        Create an object that corresponds to the syntax of the input to "create_onto".
        :return: A python object that can be jsonfied to correspond to the syntax of the input to "create_onto".
        """
        listnode: dict[str, Any] = {
            "name": self._name,
            "labels": self._label.createDefinitionFileObj(),
        }
        if not self._comments.isEmpty():
            listnode["comments"] = self._comments.createDefinitionFileObj()
        if self._children:
            listnode["nodes"] = self._createDefinitionFileObj(self._children)
        return listnode
