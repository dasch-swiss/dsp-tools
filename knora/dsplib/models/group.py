import json
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from urllib.parse import quote_plus

from .helpers import Actions, BaseError
from .connection import Connection
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
class Group:
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

    description : str
        A description of the group

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

    __id: str
    __name: str
    __description: str
    __project: str
    __selfjoin: bool
    __status: bool
    __changed: set

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 project: Optional[Union[str, Project]] = None,
                 selfjoin: Optional[bool] = None,
                 status: Optional[bool] = None):
        if not isinstance(con, Connection):
            raise BaseError ('"con"-parameter must be an instance of Connection')
        self.con = con
        self.__id = str(id) if id is not None else None
        self.__name = str(name) if name is not None else None
        self.__description = description
        if project is not None and isinstance(project, Project):
            self.__project = project.id
        else:
            self.__project = str(project) if project is not None else None
        self.__selfjoin = bool(selfjoin) if selfjoin is not None else None
        self.__status = bool(status) if status is not None else None
        self.__changed = set()

    @property
    def id(self) -> Optional[str]:
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('Group id cannot be modified!')

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value
        self.__changed.add('name')

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value: Optional[str]):
        self.__description = value
        self.__changed.add('description')

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, value: str):
        raise BaseError('project id cannot be modified!')

    @property
    def selfjoin(self) -> bool:
        return self.__selfjoin

    @selfjoin.setter
    def selfjoin(self, value: bool) -> None:
        self.__selfjoin = value
        self.__changed.add('selfjoin')

    @property
    def status(self) -> bool:
        return self.__status

    @status.setter
    def status(self, value: bool) -> None:
        self.__status = value
        self.__changed.add('status')

    def has_changed(self) -> bool:
        if self.__changed:
            return True
        else:
            return False

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any):
        id = json_obj.get('id')
        if id is None:
            raise BaseError('Group "id" is missing in JSON from knora')
        name = json_obj.get('name')
        if name is None:
            raise BaseError('Group "name" is missing in JSON from knora')
        description = json_obj.get('description')
        tmp = json_obj.get('project')
        if tmp is None:
            raise BaseError('Group "project" is missing in JSON from knora')
        project = tmp.get('id')
        if project is None:
            raise BaseError('Group "project" has no "id" in JSON from knora')
        selfjoin = json_obj.get('selfjoin')
        if selfjoin is None:
            raise BaseError("selfjoin is missing in JSON from knora")
        status = json_obj.get('status')
        if status is None:
            raise BaseError("Status is missing in JSON from knora")
        return cls(con=con,
                   name=name,
                   id=id,
                   description=description,
                   project=project,
                   selfjoin=selfjoin,
                   status=status)

    def toJsonObj(self, action: Actions):
        tmp = {}
        if action == Actions.Create:
            if self.__name is None:
                raise BaseError("There must be a valid name!")
            tmp['name'] = self.__name
            if self.__description is not None:
                tmp['description'] = self.__description
            if self.__project is None:
                raise BaseError("There must be a valid project!")
            tmp['project'] = self.__project
            if self.__selfjoin is None:
                raise BaseError("There must be a valid value for selfjoin!")
            tmp['selfjoin'] = self.__selfjoin
            if self.__status is None:
                raise BaseError("There must be a valid value for status!")
            tmp['status'] = self.__status
        else:
            if self.__name is not None and 'name' in self.__changed:
                tmp['name'] = self.__name
            if self.__description is not None and 'description' in self.__changed:
                tmp['description'] = self.__description
            if self.__selfjoin is not None and 'selfjoin' in self.__changed:
                tmp['selfjoin'] = self.__selfjoin
        return tmp

    def create(self):
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self.con.post('/admin/groups', jsondata)
        return Group.fromJsonObj(self.con, result['group'])

    def read(self):
        result = self.con.get('/admin/groups/' + quote_plus(self.__id))
        return Group.fromJsonObj(self.con, result['group'])

    def update(self):
        jsonobj = self.toJsonObj(Actions.Update)
        if jsonobj:
            jsondata = json.dumps(jsonobj)
            result = self.con.put('/admin/groups/' + quote_plus(self.id), jsondata)
            updated_group = Group.fromJsonObj(self.con, result['group'])
        if self.__status is not None and 'status' in self.__changed:
            jsondata = json.dumps({'status': self.__status})
            result = self.con.put('/admin/groups/' + quote_plus(self.id) + '/status', jsondata)
            updated_group = Group.fromJsonObj(self.con, result['group'])
        return updated_group

    def delete(self):
        result = self.con.delete('/admin/groups/' + quote_plus(self.__id))
        return Group.fromJsonObj(self.con, result['group'])

    @staticmethod
    def getAllGroups(con: Connection) -> List['Group']:
        result = con.get('/admin/groups')
        if 'groups' not in result:
            raise BaseError("Request got no groups!")
        return list(map(lambda a: Group.fromJsonObj(con, a), result['groups']))

    def print(self):
        print('Group Info:')
        print('  Id:          {}'.format(self.__id))
        print('  Name:        {}'.format(self.__name))
        print('  Description: {}'.format(self.__description))
        print('  Project:     {}'.format(self.__project))
        print('  Selfjoin:    {}'.format(self.__selfjoin))
        print('  Status:      {}'.format(self.__status))



if __name__ == '__main__':
    con = Connection('http://0.0.0.0:3333')
    con.login('root@example.com', 'test')

    groups = Group.getAllGroups(con)
    for group in groups:
        group.print()

    new_group = Group(con=con,
                           name="KNORA-PY TEST",
                           description="Test project for knora-py",
                           project="http://rdfh.ch/projects/00FF",
                           status=True,
                           selfjoin=False).create()
    new_group.print()

    new_group.name="KNORA-PY TEST - modified"
    new_group = new_group.update();
    new_group.print()

    new_group.description="gaga gaga gaga gaga gaga gaga gaga"
    new_group = new_group.update();
    new_group.print()

    new_group.selfjoin = True
    new_group = new_group.update();
    new_group.print()

    new_group.status = False
    new_group = new_group.update();
    new_group.print()

    new_group.name = '-- KNORA-PY TEST --'
    new_group.description = 'Final Test'
    new_group.status = True
    new_group = new_group.update()
    new_group.print()

    new_group.delete()

    print('=========================')
    groups = Group.getAllGroups(con)
    for group in groups:
        group.print()
