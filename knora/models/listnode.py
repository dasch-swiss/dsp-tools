import os
import sys
import requests
import json
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union, NewType
from enum import Enum, unique
from urllib.parse import quote_plus
from pprint import pprint

from helpers import Languages, Actions, LangString, BaseError
from connection import Connection
from project import Project

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

    _id: str
    _project: str
    _label: LangString
    _comment: LangString
    _name: str
    _parent: str
    _isRootNode: bool
    _children: List['ListNode']
    _rootNodeIri: str
    changed: Set[str]

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 project: Optional[Union[Project, str]] = None,
                 label: Optional[LangString] = LangString(),
                 comment: Optional[LangString] = LangString(),
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
            raise BaseError ('"con"-parameter must be an instance of Connection')
        self.con = con

        self._project = project.id if isinstance(project, Project) else str(project) if project is not None else None
        self._id = str(id) if id is not None else None
        if not isinstance(label, LangString) and label is not None:
            raise BaseError('Labels must be LangString instance or None!')
        self._label = label
        if not isinstance(comment, LangString) and comment is not None:
            raise BaseError('Comments must be LangString instance or None!')
        self._comment = comment
        self._name = name if name is not None else None
        if not isinstance(parent, ListNode) and parent is not None:
            raise BaseError('Parent must be ListNode instance or None!')
        if isinstance(parent, ListNode):
            self._parent = parent.id
        else:
            self._parent = parent
        self._isRootNode = isRootNode
        if children is not None:
            if isinstance(children, List) and len(children) > 0 and isinstance(children[0], ListNode):
                self._children = children
            else:
                raise BaseError('Children must be list of ListNodes!')
        else:
            self._children = None
        if not isinstance(rootNodeIri, str) and rootNodeIri is not None:
            raise BaseError('rootNodeIri must be a str!')
        self._rootNodeIri = rootNodeIri
        self.changed = set()

    #
    # Here follows a list of getters/setters
    #
    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('ListNode id cannot be modified!')

    @property
    def project(self) -> Optional[str]:
        return self._project

    @project.setter
    def project(self, value: str) -> None:
        raise BaseError('Project id cannot be modified!')

    @property
    def label(self) -> Optional[LangString]:
        return self._label

    @label.setter
    def label(self, value: LangString) -> None:
        if value is not None and instanceof(value, LangString):
            self._label = value
            self.changed.add('label')
        else:
            raise BaseError('Not a valid LangString')

    def addLabel(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a node label with the given language (executed at next update)

        :param lang: The language the label, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the label
        :return: None
        """

        if isinstance(lang, Languages):
            self._label[lang] = value
            self.changed.add('label')
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(lang) is None:
                raise BaseError('Invalid language string "' + lang  + '"!')
            self._label[lmap[lang]] = value
            self.changed.add('label')

    def rmLabel(self, lang: Union[Languages, str]) -> None:
        """
        Remove a label from a list node (executed at next update)

        :param lang: The language the label to be removed is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :return: None
        """
        if isinstance(lang, Languages):
            del self._label[lang]
            self.changed.add('label')
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(lang) is None:
                raise BaseError('Invalid language string "' + lang  + '"!')
            del self._label[lmap[lang]]
            self.changed.add('label')

    @property
    def comment(self) -> Optional[LangString]:
        return self._comment

    @comment.setter
    def comment(self, value: LangString) -> None:
        if value is not None and instanceof(value, LangString):
            self._comment = value
            self.changed.add('comment')
        else:
            raise BaseError('Not a valid LangString')

    def addComment(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a node comment with the given language (executed at next update)

        :param lang: The language the comment, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the comment
        :return: None
        """

        if isinstance(lang, Languages):
            self._comment[lang] = value
            self.changed.add('comment')
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(lang) is None:
                raise BaseError('Invalid language string "' + lang  + '"!')
            self._comment[lmap[lang]] = value
            self.changed.add('comment')

    def rmComment(self, lang: Union[Languages, str]) -> None:
        """
        Remove a comment from a list node (executed at next update)

        :param lang: The language the comment to be removed is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :return: None
        """
        if isinstance(lang, Languages):
            del self._comment[lang]
            self.changed.add('comment')
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(lang) is None:
                raise BaseError('Invalid language string "' + lang  + '"!')
            del self._comment[lmap[lang]]
            self.changed.add('comment')

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = str(value)
        self.changed.add('name')

    @property
    def parent(self) -> Optional[str]:
        raise BaseError('Property parent cannot be read!')

    @parent.setter
    def parent(self, value: any):
        raise BaseError('Property parent cannot be set!')

    @property
    def isRootNode(self) -> Optional[bool]:
        return self._isRootNode

    @isRootNode.setter
    def isRootNode(self, value: bool) -> None:
        raise BaseError('Property isRootNode cannot be set!')

    @property
    def children(self) -> Optional[List['ListNode']]:
        return self._children

    @staticmethod
    def _getChildren(con: Connection, children: List[Any]) -> Optional[List['ListNode']]:
        """
        Internal method! Should not be used directly!

        Static method gets a recursive List of children nodes

        :param con: Valid Connection instance
        :param children: json object of children
        :return: List of ListNode instances
        """

        if len(children) == 0:
            return None
        child_nodes = []
        for child in children:
            child_nodes.append(ListNode.fromJsonObj(con, child))
        return child_nodes

    @property
    def rootNodeIri(self) -> Optional[str]:
        return self._rootNodeIri

    @rootNodeIri.setter
    def rootNodeIri(self, value: str):
        raise BaseError('rootNodeIri cannot be set!')

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
        project = json_obj.get('projectIri')
        if id is None:
            raise BaseError('ListNode id is missing')
        lbl = json_obj.get('labels')
        if lbl is not None:
            label = LangString()
            for l in lbl:
                label[l['language'] if l.get('language') is not None else 'en'] = l['value']
        else:
            label = None
        cmt = json_obj.get('comments')
        if cmt is not None:
            comment = LangString()
            for c in cmt:
                comment[c['language'] if c.get('language') is not None else 'en'] = c['value']
        else:
            comment = None
        name = json_obj.get('name')
        parent = json_obj.get('parentNodeIri')
        isRootNode = json_obj.get('isRootNode')

        child_info = json_obj.get('children')
        children = None
        if child_info is not None:
            children = ListNode._getChildren(con, child_info)

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
            if self._project is None:
                raise BaseError("There must be a project id given!")
            tmp['projectIri'] = self._project
            if self._label.isEmpty():
                raise BaseError("There must be a valid ListNode label!")
            tmp['labels'] = self._label.toJsonObj()
            if not self._comment.isEmpty():
                tmp['comments'] = self._comment.toJsonObj()
            if self._name is not None:
                tmp['name'] = self._name
            if self._parent is not None:
                tmp['parentNodeIri'] = self._parent
        elif action == Actions.Update:
            if self.id is None:
                raise BaseError("There must be a node id given!")
            tmp['listIri'] = listIri
            if self._project is None:
                raise BaseError("There must be a project id given!")
            tmp['projectIri'] = self._project
            if not self._label.isEmpty() and 'label' in self.changed:
                tmp['labels'] = self._label.toJsonObj()
            if not self._comment.isEmpty() and 'comment' in self.changed:
                tmp['comments'] = self._comment.toJsonObj()
            if self._name is not None and 'name' in self.changed:
                tmp['name'] = self._name
        return tmp

    def create(self) -> 'ListNode':
        """
        Create a new List in Knora

        :return: JSON-object from Knora
        """

        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        if self._parent is not None:
            result = self.con.post('/admin/lists/'+ quote_plus(self._parent), jsondata)
            return ListNode.fromJsonObj(self.con, result['nodeinfo'])
        else:
            result = self.con.post('/admin/lists', jsondata)
            return ListNode.fromJsonObj(self.con, result['list']['listinfo'])

    def read(self) -> Any:
        """
        Read a project from Knora

        :return: JSON-object from Knora
        """

        result = self.con.get('/admin/lists/nodes/' + quote_plus(self._id))
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
        result = self.con.delete('/admin/lists/' + quote_plus(self._id))
        return result
        #return Project.fromJsonObj(self.con, result['project'])

    def getAllNodes(self):
        """
        Get all nodes of the list. Mus be called from a ListNode instance that has at least set the
        list iri!

        :return: Root node of list with recursive ListNodes ("children"-attributes)
        """
        
        result = self.con.get('/admin/lists/' + quote_plus(self._id))
        if 'list' not in result:
            raise BaseError("Request got no list!")
        if 'listinfo' not in result['list']:
            raise BaseError("Request got no proper list information!")
        root = ListNode.fromJsonObj(self.con, result['list']['listinfo'])
        if 'children' in result['list']:
            root._children = ListNode._getChildren(self.con, result['list']['children'])
        return root

    @staticmethod
    def getAllLists(con: Connection, project_iri: str) -> List['ListNode']:
        """
        Get all lists of the specified project

        :param con: Connection instance
        :param project_iri: Iri/id of project
        :return: list of ListNodes
        """
        result = con.get('/admin/lists?projectIri=' + quote_plus(project_iri))
        if 'lists' not in result:
            raise BaseError("Request got no lists!")
        return list(map(lambda a: ListNode.fromJsonObj(con, a), result['lists']))


    def print(self):
        """
        print info to stdout

        :return: None
        """

        print('Node Info:')
        print('  Id:        {}'.format(self._id))
        print('  Project:   {}'.format(self._project))
        print('  Name:      {}'.format(self._name))
        print('  Label:     ')
        if self._label is not None:
            for lbl in self._label.items():
                print('             {}: {}'.format(lbl[0], lbl[1]))
        else:
            print('             None')
        print('  Comment:   ')
        if self._comment is not None:
            for lbl in self._comment.items():
                print('             {}: {}'.format(lbl[0], lbl[1]))
        else:
            print('             None')
        print('  Parent', self._parent)
        print('  IsRootNode: {}'.format(self._isRootNode))
