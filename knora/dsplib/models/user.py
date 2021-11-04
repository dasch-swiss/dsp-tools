import json
import os
import sys
from typing import List, Set, Dict, Optional, Any, Union
from urllib.parse import quote_plus

from pystrict import strict

from .connection import Connection
from .group import Group
from .helpers import Actions, BaseError
from .langstring import Languages
from .model import Model
from .project import Project

path = os.path.abspath(os.path.dirname(__file__))
(head, tail) = os.path.split(path)
if not head in sys.path:
    sys.path.insert(0, head)
if not path in sys.path:
    sys.path.insert(0, path)

"""
This module implements the handling (CRUD) of Knora users.

CREATE:
    * Instantiate a new object of the class User with all required parameters
    * Call the ``create``-method on the instance to create the new user

READ:
    * Instantiate a new objects with ``id``(IRI of user) given
    * Call the ``read``-method on the instance
    * Access the information that has been ptovided to the instance

UPDATE:
    * You need an instance of an existing User by reading an instance
    * Change the attributes by assigning the new values
    * Call the ``update```method on the instance

DELETE
    * Instantiate a new objects with ``id``(IRI of user) given, or use any instance that has the id set
    * Call the ``delete``-method on the instance

In addition there is a static methods ``getAllProjects`` which returns a list of all projects
"""


