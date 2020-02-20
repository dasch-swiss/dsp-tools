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


@strict
class ListNode:
    _id: str
    _project: str
    _label: LangString
    _comment: LangString
    _name: str
    _parent: str
    _isRootNode: bool
    changed: Set[str]

    def __init__(
        self,
        con: Connection,
        id: Optional[str] = None,
        project: Optional[Union[Project, str]] = None,
        label: Optional[LangString] = LangString(),
        comment: Optional[LangString] = LangString(),
        name: Optional[str] = None,
        parent: Optional[Union['ListNode', str]] = None,
        isRootNode: Optional[bool] = None
    ):
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
        return self._parent

    @parent.setter
    def parent(self, value: any):
        raise BaseError('Property parent cannot be set!')

    @property
    def isRootNode(self) -> Optional[bool]:
        return self._isRootNode

    @isRootNode.setter
    def isRootNode(self, value: bool) -> None:
        raise BaseError('Property isRootNode cannot be set!')

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

        return cls(con=con,
                   id=id,
                   project=project,
                   label=label,
                   comment=comment,
                   name=name,
                   parent=parent,
                   isRootNode=isRootNode)

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
            pprint(result)
            return ListNode.fromJsonObj(self.con, result['listinfo'])
        else:
            return None

    def delete(self) -> None:
        """
        Delete the given ListNode

        :return: Knora response
        """

        result = self.con.delete('/admin/lists/' + quote_plus(self._id))
        return result
        #return Project.fromJsonObj(self.con, result['project'])


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
