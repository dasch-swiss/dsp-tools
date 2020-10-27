import json
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from urllib.parse import quote_plus

from .helpers import Actions, BaseError
from .connection import Connection
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

    _id: str
    _name: str
    _description: str
    _project: str
    _selfjoin: bool
    _status: bool

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 project: Optional[Union[str, Project]] = None,
                 selfjoin: Optional[bool] = None,
                 status: Optional[bool] = None):
        super().__init__(con)
        self._id = str(id) if id is not None else None
        self._name = str(name) if name is not None else None
        self._description = description
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
    def description(self):
        return self._description

    @description.setter
    def description(self, value: Optional[str]):
        self._description = value
        self._changed.add('description')

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
            if self._name is None:
                raise BaseError("There must be a valid name!")
            tmp['name'] = self._name
            if self._description is not None:
                tmp['description'] = self._description
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
            if self._description is not None and 'description' in self._changed:
                tmp['description'] = self._description
            if self._selfjoin is not None and 'selfjoin' in self._changed:
                tmp['selfjoin'] = self._selfjoin
        return tmp

    def create(self):
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self._con.post('/admin/groups', jsondata)
        return Group.fromJsonObj(self._con, result['group'])

    def read(self):
        result = self._con.get('/admin/groups/' + quote_plus(self._id))
        return Group.fromJsonObj(self._con, result['group'])

    def update(self):
        jsonobj = self.toJsonObj(Actions.Update)
        if jsonobj:
            jsondata = json.dumps(jsonobj)
            result = self._con.put('/admin/groups/' + quote_plus(self._id), jsondata)
            updated_group = Group.fromJsonObj(self._con, result['group'])
        if self._status is not None and 'status' in self._changed:
            jsondata = json.dumps({'status': self._status})
            result = self._con.put('/admin/groups/' + quote_plus(self._id) + '/status', jsondata)
            updated_group = Group.fromJsonObj(self._con, result['group'])
        return updated_group

    def delete(self):
        result = self._con.delete('/admin/groups/' + quote_plus(self._id))
        return Group.fromJsonObj(self._con, result['group'])

    @staticmethod
    def getAllGroups(con: Connection) -> List['Group']:
        result = con.get('/admin/groups')
        if 'groups' not in result:
            raise BaseError("Request got no groups!")
        return list(map(lambda a: Group.fromJsonObj(con, a), result['groups']))


    def print(self):
        print('Group Info:')
        print('  Id:          {}'.format(self._id))
        print('  Name:        {}'.format(self._name))
        print('  Description: {}'.format(self._description))
        print('  Project:     {}'.format(self._project))
        print('  Selfjoin:    {}'.format(self._selfjoin))
        print('  Status:      {}'.format(self._status))



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
