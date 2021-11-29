import json
from pprint import pprint
from typing import List, Set, Optional, Any, Union
from urllib.parse import quote_plus

from pystrict import strict

from knora.dsplib.utils.set_encoder import SetEncoder
from .connection import Connection
from .helpers import Actions, BaseError
from .langstring import Languages, LangStringParam, LangString
from .model import Model


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
class Project(Model):
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
        Set if IRI's of the ontologies attached to the project [readonly]

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
    _id: str
    _shortcode: str
    _shortname: str
    _longname: str
    _description: LangString
    _keywords: Set[str]
    _ontologies: Set[str]
    _selfjoin: bool
    _status: bool
    _logo: Optional[str]

    SYSTEM_PROJECT: str = "http://www.knora.org/ontology/knora-admin#SystemProject"

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 shortcode: Optional[str] = None,
                 shortname: Optional[str] = None,
                 longname: Optional[str] = None,
                 description: LangString = None,
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
        super().__init__(con)
        self._id = id
        self._shortcode = shortcode
        self._shortname = shortname
        self._longname = longname
        self._description = LangString(description)
        self._keywords = keywords
        if not isinstance(ontologies, set) and ontologies is not None:
            raise BaseError('Ontologies must be a set of strings or None!')
        self._ontologies = ontologies
        self._selfjoin = selfjoin
        self._status = status
        self._logo = logo

    def __str__(self):
        tmpstr = self._id + "\n  " + self._shortcode + "\n  " + self._shortname
        return tmpstr

    #
    # Here follows a list of getters/setters
    #
    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('Project id cannot be modified!')

    @property
    def shortcode(self) -> Optional[str]:
        return self._shortcode

    @shortcode.setter
    def shortcode(self, value: str) -> None:
        raise BaseError('Shortcode id cannot be modified!')

    @property
    def shortname(self) -> Optional[str]:
        return self._shortname

    @shortname.setter
    def shortname(self, value: str) -> None:
        if self._shortname != str(value):
            self._shortname = str(value)
            self._changed.add('shortname')

    @property
    def longname(self) -> Optional[str]:
        return self._longname

    @longname.setter
    def longname(self, value: str) -> None:
        if self._longname != str(value):
            self._longname = str(value)
            self._changed.add('longname')

    @property
    def description(self) -> Optional[LangString]:
        return self._description

    @description.setter
    def description(self, value: Optional[LangString]) -> None:
        self._description = LangString(value)
        self._changed.add('description')

    def addDescription(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a project description with the given language (executed at next update)

        :param lang: The language the description is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the description
        :return: None
        """

        self._description[lang] = value
        self._changed.add('description')

    def rmDescription(self, lang: Union[Languages, str]) -> None:
        """
        Remove a description from a project (executed at next update)

        :param lang: The language the description to be removed is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :return: None
        """

        del self._description[lang]
        self._changed.add('description')

    @property
    def keywords(self) -> Set[str]:
        return self._keywords

    @keywords.setter
    def keywords(self, value: Union[List[str], Set[str]]):
        if isinstance(value, set):
            self._keywords = value
            self._changed.add('keywords')
        elif isinstance(value, list):
            self._keywords = set(value)
            self._changed.add('keywords')
        else:
            raise BaseError('Must be a set of strings!')

    def addKeyword(self, value: str):
        """
        Add a new keyword to the set of keywords. (executed at next update)
        May raise a BaseError

        :param value: keyword
        :return: None
        """

        self._keywords.add(value)
        self._changed.add('keywords')

    def rmKeyword(self, value: str):
        """
        Remove a keyword from the list of keywords (executed at next update)
        May raise a BaseError

        :param value: keyword
        :return: None
        """
        try:
            self._keywords.remove(value)
        except KeyError as ke:
            raise BaseError('Keyword "' + value + '" is not in keyword set')
        self._changed.add('keywords')

    @property
    def ontologies(self) -> Set[str]:
        return self._ontologies

    @ontologies.setter
    def ontologies(self, value: Set[str]) -> None:
        raise BaseError('Cannot add a ontology!')

    @property
    def selfjoin(self) -> Optional[bool]:
        return self._selfjoin

    @selfjoin.setter
    def selfjoin(self, value: bool) -> None:
        if self._selfjoin != value:
            self._changed.add('selfjoin')
            self._selfjoin = value

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: bool) -> None:
        if self._status != value:
            self._status = value
            self._changed.add('status')

    @property
    def logo(self) -> str:
        return self._logo

    @logo.setter
    def logo(self, value: str) -> None:
        if self._logo != value:
            self._logo = value
            self._changed.add('logo')

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
            raise BaseError("ontologies are missing")
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
            if self._shortcode is None:
                raise BaseError("There must be a valid project shortcode!")
            tmp['shortcode'] = self._shortcode
            if self._shortname is None:
                raise BaseError("There must be a valid project shortname!")
            tmp['shortname'] = self._shortname
            if self._longname is None:
                raise BaseError("There must be a valid project longname!")
            tmp['longname'] = self._longname
            if self._description.isEmpty():
                raise BaseError("There must be a valid project description!")
            tmp['description'] = self._description.toJsonObj()
            if self._keywords is not None and len(self._keywords) > 0:
                tmp['keywords'] = self._keywords
            if self._selfjoin is None:
                raise BaseError("selfjoin must be defined (True or False!")
            tmp['selfjoin'] = self._selfjoin
            if self._status is None:
                raise BaseError("status must be defined (True or False!")
            tmp['status'] = self._status
        elif action == Actions.Update:
            if self._shortcode is not None and 'shortcode' in self._changed:
                tmp['shortcode'] = self._shortcode
            if self._shortname is not None and 'shortname' in self._changed:
                tmp['shortname'] = self._shortname
            if self._longname is not None and 'longname' in self._changed:
                tmp['longname'] = self._longname
            if not self._description.isEmpty() and 'description' in self._changed:
                tmp['description'] = self._description.toJsonObj()
            if len(self._keywords) > 0 and 'keywords' in self._changed:
                tmp['keywords'] = self._keywords
            if self._selfjoin is not None and 'selfjoin' in self._changed:
                tmp['selfjoin'] = self._selfjoin
            if self._status is not None and 'status' in self._changed:
                tmp['status'] = self._status
        return tmp

    def createDefinitionFileObj(self):
        return {
            "shortcode": self._shortcode,
            "shortname": self._shortname,
            "longname": self._longname,
            "descriptions": self._description.createDefinitionFileObj(),
            "keywords": [kw for kw in self._keywords]
        }

    def create(self) -> 'Project':
        """
        Create a new project in Knora

        :return: JSON-object from Knora
        """

        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        result = self._con.post('/admin/projects', jsondata)
        return Project.fromJsonObj(self._con, result['project'])

    def read(self) -> 'Project':
        """
        Read a project from Knora

        :return: JSON-object from Knora
        """
        result = None
        if self._id is not None:
            result = self._con.get('/admin/projects/iri/' + quote_plus(self._id))
        elif self._shortcode is not None:
            result = self._con.get('/admin/projects/shortcode/' + quote_plus(self._shortcode))
        elif self._shortname is not None:
            result = self._con.get('/admin/projects/shortname/' + quote_plus(self._shortname))
        if result is not None:
            return Project.fromJsonObj(self._con, result['project'])
        else:
            return None  # Todo: throw exception

    def update(self) -> Union['Project', None]:
        """
        Udate the project info in Knora with the modified data in this project instance

        :return: JSON-object from Knora refecting the update
        """

        jsonobj = self.toJsonObj(Actions.Update)
        if jsonobj:
            jsondata = json.dumps(jsonobj, cls=SetEncoder)
            result = self._con.put('/admin/projects/iri/' + quote_plus(self.id), jsondata)
            return Project.fromJsonObj(self._con, result['project'])
        else:
            return None

    def delete(self) -> 'Project':
        """
        Delete the given Knora project

        :return: Knora response
        """

        result = self._con.delete('/admin/projects/iri/' + quote_plus(self._id))
        return Project.fromJsonObj(self._con, result['project'])

    def set_default_permissions(self, group_id: str) -> None:
        permobj = {
            "forGroup": "http://www.knora.org/ontology/knora-admin#ProjectMember",
            "forProject": self._id,
            "hasPermissions": [
                {
                    "additionalInformation": None,
                    "name": "ProjectResourceCreateAllPermission",
                    "permissionCode": None
                }
            ]
        }
        jsondata = json.dumps(permobj, indent=4)
        print(jsondata)
        result = self._con.post("/admin/permissions/ap", jsondata)
        pprint(result)

        return
        permobj = {
            "forGroup": group_id,
            "forProject": self._id,
            "forProperty": None,
            "forResourceClass": None,
            "hasPermissions": [
                {
                    "additionalInformation": "http://www.knora.org/ontology/knora-admin#ProjectMember",
                    "name": "D",
                    "permissionCode": 7
                }
            ]
        }
        jsondata = json.dumps(permobj)
        result = self._con.post("/admin/permissions/ap", jsondata)
        pprint(result)

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

    def print(self) -> None:
        """
        print info to stdout

        :return: None
        """

        print('Project Info:')
        print('  Id:         {}'.format(self._id))
        print('  Shortcode:  {}'.format(self._shortcode))
        print('  Shortname:  {}'.format(self._shortname))
        print('  Longname:   {}'.format(self._longname))
        if self._description is not None:
            print('  Description:')
            for descr in self._description.items():
                print('    {}: {}'.format(descr[0], descr[1]))
        else:
            print('  Description: None')
        if self._keywords is not None:
            print('  Keywords:   {}'.format(' '.join(self._keywords)))
        else:
            print('  Keywords:   None')
        if self._ontologies is not None:
            print('  Ontologies: {}'.format(' '.join(self._ontologies)))
        else:
            print('  Ontologies: None')
        print('  Selfjoin:   {}'.format(self._selfjoin))
        print('  Status:     {}'.format(self._status))


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
