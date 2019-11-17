import os
import sys
import requests
import json
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union, NewType
from enum import Enum, unique
from urllib.parse import quote_plus
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
(head, tail)  = os.path.split(path)
if not head in sys.path:
    sys.path.append(head)
if not path in sys.path:
    sys.path.append(path)

from models.Helpers import Languages, Actions, LangString, BaseError
from models.Connection import Connection
from models.KnoraGroup import KnoraGroup
from models.KnoraProject import KnoraProject

@strict
class KnoraUser:
    _id: str
    _username: str
    _email: str
    _givenName: str
    _familyName: str
    _password: str
    _lang: Languages
    _status: bool
    _sysadmin: bool
    _in_groups: Set[str]
    _in_projects: Dict[str,bool]
    add_to_project: Dict[str,bool]
    rm_from_project: Dict[str,bool]
    change_admin: Dict[str,bool]

    def __init__(self,
                 con:  Connection,
                 id: Optional[str] = None,
                 username: Optional[str] = None,
                 email: Optional[str] = None,
                 givenName: Optional[str] = None,
                 familyName: Optional[str] = None,
                 password: Optional[str] = None,
                 lang: Optional[Union[str,Languages]] = None,
                 status: Optional[bool] = None,
                 sysadmin: Optional[bool] = None,
                 in_projects: Optional[Dict[str,bool]] = None,
                 in_groups: Optional[Set[str]] = None):
        if not isinstance(con, Connection):
            raise BaseError ('"con"-parameter must be an instance of Connection')
        self.con = con
        self._id = str(id) if id is not None else None
        self._username = str(username) if username is not None else None
        self._email = str(email) if email is not None else None
        self._givenName = str(givenName) if givenName is not None else None
        self._familyName = str(familyName) if familyName is not None else None
        self._password = str(password) if password is not None else None
        if lang is not None:
            if isinstance(lang, Languages):
                self._lang = lang
            else:
                lmap = dict(map(lambda a: (a.value, a), Languages))
                if lmap.get(lang) is None:
                    raise BaseError('Invalid language string "' + lang  + '"!')
                self._lang =  lmap[lang]
        else:
            self._lang = None
        self._status = None if status is None else bool(status)
        if in_projects is None or isinstance(in_projects, dict):
            self._in_projects = in_projects if in_projects is not None else {}
        else:
            raise BaseError("In_project must be tuple (project-iri: str, is-admin: bool)!")
        if in_groups is None or isinstance(in_groups, set):
            self._in_groups = in_groups if in_groups is not None else set()
        else:
            raise BaseError('In_groups must be a set of strings or None!')
        self._sysadmin = None if sysadmin is None else bool(sysadmin)
        self.changed = set()
        self.add_to_project = {}
        self.rm_from_project = {}
        self.change_admin = {}

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('User id cannot be modified!')

    @property
    def username(self) -> Optional[str]:
        return  self._username

    @username.setter
    def username(self, value: Optional[str]):
        if value is None:
            return
        self._username = str(value)
        self.changed.add('username')

    @property
    def email(self) -> Optional[str]:
        return self._email

    @email.setter
    def email(self, value: Optional[str]):
        if value is None:
            return
        self._email = str(value)
        self.changed.add('email')

    @property
    def givenName(self) -> Optional[str]:
        return self._givenName

    @givenName.setter
    def givenName(self, value: Optional[str]):
        if value is None:
            return
        self._givenName = str(value)
        self.changed.add('givenName')

    @property
    def familyName(self) -> Optional[str]:
        return self._familyName

    @familyName.setter
    def familyName(self, value: Optional[str]):
        if value is None:
            return
        self._familyName = str(value)
        self.changed.add('familyName')

    @property
    def password(self) -> Optional[str]:
        return self._password

    @password.setter
    def password(self, value: Optional[str]):
        if value is None:
            return
        self._password = str(value)
        self.changed.add('password')

    @property
    def lang(self) -> Optional[Languages]:
        return self._lang

    @lang.setter
    def lang(self, value: Optional[Union[str, Languages]]):
        if value is None:
            return
        if isinstance(value, Languages):
            self._lang = value
            self.changed.add('lang')
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(value) is None:
                raise BaseError('Invalid language string "' + value + '"!')
            self._lang = lmap[value]
            pprint(self._lang)
            self.changed.add('lang')

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: Optional[bool]) -> None:
        self._status = None if value is None else bool(value)
        if value is not None:
            self.changed.add('status')

    @property
    def sysadmin(self) -> bool:
        return self._sysadmin

    @sysadmin.setter
    def sysadmin(self, value: bool):
        self._sysadmin = None if value is None else bool(value)
        if value is not None:
            self.changed.add('sysadmin')

    @property
    def in_projects(self):
        return self._in_projects

    @in_projects.setter
    def in_project(self, value: Any):
        raise BaseError('Project membership cannot be modified directly! Use methods "addToProject" and "rmFromProject"')

    def addToProject(self, value: str, padmin: bool = False):
        if value in self.rm_from_project:
            self.rm_from_project.pop(value)
        elif value not in self._in_projects:
            self.add_to_project[value] = padmin
            self.changed.add('in_projects')
        else:
            raise BaseError("Already member of this project!")

    def rmFromProject(self, value: str):
        if value in self.add_to_project:
            self.add_to_project.pop(value)
        elif value in self._in_projects:
            self.rm_from_project[value] = self._in_projects[value]
            self.changed.add('in_projects')
        else:
            raise BaseError("Project is not in list of member projects!")

    def makeProjectAdmin(self, value: str):
        if value in self._in_projects:
            self.change_admin[value] = True
            self.changed.add('in_projects')
        elif value in self.add_to_project:
            self.add_to_project[value] = True
        else:
            raise BaseError("User is not member of project!")

    def unmakeProjectAdmin(self, value: str):
        if value in self._in_projects:
            self.change_admin[value] = False
            self.changed.add('in_projects')
        elif value in self.add_to_project:
            self.add_to_project[value] = False
        else:
            raise BaseError("User is not member of project!")

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any):
        id = json_obj.get('id')
        if id is None:
            raise BaseError('User "id" is missing in JSON from knora')
        email = json_obj.get('email')
        if email is None:
            raise BaseError('User "email" is missing in JSON from knora')
        username = json_obj.get('username')
        if username is None:
            raise BaseError('User "username" is missing in JSON from knora')
        familyName = json_obj.get('familyName')
        givenName = json_obj.get('givenName')
        lang = json_obj.get('lang')
        status = json_obj.get('status')
        if status is None:
            raise BaseError("Status is missing in JSON from knora")

        in_projects: Dict[str, bool] = {}
        in_groups: Set[str] = set()
        if json_obj.get('permissions') is not None and json_obj['permissions'].get('groupsPerProject') is not None:
            sysadmin = False
            project_groups = json_obj['permissions']['groupsPerProject']
            for project in project_groups:
                if project == KnoraProject.SYSTEM_PROJECT:
                    if KnoraGroup.PROJECT_SYSTEMADMIN_GROUP in project_groups[project]:
                        sysadmin = True
                else:
                    for group in project_groups[project]:
                        if group == KnoraGroup.PROJECT_MEMBER_GROUP:
                            if in_projects.get(project) is None:
                                in_projects[project] = False
                        elif group == KnoraGroup.PROJECT_ADMIN_GROUP:
                            in_projects[project] = True
                        else:
                            in_groups.add(group)
        return cls(con=con,
                   id=id,
                   username=username,
                   email=email,
                   givenName=givenName,
                   familyName=familyName,
                   lang=lang,
                   status=status,
                   sysadmin=sysadmin,
                   in_projects=in_projects,
                   in_groups=in_groups)

    def toJsonObj(self, action: Actions):
        tmp = {}
        if action == Actions.Create:
            if self._username is None:
                raise BaseError("There must be a valid username!")
            tmp['username'] = self._username
            if self._email is None:
                raise BaseError("'email' is mandatory!")
            tmp['email'] = self._email
            if self._givenName is None:
                raise BaseError("'givenName is mandatory!")
            tmp['givenName'] = self._givenName
            if self._familyName is None:
                raise BaseError("'familyName' is mandatory!")
            tmp['familyName'] = self._familyName
            if self._password is None:
                raise BaseError("'password' is mandatory!")
            tmp['password'] = self._password
            if self._lang is None:
                raise BaseError("'language' is mandatory!")
            tmp['lang'] = self._lang.value
            tmp['status'] = True if self._status is None else self._status
            tmp['systemAdmin'] = False if self._status is None else self._sysadmin
        elif action == Actions.Update:
            tmp_changed = False
            if self._username is not None and 'username' in self.changed:
                tmp['username'] = self._username
                tmp_changed = self._username
            else:
                tmp['username'] = None
            if self._email is not None  and 'email' in self.changed:
                tmp['email'] = self._email
                tmp_changed = True
            else:
                tmp['email'] = self._email
            if self._givenName is not None and 'givenName' in self.changed:
                tmp['givenName'] = self._givenName
                tmp_changed = True
            else:
                tmp['givenName'] = None
            if self._familyName is not None and 'familyName' in self.changed:
                tmp['familyName'] = self._familyName
                tmp_changed = True
            else:
                tmp['familyName'] = None
            if self._lang is not None and 'lang' in self.changed:
                tmp['lang'] = self._lang.value
                tmp_changed = True
            else:
                tmp['lang'] = None
            if not tmp_changed:
                tmp = {}
        return tmp

    def create(self):
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self.con.post('/admin/users', jsondata)
        id = result['user']['id']
        if self._in_projects is not None:
            for project in self._in_projects:
                result = self.con.post('/admin/users/iri/' + quote_plus(id) + '/project-memberships/' + quote_plus(project))
                if self._in_projects[project]:
                    result = self.con.post('/admin/users/iri/' + quote_plus(id) + '/project-admin-memberships/' + quote_plus(project))
        if self._in_groups is not None:
            for group in self._in_groups:
                result = self.con.post('/admin/users/iri/' + quote_plus(id) + '/group-memberships/' + quote_plus(group))
        return KnoraUser.fromJsonObj(self.con, result['user'])

    def read(self):
        result = self.con.get('/admin/users/iri/' + quote_plus(self._id))
        return KnoraUser.fromJsonObj(self.con, result['user'])

    def update(self, requesterPassword: Optional[str] = None):
        jsonobj = self.toJsonObj(Actions.Update)
        if jsonobj:
            jsondata = json.dumps(jsonobj)
            result = self.con.put('/admin/users/iri/' + quote_plus(self.id) + '/BasicUserInformation', jsondata)
        if 'status' in self.changed:
            jsonobj = {'status': self._status}
            jsondata = json.dumps(jsonobj)
            result = self.con.put('/admin/users/iri/' + quote_plus(self.id) + '/Status', jsondata)
        if 'password' in self.changed:
            if requesterPassword is None:
                raise BaseError("Requester's password is missing!")
            jsonobj = {
                "requesterPassword": requesterPassword,
                "newPassword": self._password
            }
            jsondata = json.dumps(jsonobj)
            result = self.con.put('/admin/users/iri/' + quote_plus(self.id) + '/Password', jsondata)
        for p in self.add_to_project.items():
            result = self.con.post('/admin/users/iri/' + quote_plus(self._id) + '/project-memberships/' + quote_plus(p[0]))
            if p[1]:
                result = self.con.post('/admin/users/iri/' + quote_plus(self._id) + '/project-admin-memberships/' + quote_plus(p[0]))
        for p in self.rm_from_project:
            if self._in_projects.get(p) is not None and self._in_projects[p]:
                result = self.con.delete('/admin/users/iri/' + quote_plus(self._id) + '/project-admin-memberships/' + quote_plus(p))
            result = self.con.delete('/admin/users/iri/' + quote_plus(self._id) + '/project-memberships/' + quote_plus(p))
        for p in self.change_admin.items():
            if not p[0] in self._in_projects:
                raise BaseError('user must be member of project!')
            if p[1]:
                result = self.con.post('/admin/users/iri/' + quote_plus(self._id) + '/project-admin-memberships/' + quote_plus(p[0]))
            else:
                result = self.con.delete('/admin/users/iri/' + quote_plus(self._id) + '/project-admin-memberships/' + quote_plus(p[0]))

        pprint(result)
        return KnoraUser.fromJsonObj(self.con, result['user'])

    def delete(self):
        pass

    @staticmethod
    def getAllUsers(con: Connection):
        result = con.get('/admin/users')
        if 'users' not in result:
            raise BaseError("Request got no users!")
        return list(map(lambda a: KnoraUser.fromJsonObj(con, a), result['users']))

    def print(self):
        print('User info:')
        print('  Id:          {}'.format(self._id))
        print('  Username:    {}'.format(self._username))
        print('  Family name: {}'.format(self._familyName))
        print('  Given name:  {}'.format(self._givenName))
        print('  Language:    {}'.format(self._lang.value))
        print('  Status:      {}'.format(self._status))
        print('  Sysadmin:    {}'.format(self._sysadmin))
        print('  In projects:')
        if self._in_projects is not None:
            for p in self._in_projects:
                print('    {} : project admin: {}'.format(p, self._in_projects[p]))
        print('   In groups:')
        if self._in_groups is not None:
            for g in self._in_groups:
                print('    {}'.format(g))



if __name__ == '__main__':
    con = Connection('http://0.0.0.0:3333')
    con.login('root@example.com', 'test')

    users = KnoraUser.getAllUsers(con)
    for u in users:
        uu = u.read()
        uu.print()

    print('======================================')

    new_user = KnoraUser(
        con=con,
        username="lrosenth",
        email="lukas.rosenthaler@gmail.com",
        givenName="Lukas",
        familyName="Rosenthaler",
        password="test",
        status=True,
        lang=Languages.DE,
        sysadmin=True,
        in_projects= {
            "http://rdfh.ch/projects/0001": True,
            "http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF": False
        },
        in_groups={"http://rdfh.ch/groups/00FF/images-reviewer"}
    ).create()
    new_user.print()

    new_user.status = False
    new_user = new_user.update()
    new_user.print()

    new_user.status = True
    #new_user.givenName = '--Lukas--'
    new_user.familyName = '--Rosenthaler--'
    new_user.password = 'gaga'
    new_user = new_user.update("test")
    new_user.print()

    new_user.addToProject("http://rdfh.ch/projects/0803", True)
    new_user.rmFromProject('http://rdfh.ch/projects/0001')
    new_user.makeProjectAdmin('http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF')
    new_user = new_user.update()
    new_user.print()
