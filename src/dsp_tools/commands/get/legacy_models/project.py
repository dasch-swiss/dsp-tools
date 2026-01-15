"""
This module implements reading DSP projects.

READ:
    * Instantiate a new object with ``iri`` given
    * Call the ``read``-method on the instance
    * Access the information that has been provided to the instance

"""

from __future__ import annotations

from typing import Any
from typing import Optional
from urllib.parse import quote_plus

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString


class Project:
    """
    This class represents a project in DSP.

    Attributes
    ----------

    con : Connection
        A Connection instance to a DSP server

    iri : str
        IRI of the project [readonly]

    shortcode : str
        DSP project shortcode [readonly]

    shortname : str
        DSP project shortname [readonly]

    longname : str
        DSP project longname [readonly]

    description : LangString
        DSP project description in a given language (Languages.EN, Languages.DE, Languages.FR, Languages.IT).

    keywords : set[str]
        Set of keywords describing the project.

    ontologies : set[str]
        Set of IRI's of the ontologies attached to the project [readonly]

    selfjoin : bool
        Boolean if the project allows selfjoin


    Methods
    -------

    read : DSP project information object
        Read project data from an existing project

    getAllProjects [static]: List of all projects
        Returns a list of all projects available

    """

    ROUTE: str = "/admin/projects"
    IRI: str = ROUTE + "/iri/"

    _con: Connection
    _iri: str
    _shortcode: str
    _shortname: str
    _longname: str
    _description: LangString
    _keywords: set[str]
    _enabled_licenses: set[str]

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        shortcode: Optional[str] = None,
        shortname: Optional[str] = None,
        longname: Optional[str] = None,
        description: LangString = None,
        keywords: Optional[set[str]] = None,
        enabled_licenses: Optional[set[str]] = None,
    ):
        """
        Constructor for Project

        :param con: Connection instance
        :param iri: IRI of the project [required for READ]
        :param shortcode: Shortcode of the project. Four-digit hexadecimal number.
        :param shortname: Shortname of the project
        :param longname: Longname of the project
        :param description: LangString instance containing the description
        :param keywords: Set of keywords
        :param enabled_licenses: Set of enabled licenses [optional]
        """
        self._con = con
        self._iri = iri
        self._shortcode = shortcode
        self._shortname = shortname
        self._longname = longname
        self._description = LangString(description)
        self._keywords = keywords
        self._enabled_licenses = enabled_licenses or set()

    @property
    def iri(self) -> Optional[str]:
        return self._iri

    @property
    def shortcode(self) -> Optional[str]:
        return self._shortcode

    @property
    def shortname(self) -> Optional[str]:
        return self._shortname

    @property
    def longname(self) -> Optional[str]:
        return self._longname

    @property
    def description(self) -> LangString:
        return self._description or LangString({})

    @property
    def keywords(self) -> set[str]:
        return self._keywords

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
        enabled_licenses = json_obj.get("enabledLicenses", set())
        return cls(
            con=con,
            iri=iri,
            shortcode=shortcode,
            shortname=shortname,
            longname=longname,
            description=description,
            keywords=keywords,
            enabled_licenses=enabled_licenses,
        )

    def createDefinitionFileObj(self) -> dict[str, Any]:
        return {
            "shortcode": self._shortcode,
            "shortname": self._shortname,
            "longname": self._longname,
            "descriptions": self._description.createDefinitionFileObj(),
            "keywords": list(self._keywords),
            "enabled_licenses": list(self._enabled_licenses),
        }

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

    @staticmethod
    def getAllProjects(con: Connection) -> list[Project]:
        """
        Get all existing projects in DSP

        :param con: Connection instance
        :return:
        """
        try:
            result = con.get(Project.ROUTE)
            return [Project.fromJsonObj(con, a) for a in result["projects"]]
        except BaseError:
            return []
