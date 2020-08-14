import os
import sys
import requests
import json
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum, unique
from urllib.parse import quote_plus
from pprint import pprint

from models.helpers import Actions, BaseError
from models.langstring import Languages, LangStringParam, LangString
from models.connection import Connection, Error

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

"""
This module implements the handling (CRUD) of Knora projects.

CREATE:
    * Instantiate a new object of the class Project with all required parameters
    * Call the ``create``-method on the instance

READ:
    * Instantiate a new object with ``id``(IRI of project) given
    * Call the ``read``-method on the instance
    * Access the information that has been provided to the instance

UPDATE:
    * You need an instance of an existing Project by reading an instance
    * Change the attributes by assigning the new values
    * Call the ``update```method on the instance

DELETE
    * Instantiate a new objects with ``id``(IRI of project) given, or use any instance that has the id set
    * Call the ``delete``-method on the instance

In addition there is a static methods ``getAllProjects`` which returns a list of all projects
"""

@strict
class Project:
    """
    This class represents a project in Knora.

    Attributes
    ----------

    con : Connection
        A Connection instance to a Knora server

    id : str
        IRI of the project [readonly, cannot be modified after creation of instance]

    shortcode : str
        Knora project shortcode [readonly, cannot be modified after creation of instance]

    shortname : str
        Knora project shortname [read/write]

    longname : str
        Knora project longname [read/write]

    description : LangString
        Knora project description in a given language (Languages.EN, Languages.DE, Languages.FR, Languages.IT).
        A desciption can be add/replaced or removed with the methods ``addDescription``and ``rmDescription``.

    keywords : Set[str]
        Set of keywords describing the project. Keywords can be added/removed by the methods ``addKeyword``
        and ``rmKeyword``

    ontologies : Set[str]
        Set if IRI's of te ontologies attached to the project [readonly]

    selfjoin : bool
        Boolean if the project allows selfjoin


    Methods
    -------

    create : Knora project information object
        Creates a new project and returns the information from the project as it is in Knora

    read : Knora project information object
        Read project data from an existing project

    update : Knora project information object
        Updates the changed attributes and returns the updated information from the project as it is in Knora

    delete : Knora result code
        Deletes a project and returns the result code

    getAllprojects [static]: List of all projects
        Returns a list of all projects available

    print : None
        Prints the project information to stdout

    """
    __id: str
    __shortcode: str
    __shortname: str
    __longname: str
    __description: LangString
    __keywords: Set[str]
    __ontologies: Set[str]
    __selfjoin: bool
    __status: bool
    __logo: Optional[str]
    __changed: Set[str]

    SYSTEM_PROJECT: str = "http://www.knora.org/ontology/knora-admin#SystemProject"

    def __init__(self,
                 con:  Connection,
                 id: Optional[str] = None,
                 shortcode: Optional[str] = None,
                 shortname: Optional[str] = None,
                 longname: Optional[str] = None,
                 description: LangStringParam = None,
                 keywords: Optional[Set[str]] = None,
                 ontologies: Optional[Set[str]] = None,
                 selfjoin: Optional[bool] = None,
                 status: Optional[bool] = None,
                 logo: Optional[str] = None):
        """
        Constructor for Project

        :param con: Connection instance
        :param id: IRI of the project [required for CREATE, READ]
        :param shortcode: Shortcode of the project. String inf the form 'XXXX' where each X is a hexadezimal sign 0-1,A,B,C,D,E,F. [required for CREATE]
        :param shortname: Shortname of the project [required for CREATE]
        :param longname: Longname of the project [required for CREATE]
        :param description: LangString instance containing the description [required for CREATE]
        :param keywords: Set of keywords [required for CREATE]
        :param ontologies: Set of ontologies that belong to this project [optional]
        :param selfjoin: Allow selfjoin [required for CREATE]
        :param status: Status of project (active if True) [required for CREATE]
        :param logo: Path to logo image file [optional] NOT YET USED
        """

        if not isinstance(con, Connection):
           raise BaseError ('"con"-parameter must be an instance of Connection')
        self.con = con
        self.__id = id
        self.__shortcode = shortcode
        self.__shortname = shortname
        self.__longname = longname
        self.__description = LangString(description)
        self.__keywords = keywords
        if not isinstance(ontologies, set) and ontologies is not None:
            raise BaseError('Ontologies must be a set of strings or None!')
        self.__ontologies = ontologies
        self.__selfjoin = selfjoin
        self.__status = status
        self.__logo = logo
        self.__changed = set()

    def __str__(self):
        tmpstr = self.__id + "\n  " + self.__shortcode + "\n  " + self.__shortname
        return tmpstr

    #
    # Here follows a list of getters/setters
    #
    @property
    def id(self) -> Optional[str]:
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('Project id cannot be modified!')

    @property
    def shortcode(self) -> Optional[str]:
        return self.__shortcode

    @shortcode.setter
    def shortcode(self, value: str) -> None:
        raise BaseError('Shortcode id cannot be modified!')

    @property
    def shortname(self) -> Optional[str]:
        return self.__shortname

    @shortname.setter
    def shortname(self, value: str) -> None:
        if self.__shortname != str(value):
            self.__shortname = str(value)
            self.__changed.add('shortname')

    @property
    def longname(self) -> Optional[str]:
        return self.__longname

    @longname.setter
    def longname(self, value: str) -> None:
        if self.__longname != str(value):
            self.__longname = str(value)
            self.__changed.add('longname')

    @property
    def description(self) -> Optional[LangString]:
        return self.__description

    @description.setter
    def description(self, value: Optional[LangString]) -> None:
        self.__description = LangString(value)
        self.__changed.add('description')

    def addDescription(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a project description with the given language (executed at next update)

        :param lang: The language the description is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the description
        :return: None
        """

        self.__description[lang] = value
        self.__changed.add('description')

    def rmDescription(self, lang: Union[Languages, str]) -> None:
        """
        Remove a description from a project (executed at next update)

        :param lang: The language the description to be removed is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :return: None
        """

        del self.__description[lang]
        self.__changed.add('description')

    @property
    def keywords(self) -> Set[str]:
        return self.__keywords

    @keywords.setter
    def keywords(self, value: Union[List[str], Set[str]]):
        if isinstance(value, set):
            self.__keywords = value
            self.__changed.add('keywords')
        elif isinstance(value, list):
            self.__keywords = set(value)
            self.__changed.add('keywords')
        else:
            raise BaseError('Must be a set of strings!')

    def addKeyword(self, value: str):
        """
        Add a new keyword to the set of keywords. (executed at next update)
        May raise a BaseError

        :param value: keyword
        :return: None
        """

        self.__keywords.add(value)
        self.__changed.add('keywords')

    def rmKeyword(self, value: str):
        """
        Remove a keyword from the list of keywords (executed at next update)
        May raise a BaseError

        :param value: keyword
        :return: None
        """
        try:
            self.__keywords.remove(value)
        except KeyError as ke:
            raise BaseError('Keyword "'  + value + '" is not in keyword set')
        self.__changed.add('keywords')

    @property
    def ontologies(self) -> Set[str]:
        return self.__ontologies

    @ontologies.setter
    def ontologies(self, value: Set[str]) -> None:
        raise BaseError('Cannot add a ontology!')

    @property
    def selfjoin(self) -> Optional[bool]:
        return self.__selfjoin

    @selfjoin.setter
    def selfjoin(self, value: bool) -> None:
        if self.__selfjoin != value:
            self.__changed.add('selfjoin')
            self.__selfjoin = value

    @property
    def status(self) -> bool:
        return self.__status

    @status.setter
    def status(self, value: bool) -> None:
        if self.__status != value:
            self.__status = value
            self.__changed.add('status')

    @property
    def logo(self) -> str:
        return self.__logo

    @logo.setter
    def logo(self, value: str) -> None:
        if self.__logo != value:
            self.__logo = value
            self.__changed.add('logo')

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> Any:
        """
        Internal method! Should not be used directly!

        This method is used to create a Project instance from the JSON data returned by Knora

        :param con: Connection instance
        :param json_obj: JSON data returned by Knora as python3 object
        :return: Project instance
        """

        id = json_obj.get('id')
        if id is None:
            raise BaseError('Project id is missing')
        shortcode = json_obj.get('shortcode')
        if shortcode is None:
            raise BaseError("Shortcode is missing")
        shortname = json_obj.get('shortname')
        if shortname is None:
            raise BaseError("Shortname is missing")
        longname = json_obj.get('longname')
        if longname is None:
            raise BaseError("Longname is missing")
        description = LangString.fromJsonObj(json_obj.get('description'))
        keywords = set(json_obj.get('keywords'))
        if keywords is None:
            raise BaseError("Keywords are missing")
        ontologies = set(json_obj.get('ontologies'))
        if ontologies is None:
            raise BaseError("Keywords are missing")
        selfjoin = json_obj.get('selfjoin')
        if selfjoin is None:
            raise BaseError("Selfjoin is missing")
        status = json_obj.get('status')
        if status is None:
            raise BaseError("Status is missing")
        logo = json_obj.get('logo')
        return cls(con=con,
                   id=id,
                   shortcode=shortcode,
                   shortname=shortname,
                   longname=longname,
                   description=description,
                   keywords=keywords,
                   ontologies=ontologies,
                   selfjoin=selfjoin,
                   status=status,
                   logo=logo)

    def toJsonObj(self, action: Actions) -> Any:
        """
        Internal method! Should not be used directly!

        Creates a JSON-object from the Project instance that can be used to call Knora

        :param action: Action the object is used for (Action.CREATE or Action.UPDATE)
        :return: JSON-object
        """

        tmp = {}
        if action == Actions.Create:
            if self.__shortcode is None:
                raise BaseError("There must be a valid project shortcode!")
            tmp['shortcode'] = self.__shortcode
            if self.__shortname is None:
                raise BaseError("There must be a valid project shortname!")
            tmp['shortname'] = self.__shortname
            if self.__longname is None:
                raise BaseError("There must be a valid project longname!")
            tmp['longname'] = self.__longname
            if self.__description.isEmpty():
                raise BaseError("There must be a valid project description!")
            tmp['description'] = self.__description.toJsonObj()
            if self.__keywords is not None and len(self.__keywords) > 0:
                tmp['keywords'] = self.__keywords
            if self.__selfjoin is None:
                raise BaseError("selfjoin must be defined (True or False!")
            tmp['selfjoin'] = self.__selfjoin
            if self.__status is None:
                raise BaseError("status must be defined (True or False!")
            tmp['status'] = self.__status
        elif action == Actions.Update:
            if self.__shortcode is not None and 'shortcode' in self.__changed:
                tmp['shortcode'] = self.__shortcode
            if self.__shortname is not None  and 'shortname' in self.__changed:
                tmp['shortname'] = self.__shortname
            if self.__longname is not None and 'longname' in self.__changed:
                tmp['longname'] = self.__longname
            if not self.__description.isEmpty() and 'description' in self.__changed:
                tmp['description'] = self.__description.toJsonObj()
            if len(self.__keywords) > 0 and 'keywords' in self.__changed:
                tmp['keywords'] = self.__keywords
            if self.__selfjoin is not None and 'selfjoin' in self.__changed:
                tmp['selfjoin'] = self.__selfjoin
            if self.__status is not None and 'status' in self.__changed:
                tmp['status'] = self.__status
        return tmp

    def createDefinitionFileObj(self):
        return {
            "shortcode": self.__shortcode,
            "shortname": self.__shortname,
            "longname": self.__longname,
            "descriptions": self.__description.createDefinitionFileObj(),
            "keywords": [kw for kw in self.__keywords]
        }

    def create(self) -> 'Project':
        """
        Create a new project in Knora

        :return: JSON-object from Knora
        """

        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        result = self.con.post('/admin/projects', jsondata)
        return Project.fromJsonObj(self.con, result['project'])

    def read(self) -> 'Project':
        """
        Read a project from Knora

        :return: JSON-object from Knora
        """
        result = None
        if self.__id is not None:
            result = self.con.get('/admin/projects/iri/' + quote_plus(self.__id))
        elif self.__shortcode is not None:
            result = self.con.get('/admin/projects/shortcode/' + quote_plus(self.__shortcode))
        elif self.__shortname is not None:
            result = self.con.get('/admin/projects/shortname/' + quote_plus(self.__shortname))
        if result is not None:
            return Project.fromJsonObj(self.con, result['project'])
        else:
            return None

    def update(self) -> Union['Project', None]:
        """
        Udate the project info in Knora with the modified data in this project instance

        :return: JSON-object from Knora refecting the update
        """

        jsonobj = self.toJsonObj(Actions.Update)
        if jsonobj:
            jsondata = json.dumps(jsonobj, cls=SetEncoder)
            result = self.con.put('/admin/projects/iri/' + quote_plus(self.id), jsondata)
            return Project.fromJsonObj(self.con, result['project'])
        else:
            return None

    def delete(self) -> 'Project':
        """
        Delete the given Knora project

        :return: Knora response
        """

        result = self.con.delete('/admin/projects/iri/' + quote_plus(self.__id))
        return Project.fromJsonObj(self.con, result['project'])

    @staticmethod
    def getAllProjects(con: Connection) -> List['Project']:
        """
        Get all existing projects in Knora

        :param con: Connection instance
        :return:
        """
        result = con.get('/admin/projects')
        if 'projects' not in result:
            raise BaseError("Request got no projects!")
        return list(map(lambda a: Project.fromJsonObj(con, a), result['projects']))

    def print(self):
        """
        print info to stdout

        :return: None
        """

        print('Project Info:')
        print('  Id:         {}'.format(self.__id))
        print('  Shortcode:  {}'.format(self.__shortcode))
        print('  Shortname:  {}'.format(self.__shortname))
        print('  Longname:   {}'.format(self.__longname))
        if self.__description is not None:
            print('  Description:')
            for descr in self.__description.items():
                print('    {}: {}'.format(descr[0], descr[1]))
        else:
            print('  Description: None')
        if self.__keywords is not None:
            print('  Keywords:   {}'.format(' '.join(self.__keywords)))
        else:
            print('  Keywords:   None')
        if self.__ontologies is not None:
            print('  Ontologies: {}'.format(' '.join(self.__ontologies)))
        else:
            print('  Ontologies: None')
        print('  Selfjoin:   {}'.format(self.__selfjoin))
        print('  Status:     {}'.format(self.__status))

if __name__ == '__main__':
    con = Connection('http://0.0.0.0:3333')
    con.login('root@example.com', 'test')

    projects = Project.getAllProjects(con)

    for project in projects:
        project.print()

    new_project = Project(con=con,
                               shortcode='F11F',
                               shortname='mytest3',
                               longname='A Test beloning to me',
                               description=LangString({Languages.EN: 'My Tests description'}),
                               keywords={'AAA', 'BBB'},
                               selfjoin=False,
                               status=True).create()

    new_project.print()

    new_project.longname = 'A long name fore a short project'
    new_project.status = False
    new_project.description = LangString({Languages.DE: 'Beschreibung meines Tests'})
    new_project.add_keyword('CCC')
    new_project = new_project.update()
    new_project.print()

    new_project = new_project.delete()

    print('**************************************************************')
    projects = Project.getAllProjects(con)

    for project in projects:
        project.print()
