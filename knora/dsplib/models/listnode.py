import json
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union, NewType
from urllib.parse import quote_plus

from .helpers import Actions, BaseError
from .langstring import Languages, LangStringParam, LangString
from .connection import Connection
from .project import Project

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

"""
This module implements the handling (CRUD) of Knora ListNodes and adds some function to read whole lists.

CREATE:
    * Instantiate a new object of the class ListNode with all required parameters
    * Call the ``create``-method on the instance

READ:
    * Instantiate a new object with ``id``(IRI of list(-node) given
    * Call the ``read``-method on the instance
    * Access the information that has been provided to the instance

UPDATE:
    * Only partially implemented. Only "label" and "comment" attributes may be changed.
    * You need an instance of an existing ListNode by reading an instance
    * Change the attributes by assigning the new values
    * Call the ``update```method on the instance

DELETE
    * NOT YET IMPLEMENTED BY Knora backend!
    * Instantiate a new objects with ``id``(IRI of project) given, or use any instance that has the id set
    * Call the ``delete``-method on the instance

In addition there is a static methods ``getAllProjects`` which returns a list of all projects
"""


@strict
class ListNode:
    """
    This class represents a list node or a while list from Knora

    Attributes
    ----------

    con : Connection
        A Connection instance to a Knora server (for some operation a login has to be performedwith valid credentials)

    id : str
        IRI of the project [readonly, cannot be modified after creation of instance]

    project : str
        IRI of project. Only used for the creation of a new list (root node) [write].

    label : LangString
        A LangString instance with language depenedent labels. Setting this attributes overwites all entries
        with the new ones. In order to add/remove a specific entry, use "addLabel" or "rmLabel".
        At least one label is required [read/write].

    comment : LangString
        A LangString instance with language depenedent comments. Setting this attributes overwites all entries
        with the new ones.In order to add/remove a specific entry, use "addComment" or "rmComment".

    name : str
        A unique name for the ListNode (unique regarding the whole list) [read/write].

    parent : IRI | ListNode
        Is required and allowed only for the CREATE operation. Otherwise use the
        "children" attribute [write].

    isRootNode : bool
        Is True if the ListNode is a root node of a list Cannot be set [read].

    children : List[ListNode]
        Contains a list of children nodes. This attribute is only avaliable for nodes that have been read by the
        method "getAllNodes()"! [read]

    rootNodeIri : str
        IRI of the root node. This attribute is only avaliable for nodes that have been read by the
        method "getAllNodes()"! [read]

    Methods
    -------

    create : Knora ListNode information object
        Creates a new project and returns the information from the project as it is in Knora. Used to create new lists
        or append new ListNodes to an existing list. If appending, the attribute "parent" must not be None!

    read : Knora ListNode information object
        Read single list node

    update : Knora ListNode information object
        Updates the changed attributes and returns the updated information from the ListNode as it is in Knora

    delete : Knora result code
        Deletes a ListNode and returns the result code [NOT YET IMPLEMENTED!]

    getAllNodes : ListNode
        Get all nodes of a list. The IRI of the root node must be supplied.

    getAllLists [static]:
        returns all lists of a given project.

    print : None
        Prints the ListNode information to stdout (no recursion for children!)

    """

    __id: Union[str, None]
    __project: Union[str, None]
    __label: LangString
    __comment: LangString
    __name: Union[str, None]
    __parent: Union[str, None]
    __isRootNode: bool
    __children: Union[List['ListNode'], None]
    __rootNodeIri: Union[str, None]
    __changed: Set[str]

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 project: Optional[Union[Project, str]] = None,
                 label: LangStringParam = None,
                 comment: LangStringParam = None,
                 name: Optional[str] = None,
                 parent: Optional[Union['ListNode', str]] = None,
                 isRootNode: Optional[bool] = None,
                 children: Optional[List['ListNode']] = None,
                 rootNodeIri: Optional[str] = None):
        """
        This is the constructor for the ListNode object. For

        CREATE:
            * The "con" and at least one "label" are required
        READ:
            * The "con" and "id" attributes are required
        UPDATE:
            * Only "label", "comment" and "name" may be changed
        DELETE:
            * Not yet implemented in the Knora-backend

        :param con: A valid Connection instance with a user logged in that has the appropriate permissions
        :param id: IRI of the project [readonly, cannot be modified after creation of instance]
        :param project: IRI of project. Only used for the creation of a new list (root node) [write].
        :param label: A LangString instance with language depenedent labels. Setting this attributes overwites all entries with the new ones. In order to add/remove a specific entry, use "addLabel" or "rmLabel". At least one label is required [read/write].
        :param comment: A LangString instance with language depenedent comments. Setting this attributes overwites all entries with the new ones.In order to add/remove a specific entry, use "addComment" or "rmComment".
        :param name: A unique name for the ListNode (unique regarding the whole list) [read/write].
        :param parent: Is required and allowed only for the CREATE operation. Otherwise use the "children" attribute [write].
        :param isRootNode: Is True if the ListNode is a root node of a list Cannot be set [read].
        :param children: Contains a list of children nodes. This attribute is only avaliable for nodes that have been read by the method "getAllNodes()"! [read]
        :param rootNodeIri: IRI of the root node. This attribute is only avaliable for nodes that have been read by the method "getAllNodes()"! [read]
        """

        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        self.con = con

        self.__project = project.id if isinstance(project, Project) else str(project) if project is not None else None
        self.__id = str(id) if id is not None else None
        self.__label = LangString(label)
        self.__comment = LangString(comment)
        self.__name = str(name) if name is not None else None
        if parent and isinstance(parent, ListNode):
            self.__parent = parent.id
        else:
            self.__parent = str(parent) if parent else None
        self.__isRootNode = isRootNode
        if children is not None:
            if isinstance(children, List) and len(children) > 0 and isinstance(children[0], ListNode):
                self.__children = children
            else:
                raise BaseError('Children must be list of ListNodes!')
        else:
            self.__children = None
        if not isinstance(rootNodeIri, str) and rootNodeIri is not None:
            raise BaseError('rootNodeIri must be a str!')
        self.__rootNodeIri = rootNodeIri
        self.__changed = set()

    #
    # Here follows a list of getters/setters
    #
    @property
    def id(self) -> Optional[str]:
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('ListNode id cannot be modified!')

    @property
    def project(self) -> Optional[str]:
        return self.__project

    @project.setter
    def project(self, value: str) -> None:
        if self.__project:
            raise BaseError('Project id cannot be modified!')
        else:
            self.__project = value

    @property
    def label(self) -> Optional[LangString]:
        return self.__label

    @label.setter
    def label(self, value: Optional[Union[LangString, str]]) -> None:
        self.__label = LangString(value)
        self.__changed.add('label')

    def addLabel(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a node label with the given language (executed at next update)

        :param lang: The language the label, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the label
        :return: None
        """

        self.__label[lang] = value
        self.__changed.add('label')

    def rmLabel(self, lang: Union[Languages, str]) -> None:
        """
        Remove a label from a list node (executed at next update)

        :param lang: The language the label to be removed is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :return: None
        """
        del self.__label[lang]
        self.__changed.add('label')

    @property
    def comment(self) -> Optional[LangString]:
        return self.__comment

    @comment.setter
    def comment(self,  value: Optional[Union[LangString, str]]) -> None:
        self.__comment = LangString(value)
        self.__changed.add('comment')

    def addComment(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a node comment with the given language (executed at next update)

        :param lang: The language the comment, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the comment
        :return: None
        """

        self.__comment[lang] = value
        self.__changed.add('comment')

    def rmComment(self, lang: Union[Languages, str]) -> None:
        """
        Remove a comment from a list node (executed at next update)

        :param lang: The language the comment to be removed is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :return: None
        """
        del self.__comment[lang]
        self.__changed.add('comment')

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = str(value)
        self.__changed.add('name')

    @property
    def parent(self) -> Optional[str]:
        return self.__parent if self.__parent else None

    @parent.setter
    def parent(self, value: Union[str, 'ListNode']):
        if isinstance(value, ListNode):
            self.__parent = value.id
        else:
            self.__parent = value

    @property
    def isRootNode(self) -> Optional[bool]:
        return self.__isRootNode

    @isRootNode.setter
    def isRootNode(self, value: bool) -> None:
        raise BaseError('Property isRootNode cannot be set!')

    @property
    def children(self) -> Optional[List['ListNode']]:
        return self.__children

    @staticmethod
    def __getChildren(con: Connection,
                      parent_iri: str,
                      project_iri: str,
                      children: List[Any]) -> Optional[List['ListNode']]:
        """
        Internal method! Should not be used directly!

        Static method gets a recursive List of children nodes

        :param con: Valid Connection instance
        :param children: json object of children
        :return: List of ListNode instances
        """
        if children:
            child_nodes: List[Any] = []
            for child in children:

                if 'parentNodeIri' not in child:
                    child['parentNodeIri'] = parent_iri
                if 'projectIri' not in child:
                    child['projectIri'] = project_iri
                child_node = ListNode.fromJsonObj(con, child)
                child_nodes.append(child_node)
            return child_nodes
        else:
            return None

    @property
    def rootNodeIri(self) -> Optional[str]:
        return self.__rootNodeIri

    @rootNodeIri.setter
    def rootNodeIri(self, value: str):
        raise BaseError('rootNodeIri cannot be set!')

    def has_changed(self) -> bool:
        if self.__changed:
            return True
        else:
            return False

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> Any:
        """
        Internal method! Should not be used directly!

        This method is used to create a ListNode instance from the JSON data returned by Knora

        :param con: Connection instance
        :param json_obj: JSON data returned by Knora as python3 object
        :return: ListNode instance
        """

        id = json_obj.get('id')
        if id is None:
            raise BaseError('ListNode id is missing')
        project = json_obj.get('projectIri')
        label = LangString.fromJsonObj(json_obj.get('labels'))
        comment = LangString.fromJsonObj(json_obj.get('comments'))
        name = json_obj.get('name')
        parent = json_obj.get('parentNodeIri')
        isRootNode = json_obj.get('isRootNode')

        child_info = json_obj.get('children')
        children = None
        if child_info is not None:
            children = ListNode.__getChildren(con=con,
                                              parent_iri=id,
                                              project_iri=project,
                                              children=child_info)
        rootNodeIri = json_obj.get('hasRootNode')

        return cls(con=con,
                   id=id,
                   project=project,
                   label=label,
                   comment=comment,
                   name=name,
                   parent=parent,
                   isRootNode=isRootNode,
                   children=children,
                   rootNodeIri=rootNodeIri)

    def toJsonObj(self, action: Actions, listIri: str = None) -> Any:
        """
        Internal method! Should not be used directly!

        Creates a JSON-object from the ListNode instance that can be used to call Knora

        :param action: Action the object is used for (Action.CREATE or Action.UPDATE)
        :return: JSON-object
        """

        tmp = {}
        if action == Actions.Create:
            if self.__project is None:
                raise BaseError("There must be a project id given!")
            tmp['projectIri'] = self.__project
            if self.__label.isEmpty():
                raise BaseError("There must be a valid ListNode label!")
            tmp['labels'] = self.__label.toJsonObj()
            if not self.__comment.isEmpty():
                tmp['comments'] = self.__comment.toJsonObj()
            else:
                tmp['comments'] = []
            if self.__name is not None:
                tmp['name'] = self.__name
            if self.__parent is not None:
                tmp['parentNodeIri'] = self.__parent
        elif action == Actions.Update:
            if self.id is None:
                raise BaseError("There must be a node id given!")
            tmp['listIri'] = listIri
            if self.__project is None:
                raise BaseError("There must be a project id given!")
            tmp['projectIri'] = self.__project
            if not self.__label.isEmpty() and 'label' in self.__changed:
                tmp['labels'] = self.__label.toJsonObj()
            if not self.__comment.isEmpty() and 'comment' in self.__changed:
                tmp['comments'] = self.__comment.toJsonObj()
            if self.__name is not None and 'name' in self.__changed:
                tmp['name'] = self.__name
        return tmp

    def create(self) -> 'ListNode':
        """
        Create a new List in Knora

        :return: JSON-object from Knora
        """

        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        if self.__parent is not None:
            result = self.con.post('/admin/lists/' + quote_plus(self.__parent), jsondata)
            return ListNode.fromJsonObj(self.con, result['nodeinfo'])
        else:
            result = self.con.post('/admin/lists', jsondata)
            return ListNode.fromJsonObj(self.con, result['list']['listinfo'])

    def read(self) -> Any:
        """
        Read a project from Knora

        :return: JSON-object from Knora
        """

        result = self.con.get('/admin/lists/nodes/' + quote_plus(self.__id))
        return self.fromJsonObj(self.con, result['nodeinfo'])

    def update(self) -> Union[Any, None]:
        """
        Udate the ListNode info in Knora with the modified data in this ListNode instance

        :return: JSON-object from Knora refecting the update
        """

        jsonobj = self.toJsonObj(Actions.Update, self.id)
        if jsonobj:
            jsondata = json.dumps(jsonobj, cls=SetEncoder)
            result = self.con.put('/admin/lists/infos/' + quote_plus(self.id), jsondata)
            return ListNode.fromJsonObj(self.con, result['listinfo'])
        else:
            return None

    def delete(self) -> None:
        """
        Delete the given ListNode

        :return: Knora response
        """
        raise BaseError("NOT YET IMPLEMENTED BY KNORA BACKEND!")
        result = self.con.delete('/admin/lists/' + quote_plus(self.__id))
        return result
        #return Project.fromJsonObj(self.con, result['project'])

    def getAllNodes(self) -> 'ListNode':
        """
        Get all nodes of the list. Must be called from a ListNode instance that has at least set the
        list iri!

        :return: Root node of list with recursive ListNodes ("children"-attributes)
        """

        result = self.con.get('/admin/lists/' + quote_plus(self.__id))
        if 'list' not in result:
            raise BaseError("Request got no list!")
        if 'listinfo' not in result['list']:
            raise BaseError("Request got no proper list information!")
        root = ListNode.fromJsonObj(self.con, result['list']['listinfo'])
        if 'children' in result['list']:
            root.__children = ListNode.__getChildren(con=self.con,
                                                     parent_iri=root.id,
                                                     project_iri=root.project,
                                                     children=result['list']['children'])
        return root

    @staticmethod
    def getAllLists(con: Connection, project_iri: Optional[str] = None) -> List['ListNode']:
        """
        Get all lists. If a project IRI is given, it returns the lists of the specified project

        :param con: Connection instance
        :param project_iri: Iri/id of project
        :return: list of ListNodes
        """
        if project_iri is None:
            result = con.get('/admin/lists')
        else:
            result = con.get('/admin/lists?projectIri=' + quote_plus(project_iri))
        if 'lists' not in result:
            raise BaseError("Request got no lists!")
        return list(map(lambda a: ListNode.fromJsonObj(con, a), result['lists']))

    def _createDefinitionFileObj(self, children: List["ListNode"]):
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
            if not listnode.comment.isEmpty():
                listnodeobj["comment"] = listnode.comment.createDefinitionFileObj()
            if listnode.children:
                listnodeobj["nodes"] = self._createDefinitionFileObj(listnode.children)
            listnodeobjs.append(listnodeobj)
        return listnodeobjs

    def createDefinitionFileObj(self):
        """
        Create an object that corresponds to the syntax of the input to "create_onto".
        :return: A python object that can be jsonfied to correspond to the syntax of the input to "create_onto".
        """
        listnode = {
            "name": self.__name,
            "labels": self.__label.createDefinitionFileObj(),
        }
        if not self.__comment.isEmpty():
            listnode["comment"] = self.__comment.createDefinitionFileObj()
        if self.__children:
            listnode["nodes"] = self._createDefinitionFileObj(self.__children)
        return listnode

    def print(self):
        """
        print info to stdout

        :return: None
        """

        print('Node Info:')
        print('  Id:        {}'.format(self.__id))
        print('  Project:   {}'.format(self.__project))
        print('  Name:      {}'.format(self.__name))
        print('  Label:     ')
        if self.__label:
            for lbl in self.__label.items():
                print('             {}: {}'.format(lbl[0], lbl[1]))
        else:
            print('             None')
        print('  Comment:   ')
        if self.__comment.isEmpty():
            for lbl in self.__comment.items():
                print('             {}: {}'.format(lbl[0], lbl[1]))
        else:
            print('             None')
        print('  Parent', self.__parent)
        print('  IsRootNode: {}'.format(self.__isRootNode))