@strict
class User(Model):
    """
    This class represents a user in Knora.

    Attributes
    ----------

    id : str
        IRI of the user [readonly, cannot be modified after creation of instance]

    username : str
        Unique identifier (not an IRI) of the user [read/write]

    email : str
        Email of the user [read/write]

    givenName : str
        Given name (firstname) of the user [read/write]

    familyName : str
        Family name of user (lastname) [read/write]

    password : str
        Password of user [write only]

    lang : Language
        Preferred language of the user. For setting can be Language instance or string "EN", "DE", "FR", "IT"

    status : bool
        Status of the user, If active, is set to True, otherwise false [read/write]

    sysadmin : bool
        True, if user is system administrator [read/write]

    in_groups : Set[str]
        Set of group IRI's the user is member of [readonly].
        Use ``addToGroup``and ``rmFromGroup`` to modify group membership

    in_projects : Set[str]
        Set of project IRI's the user belongs to
        Use ``addToproject``and ``rmFromproject`` to modify project membership


    Methods
    -------

    create : Knora user information object
        Creates a new user and returns the information about this user as it is in Knora

    read : Knora user information object
        Read user data

    update : Knora user information object
        Updates the changed attributes of a user and returns the updated information  as it is in Knora

    delete : Knora result code
        Deletes a user and returns the result code

    addToGroup : None
        Add the user to the given group (will be executed when calling ``update``)

    rmFromGroup : None
        Remove a user from a group (will be executed when calling ``update``)

    addToProject : None
        adds a user to a project, optional as project administrator (will be executed when calling ``update``)

    rmFromProject : None
        removes a user from a project (will be executed when calling ``update``)

    makeProjectAdmin : None
        Promote user to project admin of given project

    unmakeProjectAdmin : None
        Revoke project admin flog for user for given project

    getAllUsers : list of user
        Get a list of all users

    print : None
        Prints the user information to stdout


    """

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
    _in_projects: Dict[str, bool]
    _add_to_project: Dict[str, bool]
    _rm_from_project: Dict[str, bool]
    _add_to_group: Set[str]
    _rm_from_group: Set[str]
    _change_admin: Dict[str, bool]

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 username: Optional[str] = None,
                 email: Optional[str] = None,
                 givenName: Optional[str] = None,
                 familyName: Optional[str] = None,
                 password: Optional[str] = None,
                 lang: Optional[Union[str, Languages]] = None,
                 status: Optional[bool] = None,
                 sysadmin: Optional[bool] = None,
                 in_projects: Optional[Dict[str, bool]] = None,
                 in_groups: Optional[Set[str]] = None):
        """
        Constructor for User

        The constructor is user internally or externally, when a new user should be created in Knora.

        :param con: Connection instance [required]
        :param id: IRI of the user [required for CREATE, READ]
        :param username: Username [required for CREATE]
        :param email: Email address [required for CREATE]
        :param givenName: Given name (firstname) of user [required for CREATE]
        :param familyName: Family name (lastname) of user [required for CREATE]
        :param password: Password [required for CREATE]
        :param lang: Preferred language of the user [optional]
        :param status: Status (active = True, inactive/deleted = False) [optional]
        :param sysadmin: User has system administration privileges [optional]
        :param in_projects: Dict with project-IRI as key, boolean(True=project admin) as value [optional]
        :param in_groups: Set with group-IRI's the user should belong to [optional]
        """
        super().__init__(con)
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
                    raise BaseError('Invalid language string "' + lang + '"!')
                self._lang = lmap[lang]
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
        self._add_to_project = {}
        self._rm_from_project = {}
        self._change_admin = {}
        self._add_to_group = set()
        self._rm_from_group = set()

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('User id cannot be modified!')

    @property
    def username(self) -> Optional[str]:
        return self._username

    @username.setter
    def username(self, value: Optional[str]):
        if value is None:
            return
        self._username = str(value)
        self._changed.add('username')

    @property
    def email(self) -> Optional[str]:
        return self._email

    @email.setter
    def email(self, value: Optional[str]):
        if value is None:
            return
        self._email = str(value)
        self._changed.add('email')

    @property
    def givenName(self) -> Optional[str]:
        return self._givenName

    @givenName.setter
    def givenName(self, value: Optional[str]):
        if value is None:
            return
        self._givenName = str(value)
        self._changed.add('givenName')

    @property
    def familyName(self) -> Optional[str]:
        return self._familyName

    @familyName.setter
    def familyName(self, value: Optional[str]):
        if value is None:
            return
        self._familyName = str(value)
        self._changed.add('familyName')

    @property
    def password(self) -> Optional[str]:
        return None

    @password.setter
    def password(self, value: Optional[str]):
        if value is None:
            return
        self._password = str(value)
        self._changed.add('password')

    @property
    def lang(self) -> Optional[Languages]:
        return self._lang

    @lang.setter
    def lang(self, value: Optional[Union[str, Languages]]):
        if value is None:
            return
        if isinstance(value, Languages):
            self._lang = value
            self._changed.add('lang')
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(value) is None:
                raise BaseError('Invalid language string "' + value + '"!')
            self._lang = lmap[value]
            self._changed.add('lang')

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: Optional[bool]) -> None:
        self._status = None if value is None else bool(value)
        if value is not None:
            self._changed.add('status')

    @property
    def sysadmin(self) -> bool:
        return self._sysadmin

    @sysadmin.setter
    def sysadmin(self, value: bool):
        self._sysadmin = None if value is None else bool(value)
        if value is not None:
            self._changed.add('sysadmin')

    @property
    def in_groups(self) -> Set[str]:
        return self._in_groups

    @in_groups.setter
    def in_groups(self, value: Any):
        raise BaseError('Group membership cannot be modified directly! Use methods "addToGroup" and "rmFromGroup"')

    def addToGroup(self, value: str):
        """
        Add the user to the given group (executed at next update)

        :param value: IRI of the group
        :return: None
        """

        if value in self._rm_from_group:
            self._rm_from_group.pop(value)
        elif value not in self._in_groups:
            self._add_to_group.add(value)
            self._changed.add('in_groups')
        else:
            raise BaseError("Already member of this group!")

    def rmFromGroup(self, value: str):
        """
        Remove the user from the given group (executed at next update)

        :param value: Group IRI
        :return: None
        """

        if value in self._add_to_group:
            self._add_to_group.discard(value)
        elif value in self._in_groups:
            self._rm_from_group.add(value)
            self._changed.add('in_groups')
        else:
            raise BaseError("User is not in groups!")

    @property
    def in_projects(self) -> Dict[str, bool]:
        return self._in_projects

    @in_projects.setter
    def in_project(self, value: Any):
        raise BaseError(
            'Project membership cannot be modified directly! Use methods "addToProject" and "rmFromProject"')

    def addToProject(self, value: str, padmin: bool = False):
        """
        Add the user to the given project (executed at next update)

        :param value: project IRI
        :param padmin: True, if user should be project admin, False otherwise
        :return: None
        """

        if value in self._rm_from_project:
            self._rm_from_project.pop(value)
        elif value not in self._in_projects:
            self._add_to_project[value] = padmin
            self._changed.add('in_projects')
        else:
            raise BaseError("Already member of this project!")

    def rmFromProject(self, value: str):
        """
        Remove the user from the given project (executed at next update)

        :param value: Project IRI
        :return: None
        """

        if value in self._add_to_project:
            self._add_to_project.pop(value)
        elif value in self._in_projects:
            self._rm_from_project[value] = self._in_projects[value]
            self._changed.add('in_projects')
        else:
            raise BaseError("Project is not in list of member projects!")

    def makeProjectAdmin(self, value: str):
        """
        Make the user project administrator in the given project  (executed at next update)

        :param value: Project IRI
        :return: None
        """

        if value in self._in_projects:
            self._change_admin[value] = True
            self._changed.add('in_projects')
        elif value in self._add_to_project:
            self._add_to_project[value] = True
        else:
            raise BaseError("User is not member of project!")

    def unmakeProjectAdmin(self, value: str):
        """
        Revoke project administrator right for the user from the given project  (executed at next update)

        :param value: Project IRI
        :return: None
        """
        if value in self._in_projects:
            self._change_admin[value] = False
            self._changed.add('in_projects')
        elif value in self._add_to_project:
            self._add_to_project[value] = False
        else:
            raise BaseError("User is not member of project!")

    @property
    def changed(self) -> Set[str]:
        return self._changed

    def has_changed(self, name: str):
        return name in self._changed

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any):
        """
        Internal method! Should not be used directly!

        This method is used to create a User instance from the JSON data returned by Knora

        :param con: Connection instance
        :param json_obj: JSON data returned by Knora as python3 object
        :return: User instance
        """

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
                if project == Project.SYSTEM_PROJECT:
                    if Group.PROJECT_SYSTEMADMIN_GROUP in project_groups[project]:
                        sysadmin = True
                else:
                    for group in project_groups[project]:
                        if group == Group.PROJECT_MEMBER_GROUP:
                            if in_projects.get(project) is None:
                                in_projects[project] = False
                        elif group == Group.PROJECT_ADMIN_GROUP:
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
        """
        Internal method! Should not be used directly!

        Creates a JSON-object from the Project instance that can be used to call Knora

        :param action: Action the object is used for (Action.CREATE or Action.UPDATE)
        :return: JSON-object
        """

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
            tmp['systemAdmin'] = False if self._sysadmin is None else self._sysadmin
        elif action == Actions.Update:
            tmp_changed = False
            if self._username is not None and 'username' in self._changed:
                tmp['username'] = self._username
                tmp_changed = self._username
            if self._email is not None and 'email' in self._changed:
                tmp['email'] = self._email
                tmp_changed = True
            if self._givenName is not None and 'givenName' in self._changed:
                tmp['givenName'] = self._givenName
                tmp_changed = True
            if self._familyName is not None and 'familyName' in self._changed:
                tmp['familyName'] = self._familyName
                tmp_changed = True
            if self._lang is not None and 'lang' in self._changed:
                tmp['lang'] = self._lang.value
                tmp_changed = True
            if not tmp_changed:
                tmp = {}
        return tmp

    def create(self) -> Any:
        """
        Create new user in Knora

        :return: JSON-object from Knora
        """

        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self._con.post('/admin/users', jsondata)
        id = result['user']['id']
        if self._in_projects is not None:
            for project in self._in_projects:
                result = self._con.post(
                    '/admin/users/iri/' + quote_plus(id) + '/project-memberships/' + quote_plus(project))
                if self._in_projects[project]:
                    result = self._con.post(
                        '/admin/users/iri/' + quote_plus(id) + '/project-admin-memberships/' + quote_plus(project))
        if self._in_groups is not None:
            for group in self._in_groups:
                result = self._con.post(
                    '/admin/users/iri/' + quote_plus(id) + '/group-memberships/' + quote_plus(group))
        return User.fromJsonObj(self._con, result['user'])

    def read(self) -> Any:
        """
        Read the user information from Knora. The User object must have a valid id or email!

        :return: JSON-object from Knora
        """
        if self._id is not None:
            result = self._con.get('/admin/users/iri/' + quote_plus(self._id))
        elif self._email is not None:
            result = self._con.get('/admin/users/email/' + quote_plus(self._email))
        elif self._username is not None:
            result = self._con.get('/admin/users/username/' + quote_plus(self._username))
        else:
            raise BaseError('Either user-id or email is required!')
        return User.fromJsonObj(self._con, result['user'])

    def update(self, requesterPassword: Optional[str] = None) -> Any:
        """
        Udate the user info in Knora with the modified data in this user instance

        :param requesterPassword: Old password if a user wants to change it's own password
        :return: JSON-object from Knora
        """

        jsonobj = self.toJsonObj(Actions.Update)
        if jsonobj:
            jsondata = json.dumps(jsonobj)
            result = self._con.put('/admin/users/iri/' + quote_plus(self.id) + '/BasicUserInformation', jsondata)
        if 'status' in self._changed:
            jsonobj = {'status': self._status}
            jsondata = json.dumps(jsonobj)
            result = self._con.put('/admin/users/iri/' + quote_plus(self.id) + '/Status', jsondata)
        if 'password' in self._changed:
            if requesterPassword is None:
                raise BaseError("Requester's password is missing!")
            jsonobj = {
                "requesterPassword": requesterPassword,
                "newPassword": self._password
            }
            jsondata = json.dumps(jsonobj)
            result = self._con.put('/admin/users/iri/' + quote_plus(self.id) + '/Password', jsondata)
        if 'sysadmin' in self._changed:
            jsonobj = {'systemAdmin': self._sysadmin}
            jsondata = json.dumps(jsonobj)
            result = self._con.put('/admin/users/iri/' + quote_plus(self.id) + '/SystemAdmin', jsondata)
        for p in self._add_to_project.items():
            result = self._con.post(
                '/admin/users/iri/' + quote_plus(self._id) + '/project-memberships/' + quote_plus(p[0]))
            if p[1]:
                result = self._con.post(
                    '/admin/users/iri/' + quote_plus(self._id) + '/project-admin-memberships/' + quote_plus(p[0]))

        for p in self._rm_from_project:
            if self._in_projects.get(p) is not None and self._in_projects[p]:
                result = self._con.delete(
                    '/admin/users/iri/' + quote_plus(self._id) + '/project-admin-memberships/' + quote_plus(p))
            result = self._con.delete(
                '/admin/users/iri/' + quote_plus(self._id) + '/project-memberships/' + quote_plus(p))

        for p in self._change_admin.items():
            if not p[0] in self._in_projects:
                raise BaseError('user must be member of project!')
            if p[1]:
                result = self._con.post(
                    '/admin/users/iri/' + quote_plus(self._id) + '/project-admin-memberships/' + quote_plus(p[0]))
            else:
                result = self._con.delete(
                    '/admin/users/iri/' + quote_plus(self._id) + '/project-admin-memberships/' + quote_plus(p[0]))

        for p in self._add_to_group:
            result = self._con.post('/admin/users/iri/' + quote_plus(self._id) + '/group-memberships/' + quote_plus(p))
        for p in self._rm_from_group:
            result = self._con.delete(
                '/admin/users/iri/' + quote_plus(self._id) + '/group-memberships/' + quote_plus(p))
        user = User(con=self._con, id=self._id).read()
        return user

    def delete(self):
        """
        Delete the user in nore (NOT YET IMPLEMENTED)
        :return: None
        """
        result = self._con.delete('/admin/users/iri/' + quote_plus(self._id))
        return User.fromJsonObj(self._con, result['user'])

    @staticmethod
    def getAllUsers(con: Connection) -> List[Any]:
        """
        Get a list of all users (static method)

        :param con: Connection instance
        :return: List of users
        """

        result = con.get('/admin/users')
        if 'users' not in result:
            raise BaseError("Request got no users!")
        return list(map(lambda a: User.fromJsonObj(con, a), result['users']))

    def print(self) -> None:
        """
        Prin user info to stdout

        :return: None
        """

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

    users = User.getAllUsers(con)
    for u in users:
        uu = u.read()
        uu.print()

    print('======================================')

    new_user = User(
        con=con,
        username="lrosenth",
        email="lukas.rosenthaler@gmail.com",
        givenName="Lukas",
        familyName="Rosenthaler",
        password="test",
        status=True,
        lang=Languages.DE,
        sysadmin=True,
        in_projects={
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
    # new_user.givenName = '--Lukas--'
    new_user.familyName = '--Rosenthaler--'
    new_user.password = 'gaga'
    new_user = new_user.update("test")
    new_user.print()

    new_user.addToProject("http://rdfh.ch/projects/0803", True)
    new_user.rmFromProject('http://rdfh.ch/projects/0001')
    new_user.makeProjectAdmin('http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF')
    new_user = new_user.update()
    new_user.print()
