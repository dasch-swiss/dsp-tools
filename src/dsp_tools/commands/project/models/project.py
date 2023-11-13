# pylint: disable=missing-class-docstring,missing-function-docstring

"""
This module implements the handling (CRUD) of DSP projects.

CREATE:
    * Instantiate a new object of the class Project with all required parameters
    * Call the ``create``-method on the instance

READ:
    * Instantiate a new object with ``iri`` given
    * Call the ``read``-method on the instance
    * Access the information that has been provided to the instance

UPDATE:
    * You need an instance of an existing Project by reading an instance
    * Change the attributes by assigning the new values
    * Call the ``update```method on the instance

DELETE
    * Instantiate a new objects with ``iri`` given, or use any instance that has the iri set
    * Call the ``delete``-method on the instance

In addition there is a static methods ``getAllProjects`` which returns a list of all projects
"""

from __future__ import annotations

import json
from typing import Any, Optional, Union
from urllib.parse import quote_plus

from dsp_tools.commands.project.models.model import Model
from dsp_tools.commands.project.models.set_encoder import SetEncoder
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.helpers import Actions
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection import Connection


class Project(Model):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    This class represents a project in DSP.

    Attributes
    ----------

    con : Connection
        A Connection instance to a DSP server

    iri : str
        IRI of the project [readonly, cannot be modified after creation of instance]

    shortcode : str
        DSP project shortcode [readonly, cannot be modified after creation of instance]

    shortname : str
        DSP project shortname [read/write]

    longname : str
        DSP project longname [read/write]

    description : LangString
        DSP project description in a given language (Languages.EN, Languages.DE, Languages.FR, Languages.IT).
        A desciption can be add/replaced or removed with the methods ``addDescription``and ``rmDescription``.

    keywords : set[str]
        Set of keywords describing the project. Keywords can be added/removed by the methods ``addKeyword``
        and ``rmKeyword``

    ontologies : set[str]
        Set if IRI's of the ontologies attached to the project [readonly]

    selfjoin : bool
        Boolean if the project allows selfjoin


    Methods
    -------

    create : DSP project information object
        Creates a new project and returns the information from the project as it is in DSP

    read : DSP project information object
        Read project data from an existing project

    update : DSP project information object
        Updates the changed attributes and returns the updated information from the project as it is in DSP

    delete : DSP result code
        Deletes a project and returns the result code

    getAllprojects [static]: List of all projects
        Returns a list of all projects available

    print : None
        Prints the project information to stdout

    """

    ROUTE: str = "/admin/projects"
    IRI: str = ROUTE + "/iri/"

    _iri: str
    _shortcode: str
    _shortname: str
    _longname: str
    _description: LangString
    _keywords: set[str]
    _ontologies: set[str]
    _selfjoin: bool
    _status: bool
    _logo: Optional[str]

    SYSTEM_PROJECT: str = "http://www.knora.org/ontology/knora-admin#SystemProject"

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        shortcode: Optional[str] = None,
        shortname: Optional[str] = None,
        longname: Optional[str] = None,
        description: LangString = None,
        keywords: Optional[set[str]] = None,
        ontologies: Optional[set[str]] = None,
        selfjoin: Optional[bool] = None,
        status: Optional[bool] = None,
        logo: Optional[str] = None,
    ):
        """
        Constructor for Project

        :param con: Connection instance
        :param iri: IRI of the project [required for CREATE, READ]
        :param shortcode: Shortcode of the project. Four-digit hexadecimal number. [required for CREATE]
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
        self._iri = iri
        self._shortcode = shortcode
        self._shortname = shortname
        self._longname = longname
        self._description = LangString(description)
        self._keywords = keywords
        if not isinstance(ontologies, set) and ontologies is not None:
            raise BaseError("Ontologies must be a set of strings or None!")
        self._ontologies = ontologies
        self._selfjoin = selfjoin
        self._status = status
        self._logo = logo

    def __str__(self) -> str:
        tmpstr = self._iri + "\n  " + self._shortcode + "\n  " + self._shortname
        return tmpstr

    #
    # Here follows a list of getters/setters
    #
    @property
    def iri(self) -> Optional[str]:
        return self._iri

    @iri.setter
    def iri(self, value: str) -> None:
        raise BaseError("Project iri cannot be modified!")

    @property
    def shortcode(self) -> Optional[str]:
        return self._shortcode

    @shortcode.setter
    def shortcode(self, value: str) -> None:
        raise BaseError("Shortcode id cannot be modified!")

    @property
    def shortname(self) -> Optional[str]:
        return self._shortname

    @shortname.setter
    def shortname(self, value: str) -> None:
        if self._shortname != str(value):
            self._shortname = str(value)
            self._changed.add("shortname")

    @property
    def longname(self) -> Optional[str]:
        return self._longname

    @longname.setter
    def longname(self, value: str) -> None:
        if self._longname != str(value):
            self._longname = str(value)
            self._changed.add("longname")

    @property
    def description(self) -> LangString:
        return self._description or LangString({})

    @description.setter
    def description(self, value: Optional[LangString]) -> None:
        self._description = LangString(value)
        self._changed.add("description")

    def addDescription(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a project description with the given language (executed at next update)

        :param lang: The language the description is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the description
        :return: None
        """

        self._description[lang] = value
        self._changed.add("description")

    def rmDescription(self, lang: Union[Languages, str]) -> None:
        """
        Remove a description from a project (executed at next update)

        :param lang: language of the description, either "EN", "DE", "FR", "IT", "RM", or a Language instance
        :return: None
        """

        del self._description[lang]
        self._changed.add("description")

    @property
    def keywords(self) -> set[str]:
        return self._keywords

    @keywords.setter
    def keywords(self, value: Union[list[str], set[str]]) -> None:
        if isinstance(value, set):
            self._keywords = value
            self._changed.add("keywords")
        elif isinstance(value, list):
            self._keywords = set(value)
            self._changed.add("keywords")
        else:
            raise BaseError("Must be a set of strings!")

    def addKeyword(self, value: str) -> None:
        """
        Add a new keyword to the set of keywords. (executed at next update)
        May raise a BaseError

        :param value: keyword
        :return: None
        """

        self._keywords.add(value)
        self._changed.add("keywords")

    def rmKeyword(self, value: str) -> None:
        """
        Remove a keyword from the list of keywords (executed at next update)
        May raise a BaseError

        :param value: keyword
        :return: None
        """
        try:
            self._keywords.remove(value)
        except KeyError as ke:
            raise BaseError('Keyword "' + value + '" is not in keyword set') from ke
        self._changed.add("keywords")

    @property
    def ontologies(self) -> set[str]:
        return self._ontologies

    @ontologies.setter
    def ontologies(self, value: set[str]) -> None:
        raise BaseError("Cannot add a ontology!")

    @property
    def selfjoin(self) -> Optional[bool]:
        return self._selfjoin

    @selfjoin.setter
    def selfjoin(self, value: bool) -> None:
        if self._selfjoin != value:
            self._changed.add("selfjoin")
            self._selfjoin = value

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: bool) -> None:
        if self._status != value:
            self._status = value
            self._changed.add("status")

    @property
    def logo(self) -> str:
        return self._logo

    @logo.setter
    def logo(self, value: str) -> None:
        if self._logo != value:
            self._logo = value
            self._changed.add("logo")

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> Project:
        """
        Internal method! Should not be used directly!

        This method is used to create a Project instance from the JSON data returned by DSP

        :param con: Connection instance
        :param json_obj: JSON data returned by DSP as python3 object
        :return: Project instance
        """
        iri = json_obj.get("id")
        if iri is None:
            raise BaseError("Project iri is missing")
        shortcode = json_obj.get("shortcode")
        if shortcode is None:
            raise BaseError("Shortcode is missing")
        shortname = json_obj.get("shortname")
        if shortname is None:
            raise BaseError("Shortname is missing")
        longname = json_obj.get("longname")
        if longname is None:
            raise BaseError("Longname is missing")
        description = LangString.fromJsonObj(json_obj.get("description"))
        keywords = set(json_obj.get("keywords"))
        if keywords is None:
            raise BaseError("Keywords are missing")
        ontologies = set(json_obj.get("ontologies"))
        if ontologies is None:
            raise BaseError("ontologies are missing")
        selfjoin = json_obj.get("selfjoin")
        if selfjoin is None:
            raise BaseError("Selfjoin is missing")
        status = json_obj.get("status")
        if status is None:
            raise BaseError("Status is missing")
        logo = json_obj.get("logo")
        return cls(
            con=con,
            iri=iri,
            shortcode=shortcode,
            shortname=shortname,
            longname=longname,
            description=description,
            keywords=keywords,
            ontologies=ontologies,
            selfjoin=selfjoin,
            status=status,
            logo=logo,
        )

    def toJsonObj(self, action: Actions) -> dict[str, str]:
        """
        Internal method! Should not be used directly!

        Creates a JSON-object from the Project instance that can be used to call DSP

        :param action: Action the object is used for (Action.CREATE or Action.UPDATE)
        :return: JSON-object
        """

        tmp = {}
        if action == Actions.Create:
            if self._shortcode is None:
                raise BaseError("There must be a valid project shortcode!")
            tmp["shortcode"] = self._shortcode
            if self._shortname is None:
                raise BaseError("There must be a valid project shortname!")
            tmp["shortname"] = self._shortname
            if self._longname is None:
                raise BaseError("There must be a valid project longname!")
            tmp["longname"] = self._longname
            if self._description.isEmpty():
                raise BaseError("There must be a valid project description!")
            tmp["description"] = self._description.toJsonObj()
            if self._keywords is not None and len(self._keywords) > 0:
                tmp["keywords"] = self._keywords
            if self._selfjoin is None:
                raise BaseError("selfjoin must be defined (True or False!")
            tmp["selfjoin"] = self._selfjoin
            if self._status is None:
                raise BaseError("status must be defined (True or False!")
            tmp["status"] = self._status

        elif action == Actions.Update:
            if self._shortcode is not None and "shortcode" in self._changed:
                tmp["shortcode"] = self._shortcode
            if self._shortname is not None and "shortname" in self._changed:
                tmp["shortname"] = self._shortname
            if self._longname is not None and "longname" in self._changed:
                tmp["longname"] = self._longname
            if not self._description.isEmpty() and "description" in self._changed:
                tmp["description"] = self._description.toJsonObj()
            if len(self._keywords) > 0 and "keywords" in self._changed:
                tmp["keywords"] = self._keywords
            if self._selfjoin is not None and "selfjoin" in self._changed:
                tmp["selfjoin"] = self._selfjoin
            if self._status is not None and "status" in self._changed:
                tmp["status"] = self._status
        return tmp

    def createDefinitionFileObj(self) -> dict[str, Any]:
        return {
            "shortcode": self._shortcode,
            "shortname": self._shortname,
            "longname": self._longname,
            "descriptions": self._description.createDefinitionFileObj(),
            "keywords": list(self._keywords),
        }

    def create(self) -> Project:
        """
        Create a new project in DSP

        :return: JSON-object from DSP
        """

        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        result = self._con.post(Project.ROUTE, jsondata)
        return Project.fromJsonObj(self._con, result["project"])

    def read(self) -> Project:
        """
        Read a project from DSP

        :return: JSON-object from DSP
        """
        result = None
        if self._iri is not None:
            result = self._con.get(Project.IRI + quote_plus(self._iri))
        elif self._shortcode is not None:
            result = self._con.get(Project.ROUTE + "/shortcode/" + quote_plus(self._shortcode))
        elif self._shortname is not None:
            result = self._con.get(Project.ROUTE + "/shortname/" + quote_plus(self._shortname))
        if result is not None:
            return Project.fromJsonObj(self._con, result["project"])
        else:
            raise BaseError(
                f"ERROR: Could not read project '{self.shortname}' ({self.shortcode}) with IRI {self._iri} "
                f"from DSP server."
            )

    def update(self) -> Project:
        """
        Update the project information on the DSP with the modified data in this project instance

        Returns: JSON object returned as response from DSP reflecting the update
        """

        jsonobj = self.toJsonObj(Actions.Update)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        result = self._con.put(Project.IRI + quote_plus(self.iri), jsondata)
        return Project.fromJsonObj(self._con, result["project"])

    def delete(self) -> Project:
        """
        Delete the given DSP project

        :return: DSP response
        """

        result = self._con.delete(Project.IRI + quote_plus(self._iri))
        return Project.fromJsonObj(self._con, result["project"])

    @staticmethod
    def getAllProjects(con: Connection) -> list[Project]:
        """
        Get all existing projects in DSP

        :param con: Connection instance
        :return:
        """
        result = con.get(Project.ROUTE)
        if "projects" not in result:
            raise BaseError("Request got no projects!")
        return [Project.fromJsonObj(con, a) for a in result["projects"]]
