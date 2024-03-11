"""
This module implements the handling (CRUD) of list nodes and adds some function to read whole lists.

CREATE:
    * Instantiate a new object of the class ListNode
    * Call the ``create`` method on the instance

READ:
    * Instantiate a new object with ``iri`` (IRI of listnode)
    * Call the ``read`` method on the instance
    * Access information about the instance
"""

from __future__ import annotations

from typing import Any
from typing import Optional
from typing import Union
from urllib.parse import quote_plus

from dsp_tools.commands.project.models.model import Model
from dsp_tools.commands.project.models.project import Project
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.langstring import LangString
from dsp_tools.utils.connection import Connection


class ListNode(Model):
    """
    This class represents a list node

    Attributes
    ----------

    con : Connection
        A Connection instance to a DSP server (for some operation a login has to be performed with valid credentials)

    iri : str
        IRI of the list node [readonly, cannot be modified after creation of instance]

    project : str
        IRI of project. Only used for the creation of a new list (root node) [write].

    label : LangString
        A LangString instance with language dependent labels. Setting this attribute overwrites all entries
        with the new ones.
        At least one label is required [read/write].

    comments : LangString
        A LangString instance with language dependent comments. Setting this attributes overwrites all entries
        with the new ones.

    name : str
        A unique name for the ListNode (unique inside this list) [read/write].

    parent : IRI | ListNode
        Is required and allowed only for the CREATE operation. Otherwise use the
        "children" attribute [write].

    isRootNode : bool
        Is True if the ListNode is the root node of a list. Cannot be set [read].

    children : list[ListNode]
        Contains a list of child nodes. This attribute is only available for nodes that have been read by the
        method "getAllNodes()" [read].

    rootNodeIri : str
        IRI of the root node. This attribute is only available for nodes that have been read by the
        method "getAllNodes()" [read].

    Methods
    -------

    create : ListNode information object
        Creates a new list (node) and returns the information from the list (node). Use it to create new lists
        or append new ListNodes to an existing list.

    read : ListNode information object
        Returns information about a single list node

    getAllNodes : ListNode
        Get all nodes of a list. The IRI of the root node has to be supplied.

    getAllLists [static]:
        Returns all lists of a project.

    print : None
        Prints the ListNode information to stdout (not recursive)

    """

    ROUTE = "/admin/lists"
    ROUTE_SLASH = ROUTE + "/"

    _id: Optional[str]
    _project: Optional[str]
    _label: Optional[LangString]
    _comments: Optional[LangString]
    _name: Optional[str]
    _parent: Optional[str]
    _isRootNode: bool
    _children: Optional[list[ListNode]]
    _rootNodeIri: Optional[str]

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        project: Optional[Union[Project, str]] = None,
        label: Optional[LangString] = None,
        comments: Optional[LangString] = None,
        name: Optional[str] = None,
        parent: Optional[Union[ListNode, str]] = None,
        isRootNode: bool = False,
        children: Optional[list[ListNode]] = None,
        rootNodeIri: Optional[str] = None,
    ) -> None:
        """
        This is the constructor for the ListNode object. For

        CREATE:
            * The "con" and at least one "label" are required
        READ:
            * The "con" and "iri" attributes are required

        Args:
            con: A valid Connection instance with a user logged in that has the appropriate permissions
            iri: IRI of the project [readonly, cannot be modified after creation of instance]
            project: IRI of project. Only used for the creation of a new list (root node) [write].
            label: LangString with lang dependent labels. At least one label is required [read/write].
            comments:  A LangString instance with language dependent comments.
            name: A unique name for the ListNode (unique regarding the whole list) [read/write].
            parent: Required and allowed only for the CREATE operation. Otherwise use the "children" attribute [write].
            isRootNode: Is True if the ListNode is a root node of a list Cannot be set [read].
            children: list of children nodes. Only available for nodes that have been read by getAllNodes()
            rootNodeIri: IRI of the root node. Only available for nodes that have been read by the method getAllNodes()
        """

        super().__init__(con)

        self._project = project.iri if isinstance(project, Project) else str(project) if project else None
        self._id = iri
        self._label = LangString(label)
        self._comments = LangString(comments) if comments else None
        self._name = name
        if parent and isinstance(parent, ListNode):
            self._parent = parent.iri
        else:
            self._parent = str(parent) if parent else None
        self._isRootNode = isRootNode
        if children:
            if isinstance(children, list) and len(children) > 0 and isinstance(children[0], ListNode):
                self._children = children
            else:
                raise BaseError("ERROR Children must be list of ListNodes!")
        else:
            self._children = None
        if not isinstance(rootNodeIri, str) and rootNodeIri:
            raise BaseError("ERROR rootNodeIri must be of type string")
        self._rootNodeIri = rootNodeIri

    @property
    def iri(self) -> Optional[str]:
        return self._id

    @property
    def project(self) -> Optional[str]:
        return self._project

    @project.setter
    def project(self, value: str) -> None:
        if self._project:
            raise BaseError("Project id cannot be modified!")
        else:
            self._project = value

    @property
    def label(self) -> LangString:
        return self._label or LangString({})

    @label.setter
    def label(self, value: Optional[Union[LangString, str]]) -> None:
        self._label = LangString(value)
        self._changed.add("label")

    @property
    def comments(self) -> LangString:
        return self._comments or LangString({})

    @comments.setter
    def comments(self, value: Optional[Union[LangString, str]]) -> None:
        self._comments = LangString(value)
        self._changed.add("comments")

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        self._changed.add("name")

    @property
    def parent(self) -> Optional[str]:
        return self._parent if self._parent else None

    @parent.setter
    def parent(self, value: Union[str, ListNode]) -> None:
        if isinstance(value, ListNode):
            self._parent = value.iri
        else:
            self._parent = value

    @property
    def isRootNode(self) -> Optional[bool]:
        return self._isRootNode

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

    @property
    def rootNodeIri(self) -> Optional[str]:
        return self._rootNodeIri

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
        parent = json_obj.get("parentNodeIri")
        isRootNode = json_obj.get("isRootNode")

        child_info = json_obj.get("children")
        children = None
        if child_info:
            children = ListNode.__getChildren(con=con, parent_iri=iri, project_iri=project, children=child_info)
        rootNodeIri = json_obj.get("hasRootNode")

        return cls(
            con=con,
            iri=iri,
            project=project,
            label=label,
            comments=comments,
            name=name,
            parent=parent,
            isRootNode=isRootNode,
            children=children,
            rootNodeIri=rootNodeIri,
        )

    def create(self) -> ListNode:
        """
        Create a new List

        :return: JSON-object from DSP-API
        """
        jsonobj = self._toJsonObj_create()
        if self._parent:
            result = self._con.post(ListNode.ROUTE_SLASH + quote_plus(self._parent), jsonobj)
            return ListNode.fromJsonObj(self._con, result["nodeinfo"])
        else:
            result = self._con.post(ListNode.ROUTE, jsonobj)
            return ListNode.fromJsonObj(self._con, result["list"]["listinfo"])

    def _toJsonObj_create(self):
        tmp = {}
        if self._project is None:
            raise BaseError("There must be a project id given!")
        tmp["projectIri"] = self._project
        if self._label.isEmpty():
            raise BaseError("There must be a valid ListNode label!")
        tmp["labels"] = self._label.toJsonObj()
        if self._comments:
            tmp["comments"] = self._comments.toJsonObj()
        if self._name:
            tmp["name"] = self._name
        if self._parent:
            tmp["parentNodeIri"] = self._parent
        return tmp

    def read(self) -> Any:
        """
        Read a project from DSP-API

        :return: JSON-object from DSP-API
        """

        result = self._con.get(ListNode.ROUTE_SLASH + "nodes/" + quote_plus(self._id))
        if result.get("nodeinfo"):
            return self.fromJsonObj(self._con, result["nodeinfo"])
        elif result.get("listinfo"):
            return self.fromJsonObj(self._con, result["listinfo"])
        else:
            return None

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
