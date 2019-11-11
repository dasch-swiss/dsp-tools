import requests
import json
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum, unique
from urllib.parse import quote_plus
from pprint import pprint

from Helpers import Languages, Actions, LangString, BaseError
from Connection import Connection

class KnoraGroup:
    PROJECT_MEMBER_GROUP: str = "http://www.knora.org/ontology/knora-admin#ProjectMember"
    PROJECT_ADMIN_GROUP: str = "http://www.knora.org/ontology/knora-admin#ProjectAdmin"

    _id: str
    _name: str
    _description: str
    _project: str
    _selfjoin: bool
    _status: bool

    def __init__(self,
                 con: Connection,
                 id: str = None,
                 name: str = None,
                 description: str = None,
                 project: str = None,
                 selfjoin: bool = False,
                 status: bool = True):
        self.con = con
        self._id = id
        self._name = name
        self._description = description
        self._project = project
        self._selfjoin = selfjoin
        self._status = status
        self.changed = set()

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('User id cannot be modified!')

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        self.changed.add('name')

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: Optional[str]):
        self._description = value
        self.changed.add('description')

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
        self.changed.add('selfjoin')

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: bool) -> None:
        self._status = value
        self.changed.add('status')

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
            if self._name is not None and 'name' in self.changed:
                tmp['name'] = self._name
            if self._description is not None and 'description' in self.changed:
                tmp['description'] = self._description
            if self._selfjoin is not None and 'selfjoin' in self.changed:
                tmp['selfjoin'] = self._selfjoin
        return tmp

    def create(self):
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self.con.post('/admin/groups', jsondata)
        return KnoraGroup.fromJsonObj(self.con, result['group'])

    def read(self):
        result = self.con.get('/admin/groups/iri/' + quote_plus(self._id))
        return KnoraGroup.fromJsonObj(self.con, result['group'])

    def update(self):
        jsonobj = self.toJsonObj(Actions.Update)
        pprint(jsonobj)
        if jsonobj:
            jsondata = json.dumps(jsonobj)
            result = self.con.put('/admin/groups/' + quote_plus(self.id), jsondata)
            updated_group = KnoraGroup.fromJsonObj(self.con, result['group'])
        if self._status is not None and 'status' in self.changed:
            jsondata = json.dumps({'status': self._status})
            result = self.con.put('/admin/groups/' + quote_plus(self.id) + '/status', jsondata)
            updated_group = KnoraGroup.fromJsonObj(self.con, result['group'])
        return updated_group

    def delete(self):
        result = self.con.delete('/admin/groups/' + quote_plus(self._id))
        pprint(result)
        return result

    @staticmethod
    def getAllGroups(con: Connection):
        result = con.get('/admin/groups')
        if 'groups' not in result:
            raise BaseError("Request got no groups!")
        return list(map(lambda a: KnoraGroup.fromJsonObj(con, a), result['groups']))

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

    groups = KnoraGroup.getAllGroups(con)
    for group in groups:
        group.print()

    new_group = KnoraGroup(con=con,
                           name="KNORA-PY TEST",
                           description="Test project for knora-py",
                           project="http://rdfh.ch/projects/00FF",
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
    groups = KnoraGroup.getAllGroups(con)
    for group in groups:
        group.print()
