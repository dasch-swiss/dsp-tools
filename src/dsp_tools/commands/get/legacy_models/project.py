"""
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
from dsp_tools.commands.get.legacy_models.model import Model
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString


class Project(Model):
    """
    Attributes
    ----------

    con : Connection
        A Connection instance to a DSP server

    iri : str
        IRI of the project [readonly, cannot be modified after creation of instance]

    shortcode : str
        DSP project shortcode [readonly, cannot be modified after creation of instance]

    shortname : str
        DSP project shortname

    longname : str
        DSP project longname

    description : LangString
        DSP project description in a given language (Languages.EN, Languages.DE, Languages.FR, Languages.IT).

    keywords : set[str]
        Set of keywords describing the project.

    ontologies : set[str]
        Set if IRI's of the ontologies attached to the project [readonly]

    selfjoin : bool
        Boolean if the project allows selfjoin
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
    _enabled_licenses: set[str]
    _data_license: Optional[str]
    _data_copyright_holder: Optional[str]
    _default_data_authorship: list[str]
    _selfjoin: bool
    _logo: Optional[str]

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
        enabled_licenses: Optional[set[str]] = None,
        data_license: Optional[str] = None,
        data_copyright_holder: Optional[str] = None,
        default_data_authorship: Optional[list[str]] = None,
        selfjoin: Optional[bool] = None,
        logo: Optional[str] = None,
    ):
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
        self._enabled_licenses = enabled_licenses or set()
        self._data_license = data_license
        self._data_copyright_holder = data_copyright_holder
        self._default_data_authorship = default_data_authorship or []
        self._selfjoin = selfjoin
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

    @property
    def ontologies(self) -> set[str]:
        return self._ontologies

    @property
    def selfjoin(self) -> Optional[bool]:
        return self._selfjoin

    @property
    def logo(self) -> str:
        return self._logo

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
        enabled_licenses = json_obj.get("enabledLicenses", set())
        data_license = json_obj.get("dataLicense")
        data_copyright_holder = json_obj.get("dataCopyrightHolder")
        default_data_authorship = json_obj.get("defaultDataAuthorship", [])
        selfjoin = json_obj.get("selfjoin")
        if selfjoin is None:
            raise BaseError("Selfjoin is missing")
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
            enabled_licenses=enabled_licenses,
            data_license=data_license,
            data_copyright_holder=data_copyright_holder,
            default_data_authorship=default_data_authorship,
            selfjoin=selfjoin,
            logo=logo,
        )

    def createDefinitionFileObj(self) -> dict[str, Any]:
        proj: dict[str, Any] = {
            "shortcode": self._shortcode,
            "shortname": self._shortname,
            "longname": self._longname,
            "descriptions": self._description.createDefinitionFileObj(),
            "keywords": list(self._keywords),
            "enabled_licenses": list(self._enabled_licenses),
        }
        if self._data_license:
            proj["data_license"] = self._data_license
        if self._data_copyright_holder:
            proj["data_copyright_holder"] = self._data_copyright_holder
        if self._default_data_authorship:
            proj["default_data_authorship"] = self._default_data_authorship
        return proj

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
                f"Could not read project '{self.shortname}' ({self.shortcode}) with IRI {self._iri} from DSP server."
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
