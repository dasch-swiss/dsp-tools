import requests
import json
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum, unique
from urllib.parse import quote_plus
from pprint import pprint

from Helpers import Languages, Actions, LangString, BaseError
from Connection import Connection
from KnoraGroup import KnoraGroup
from KnoraProject import KnoraProject

class KnoraUser:
    _id: str
    _username: str
    _email: str
    _givenName: str
    _familyName: str
    _password: str
    _lang: Languages
    _status: bool
    _roles: Dict[str,Set[str]]

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
                 sysadmin: bool = False,
                 projectmember: Set[str] = None,
                 projectadmin: Set[str] = None,
                 roles: Optional[Dict[str,Set[str]]] = None):
        self.con = con
        self._id = id
        self._username = username
        self._email = email
        self._givenName = givenName
        self._familyName = familyName
        self._password = password
        if isinstance(lang, Languages):
            self._lang = lang
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(lang) is None:
                raise BaseError('Invalid language string "' + lang  + '"!')
            self._lang =  lmap[lang]
        self._status = status
        self._roles = roles
        if sysadmin:
            if self._roles is None:
                self._roles = {
                    KnoraProject.SYSTEM_PROJECT: set(KnoraGroup.PROJECT_ADMIN_GROUP)
                }
            else:
                if self._roles.get(KnoraProject.SYSTEM_PROJECT) is None:
                    self.roles[KnoraProject.SYSTEM_PROJECT] = set(KnoraGroup.PROJECT_ADMIN_GROUP)
                else:
                    self.roles[KnoraProject.SYSTEM_PROJECT].add(KnoraGroup.PROJECT_ADMIN_GROUP)
        if projectmember is not None:
            for pm in projectmember:
                if self._roles is None:
                    self._roles = {
                        pm: set(KnoraGroup.PROJECT_MEMBER_GROUP)
                    }
                else:
                    if self._roles.get(pm) is None:
                        self.roles[pm] = set(KnoraGroup.PROJECT_MEMBER_GROUP)
                    else:
                        self.roles[pm].add(KnoraGroup.PROJECT_MEMBER_GROUP)

        if projectadmin is not None:
            for pm in projectadmin:
                if self._roles is None:
                    self._roles = {
                        pm: set(KnoraGroup.PROJECT_ADMIN_GROUP)
                    }
                else:
                    if self._roles.get(pm) is None:
                        self.roles[pm] = set(KnoraGroup.PROJECT_ADMIN_GROUP)
                    else:
                        self.roles[pm].add(KnoraGroup.PROJECT_ADMIN_GROUP)
        self.changed = set()
        self.newprojects = set()
        self.newprojectadmins=set()

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
    def username(self, value: str):
        self._username = value
        self.changed.add('username')

    @property
    def email(self) -> Optional[str]:
        return self._email

    @email.setter
    def email(self, value: str):
        self._email = value
        self.changed.add('email')

    @property
    def givenName(self) -> Optional[str]:
        return self._givenName

    @givenName.setter
    def givenName(self, value: str):
        self._givenName = value
        self.changed.add('givenName')

    @property
    def familyName(self) -> Optional[str]:
        return self._familyName

    @familyName.setter
    def familyName(self, value: str):
        self.familyName = value
        self.changed.add('familyName')

    @property
    def password(self) -> Optional[str]:
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = password
        self.changed.add('password')

    @property
    def lang(self) -> Optional[Languages]:
        return self._lang

    @lang.setter
    def lang(self, value: Union[str, Languages]):
        if isinstance(value, Languages):
            self._lang = value
            self.changed.add('lang')
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(value) is None:
                raise BaseError('Invalid language string "' + value + '"!')
            self._lang = lmap[value]
            self.changed.add('lang')

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: bool) -> None:
        self._status = value
        self.changed.add('status')

    @property
    def sysadmin(self) -> bool:
        if self._roles is None:
            return False
        return KnoraProject.SYSTEM_PROJECT in self._roles and KnoraGroup.PROJECT_ADMIN_GROUP in self._roles[KnoraProject.SYSTEM_PROJECT]

    @sysadmin.setter
    def sysadmin(self, value: bool):
        if self._roles is None:
            self._roles = {}
        tmp = KnoraProject.SYSTEM_PROJECT in self._roles and KnoraGroup.PROJECT_ADMIN_GROUP in self._roles[KnoraProject.SYSTEM_PROJECT]
        if tmp != value:
            self.changed.add('sysadmin')
        else:
            self.changed.discard('sysadmin')

    @property
    def projectmember(self):
        tmp = list(filter(lambda a: KnoraGroup.PROJECT_MEMBER_GROUP in a[1], self._roles.items()))
        return set(map(lambda a: a[0], tmp))

    @projectmember.setter
    def projectmember(self, value: Set[str]):
        self.newprojtcs = value

    @property
    def projectadmin(self):
        tmp = list(filter(lambda a: KnoraGroup.PROJECT_ADMIN_GROUP in a[1], self._roles.items()))
        return set(map(lambda a: a[0], tmp))

    @projectadmin.setter
    def projectadmin(self, value: Set[str]):
        self.newprojectadmins  = value

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

        if json_obj.get('permissions') is not None and json_obj['permissions'].get('groupsPerProject') is not None:
            roles = {}
            for project in json_obj['permissions']['groupsPerProject']:
                roles[project] = set()
                for group in json_obj['permissions']['groupsPerProject'][project]:
                    roles[project].add(group)
        else:
            roles = None
        return cls(con=con,
                   id=id,
                   username=username,
                   email=email,
                   givenName=givenName,
                   familyName=familyName,
                   lang=lang,
                   status=status,
                   roles=roles)

    def toJsonObj(self, action: Actions):
        tmp = {}
        if action == Actions.Create:
            if self._username is None:
                raise BaseError("There must be a valid username!")
            tmp['username'] = self._username
            if self._email is None:
                raise BaseError("There must be a valid email!")
            tmp['email'] = self._email
            if self._givenName is not None:
                tmp['c'] = self._givenName
            if self._familyName is not None:
                tmp['familyName'] = self._familyName
            if self._password is None:
                raise BaseError("There must be a password!")
            tmp['password'] = self._password
            if self._lang is None:
                raise BaseError("There must be a language given!")
            tmp['lang'] = self._lang.value
        elif action == Actions.Update:
            if self._username is not None and 'username' in self.changed:
                tmp['username'] = self._username
            if self._email is not None  and 'email' in self.changed:
                tmp['email'] = self._eemail
            if self._givenName is not None and 'givenName' in self.changed:
                tmp['givenName'] = self._givenName
            if self._familyName is not None and 'familyName' in self.changed:
                tmp['familyName'] = self._familyName
            if self._lang is not None and 'lang' in self.changed:
                tmp['lang'] = self._lang.value
        return tmp

    def create(self):
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self.con.post('/admin/users', jsondata)
        pprint(result)
        return KnoraProject.fromJsonObj(result['user'])

    def read(self):
        result = self.con.get('/admin/users/iri/' + quote_plus(self._id))
        return KnoraUser.fromJsonObj(self.con, result['user'])

    def update(self):
        jsonobj = self.toJsonObj(Actions.Update)
        jsondata = json.dumps(jsonobj)
        result = self.con.put('/admin/users/iri/' + quote_plus(self.id), jsondata)
        pprint(result)

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
        if self._roles is not None:
            if KnoraProject.SYSTEM_PROJECT in self._roles and KnoraGroup.PROJECT_ADMIN_GROUP in self._roles[KnoraProject.SYSTEM_PROJECT]:
                print('  Sysadmin:    True')
            else:
                print('  Sysadmin:    False')
            tmp = list(filter(lambda a: KnoraGroup.PROJECT_MEMBER_GROUP in a[1], self._roles.items()))
            projects = set(map(lambda a: a[0], tmp))
            for p in projects:
                print('    Member of project: ', p)

        print('  Language:    {}'.format(self._lang.value))
        print('  Status:      {}'.format(self._status))


if __name__ == '__main__':
    con = Connection('http://0.0.0.0:3333')
    con.login('root@example.com', 'test')

    users = KnoraUser.getAllUsers(con)
    for u in users:
        u.print()

    print('======================================')
    u = users.pop()
    nu = u.read()
    nu.print()
