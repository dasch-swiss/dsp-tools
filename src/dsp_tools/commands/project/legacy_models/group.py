"""
This module implements the handling (CRUD) of DSP groups.

CREATE:
    * Instantiate a new object of the class Group with all required parameters
    * Call the ``create``-method on the instance

READ:
    * Instantiate a new object with ``iri``(IRI of group) given
    * Call the ``read``-method on the instance
    * Access the information that has been provided to the instance

UPDATE:
    * You need an instance of an existing Project by reading an instance
    * Change the attributes by assigning the new values
    * Call the ``update```method on the instance

DELETE
    * Instantiate a new objects with ``iri``(IRI of group) given, or use any instance that has the iri set
    * Call the ``delete``-method on the instance

"""

from __future__ import annotations

from typing import Any
from typing import Optional
from typing import Union
from urllib.parse import quote_plus

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.project.legacy_models.model import Model
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString


class Group(Model):
    """
    This class represents a DSP group

    Attributes
    ----------

    con : Connection
        A connection instance to a DSP server

    iri : str
        IRI of the group [get only, cannot be modified after creation of instance]

    name : str
        Name of the group

    descriptions : LangString
        Group descriptions in a given language (Languages.EN, Languages.DE, Languages.FR, Languages.IT, Languages.RM).

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
    ROUTE: str = "/admin/groups"
    ROUTE_SLASH: str = ROUTE + "/"

    _iri: Optional[str]
    _name: str | None
    _descriptions: LangString
    _project: str
    _selfjoin: bool
    _status: bool

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        name: Optional[str] = None,
        descriptions: Optional[LangString] = None,
        project: Optional[Union[str, Project]] = None,
        selfjoin: Optional[bool] = None,
        status: Optional[bool] = None,
    ) -> None:
        super().__init__(con)
        self._iri = iri
        self._name = str(name) if name is not None else None
        self._descriptions = LangString(descriptions)
        if project is not None and isinstance(project, Project):
            self._project = project.iri
        else:
            self._project = str(project) if project is not None else None
        self._selfjoin = bool(selfjoin) if selfjoin is not None else None
        self._status = bool(status) if status is not None else None

    @property
    def iri(self) -> Optional[str]:
        return self._iri

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        self._changed.add("name")

    @property
    def descriptions(self) -> LangString:
        return self._descriptions

    @descriptions.setter
    def descriptions(self, value: Optional[LangString]) -> None:
        self._descriptions = LangString(value)
        self._changed.add("descriptions")

    @property
    def project(self) -> str:
        return self._project

    @property
    def selfjoin(self) -> bool:
        return self._selfjoin

    @selfjoin.setter
    def selfjoin(self, value: bool) -> None:
        self._selfjoin = value
        self._changed.add("selfjoin")

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: bool) -> None:
        self._status = value
        self._changed.add("status")

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> Group:
        group_id = json_obj.get("id")
        if group_id is None:
            raise BaseError('Group "id" is missing')
        name = json_obj.get("name")
        if name is None:
            raise BaseError('Group "name" is missing')
        descriptions = LangString.fromJsonObj(json_obj.get("descriptions"))
        tmp = json_obj.get("project")
        if tmp is None:
            raise BaseError('Group "project" is missing')
        project = tmp.get("id")
        if project is None:
            raise BaseError('Group "project" has no "id"')
        selfjoin = json_obj.get("selfjoin")
        if selfjoin is None:
            raise BaseError("selfjoin is missing")
        status = json_obj.get("status")
        if status is None:
            raise BaseError("Status is missing")
        return cls(
            con=con,
            name=name,
            iri=group_id,
            descriptions=descriptions,
            project=project,
            selfjoin=selfjoin,
            status=status,
        )

    def create(self) -> Group:
        jsonobj = self._toJsonObj_create()
        result = self._con.post(Group.ROUTE, jsonobj)
        return Group.fromJsonObj(self._con, result["group"])

    def _toJsonObj_create(self):
        tmp = {}
        if self._name is None:
            raise BaseError("There must be a valid name!")
        tmp["name"] = self._name
        if not self._descriptions.isEmpty():
            tmp["descriptions"] = self._descriptions.toJsonObj()
        if self._project is None:
            raise BaseError("There must be a valid project!")
        tmp["project"] = self._project
        if self._selfjoin is None:
            raise BaseError("There must be a valid value for selfjoin!")
        tmp["selfjoin"] = self._selfjoin
        if self._status is None:
            raise BaseError("There must be a valid value for status!")
        tmp["status"] = self._status
        return tmp

    def read(self) -> Group:
        result = self._con.get(Group.ROUTE_SLASH + quote_plus(self._iri))
        return Group.fromJsonObj(self._con, result["group"])

    def update(self) -> Optional[Group]:
        updated_group = None
        jsonobj = self._toJsonObj_update()
        if jsonobj:
            result = self._con.put(Group.ROUTE_SLASH + quote_plus(self._iri), jsonobj)
            updated_group = Group.fromJsonObj(self._con, result["group"])
        if self._status is not None and "status" in self._changed:
            jsonobj = {"status": self._status}
            result = self._con.put(Group.ROUTE_SLASH + quote_plus(self._iri) + "/status", jsonobj)
            updated_group = Group.fromJsonObj(self._con, result["group"])
        return updated_group

    def _toJsonObj_update(self) -> dict[str, Any]:
        tmp = {}
        if self._name is not None and "name" in self._changed:
            tmp["name"] = self._name
        if not self._descriptions.isEmpty() and "descriptions" in self._changed:
            tmp["descriptions"] = self._descriptions.toJsonObj()
        if self._selfjoin is not None and "selfjoin" in self._changed:
            tmp["selfjoin"] = self._selfjoin
        return tmp

    @staticmethod
    def getAllGroups(con: Connection) -> list[Group]:
        result = con.get(Group.ROUTE)
        return [Group.fromJsonObj(con, group_item) for group_item in result["groups"]]

    @staticmethod
    def getAllGroupsForProject(con: Connection, proj_iri: str) -> list[Group]:
        return [g for g in Group.getAllGroups(con) if g.project == proj_iri]

    def createDefinitionFileObj(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "descriptions": self.descriptions.createDefinitionFileObj(),
            "selfjoin": self.selfjoin,
            "status": self.status,
        }
