from __future__ import annotations

import json
from typing import Optional, Any, Union
from urllib.parse import quote_plus

from pystrict import strict

from knora.dsplib.models.langstring import LangString
from .connection import Connection
from .helpers import Actions, BaseError
from .model import Model
from .project import Project

"""
This module implements the handling (CRUD) of Knora groups.

CREATE:
    * Instantiate a new object of the class Group with all required parameters
    * Call the ``create``-method on the instance

READ:
    * Instantiate a new object with ``id``(IRI of group) given
    * Call the ``read``-method on the instance
    * Access the information that has been provided to the instance

UPDATE:
    * You need an instance of an existing Project by reading an instance
    * Change the attributes by assigning the new values
    * Call the ``update```method on the instance

DELETE
    * Instantiate a new objects with ``id``(IRI of group) given, or use any instance that has the id set
    * Call the ``delete``-method on the instance

"""


@strict
class Group(Model):
    """
    This class represents a Knora group

    Attributes
    ----------

    con : Connection
        A connection instance to a Knora server

    id : str
        IRI of the group [get only, cannot be modified after creation of instance]

    name : str
        Name of the group

    descriptions : LangString
        Group descriptions in a given language (Languages.EN, Languages.DE, Languages.FR, Languages.IT, Languages.RM).

    project : str | project
        either the IRI of a project [get only, cannot be modified after creation of instance]
        or an valid Project instance

    selfjoin : boolean
        A flag indicating if selfjoin is allowed in this group

    status : boolean
        A flag indicating if the group is active (True) or inactive/makred deleted (False)

    """

    PROJECT_MEMBER_GROUP: str = "http://www.knora.org/ontology/knora-admin#ProjectMember"
    PROJECT_ADMIN_GROUP: str = "http://www.knora.org/ontology/knora-admin#ProjectAdmin"
    PROJECT_SYSTEMADMIN_GROUP: str = "http://www.knora.org/ontology/knora-admin#SystemAdmin"
    ROUTE: str = "/admin/groups"
    ROUTE_SLASH: str = ROUTE + "/"

    _id: str
    _name: str
    _descriptions: LangString
    _project: str
    _selfjoin: bool
    _status: bool

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 name: Optional[str] = None,
                 descriptions: LangString = None,
                 project: Optional[Union[str, Project]] = None,
                 selfjoin: Optional[bool] = None,
                 status: Optional[bool] = None):
        super().__init__(con)
        self._id = str(id) if id is not None else None
        self._name = str(name) if name is not None else None
        self._descriptions = LangString(descriptions)
        if project is not None and isinstance(project, Project):
            self._project = project.id
        else:
            self._project = str(project) if project is not None else None
        self._selfjoin = bool(selfjoin) if selfjoin is not None else None
        self._status = bool(status) if status is not None else None

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('Group id cannot be modified!')

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        self._changed.add('name')

    @property
    def descriptions(self) -> Optional[LangString]:
        return self._descriptions

    @descriptions.setter
    def descriptions(self, value: Optional[LangString]) -> None:
        self._descriptions = LangString(value)
        self._changed.add('descriptions')

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value: str):
        raise BaseError('project id cannot be modified!')

    @property
    def selfjoin(self) -> bool:
        return self._selfjoin

    @selfjoin.setter
    def selfjoin(self, value: bool) -> None:
        self._selfjoin = value
        self._changed.add('selfjoin')

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: bool) -> None:
        self._status = value
        self._changed.add('status')

    def has_changed(self) -> bool:
        if self._changed:
            return True
        else:
            return False

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any):
        group_id = json_obj.get('id')
        if group_id is None:
            raise BaseError('Group "id" is missing')
        name = json_obj.get('name')
        if name is None:
            raise BaseError('Group "name" is missing')
        descriptions = LangString.fromJsonObj(json_obj.get('descriptions'))
        tmp = json_obj.get('project')
        if tmp is None:
            raise BaseError('Group "project" is missing')
        project = tmp.get('id')
        if project is None:
            raise BaseError('Group "project" has no "id"')
        selfjoin = json_obj.get('selfjoin')
        if selfjoin is None:
            raise BaseError("selfjoin is missing")
        status = json_obj.get('status')
        if status is None:
            raise BaseError("Status is missing")
        return cls(con=con,
                   name=name,
                   id=group_id,
                   descriptions=descriptions,
                   project=project,
                   selfjoin=selfjoin,
                   status=status)

    def toJsonObj(self, action: Actions):
        tmp = {}
        if action == Actions.Create:
            if self._name is None:
                raise BaseError("There must be a valid name!")
            tmp['name'] = self._name
            if not self._descriptions.isEmpty():
                tmp['descriptions'] = self._descriptions.toJsonObj()
            if self._project is None:
                raise BaseError("There must be a valid project!")
            tmp['project'] = self._project
            if self._selfjoin is None:
                raise BaseError("There must be a valid value for selfjoin!")
            tmp['selfjoin'] = self._selfjoin
            if self._status is None:
                raise BaseError("There must be a valid value for status!")
            tmp['status'] = self._status
        else:
            if self._name is not None and 'name' in self._changed:
                tmp['name'] = self._name
            if not self._descriptions.isEmpty() and 'descriptions' in self._changed:
                tmp['descriptions'] = self._descriptions.toJsonObj()
            if self._selfjoin is not None and 'selfjoin' in self._changed:
                tmp['selfjoin'] = self._selfjoin
        return tmp

    def create(self) -> Group:
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self._con.post(Group.ROUTE, jsondata)
        return Group.fromJsonObj(self._con, result['group'])

    def read(self):
        result = self._con.get(Group.ROUTE_SLASH + quote_plus(self._id))
        return Group.fromJsonObj(self._con, result['group'])

    def update(self):
        jsonobj = self.toJsonObj(Actions.Update)
        if jsonobj:
            jsondata = json.dumps(jsonobj)
            result = self._con.put(Group.ROUTE_SLASH + quote_plus(self._id), jsondata)
            updated_group = Group.fromJsonObj(self._con, result['group'])
        if self._status is not None and 'status' in self._changed:
            jsondata = json.dumps({'status': self._status})
            result = self._con.put(Group.ROUTE_SLASH + quote_plus(self._id) + '/status', jsondata)
            updated_group = Group.fromJsonObj(self._con, result['group'])
        return updated_group

    def delete(self):
        result = self._con.delete(Group.ROUTE_SLASH + quote_plus(self._id))
        return Group.fromJsonObj(self._con, result['group'])

    @staticmethod
    def getAllGroups(con: Connection) -> list[Group]:
        result = con.get(Group.ROUTE)
        return [Group.fromJsonObj(con, group_item) for group_item in result["groups"]]

    @staticmethod
    def getAllGroupsForProject(con: Connection, proj_shortcode: str) -> Optional[list[Group]]:
        all_groups = Group.getAllGroups(con)
        project_groups = []
        for group in all_groups:
            if group.project == "http://rdfh.ch/projects/" + proj_shortcode:
                project_groups.append(group)
        return project_groups

    def createDefinitionFileObj(self):
        group = {
            "name": self.name,
            "descriptions": self.descriptions.createDefinitionFileObj(),
            "selfjoin": self.selfjoin,
            "status": self.status
        }
        return group

    def print(self) -> None:
        print('Group Info:')
        print('  Id:          {}'.format(self._id))
        print('  Name:        {}'.format(self._name))
        if self._descriptions is not None:
            print('  Descriptions:')
            for descr in self._descriptions.items():
                print('    {}: {}'.format(descr[0], descr[1]))
        else:
            print('  Descriptions: None')
        print('  Project:     {}'.format(self._project))
        print('  Selfjoin:    {}'.format(self._selfjoin))
        print('  Status:      {}'.format(self._status))
