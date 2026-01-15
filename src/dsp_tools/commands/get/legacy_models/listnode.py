"""
This module implements reading list nodes and lists.
"""

from __future__ import annotations

from typing import Any
from typing import Optional
from typing import Union
from urllib.parse import quote_plus

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.project import Project
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString


class ListNode:
    """
    This class represents a list node

    Attributes
    ----------

    con : Connection
        A Connection instance to a DSP server

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

    parent : str
        IRI of parent node [readonly]

    isRootNode : bool
        Is True if the ListNode is the root node of a list [readonly]

    children : list[ListNode]
        Contains a list of child nodes. This attribute is only available for nodes that have been read by the
        method "getAllNodes()" [readonly]

    rootNodeIri : str
        IRI of the root node. This attribute is only available for nodes that have been read by the
        method "getAllNodes()" [readonly]

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
    _id: Optional[str]
    _project: Optional[str]
    _label: Optional[LangString]
    _comments: Optional[LangString]
    _name: Optional[str]
    _children: Optional[list[ListNode]]

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        project: Optional[Union[Project, str]] = None,
        label: Optional[LangString] = None,
        comments: Optional[LangString] = None,
        name: Optional[str] = None,
        children: Optional[list[ListNode]] = None,
    ) -> None:
        self._con = con

        self._project = project.iri if isinstance(project, Project) else str(project) if project else None
        self._id = iri
        self._label = LangString(label)
        self._comments = LangString(comments) if comments else None
        self._name = name
        if children:
            if isinstance(children, list) and len(children) > 0 and isinstance(children[0], ListNode):
                self._children = children
            else:
                raise BaseError("ERROR Children must be list of ListNodes!")
        else:
            self._children = None

    @property
    def iri(self) -> Optional[str]:
        return self._id

    @property
    def project(self) -> Optional[str]:
        return self._project

    @property
    def label(self) -> LangString:
        return self._label or LangString({})

    @property
    def comments(self) -> LangString:
        return self._comments or LangString({})

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def children(self) -> list[ListNode]:
        return self._children or []

    @children.setter
    def children(self, value: list[ListNode]) -> None:
        self._children = value

    @staticmethod
    def __getChildren(
        con: Connection,
        parent_iri: str,
        project_iri: str,
        children: list[Any],
    ) -> Optional[list[ListNode]]:
        """
        Internal method! Should not be used directly!

        Static method gets a recursive List of children nodes

        :param con: Valid Connection instance
        :param children: json object of children
        :return: List of ListNode instances
        """
        if children:
            child_nodes: list[Any] = []
            for child in children:
                if "parentNodeIri" not in child:
                    child["parentNodeIri"] = parent_iri
                if "projectIri" not in child:
                    child["projectIri"] = project_iri
                child_node = ListNode.fromJsonObj(con, child)
                child_nodes.append(child_node)
            return child_nodes
        else:
            return None

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
        if json_obj.get("name"):
            name = json_obj["name"]
        else:
            name = iri.rsplit("/", 1)[-1]

        child_info = json_obj.get("children")
        children = None
        if child_info:
            children = ListNode.__getChildren(con=con, parent_iri=iri, project_iri=project, children=child_info)

        return cls(
            con=con,
            iri=iri,
            project=project,
            label=label,
            comments=comments,
            name=name,
            children=children,
        )

    def getAllNodes(self) -> ListNode:
        """
        Get all nodes of the list. Must be called from a ListNode instance that has at least set the
        list iri!

        :return: Root node of list with recursive ListNodes ("children"-attributes)
        """

        result = self._con.get(ListNode.ROUTE_SLASH + quote_plus(self._id))
        if "list" not in result:
            raise BaseError("Request got no list!")
        if "listinfo" not in result["list"]:
            raise BaseError("Request got no proper list information!")
        root = ListNode.fromJsonObj(self._con, result["list"]["listinfo"])
        if "children" in result["list"]:
            root.children = ListNode.__getChildren(
                con=self._con, parent_iri=root.iri, project_iri=root.project, children=result["list"]["children"]
            )
        return root

    @staticmethod
    def getAllLists(con: Connection, project_iri: Optional[str] = None) -> list[ListNode]:
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
        listnodeobjs = []
        for listnode in children:
            listnodeobj = {
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
        listnode = {
            "name": self._name,
            "labels": self._label.createDefinitionFileObj(),
        }
        if not self._comments.isEmpty():
            listnode["comments"] = self._comments.createDefinitionFileObj()
        if self._children:
            listnode["nodes"] = self._createDefinitionFileObj(self._children)
        return listnode
