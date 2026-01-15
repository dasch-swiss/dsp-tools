"""
This module implements reading DSP groups.
"""

from __future__ import annotations

from typing import Any
from typing import Optional
from typing import Union

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.project import Project
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString


class Group:
    """
    This class represents a DSP group

    Attributes
    ----------

    iri : str
        IRI of the group [readonly]

    name : str
        Name of the group [readonly]

    descriptions : LangString
        Group descriptions in a given language (Languages.EN, Languages.DE, Languages.FR, Languages.IT, Languages.RM).

    project : str
        IRI of the project [readonly]

    selfjoin : boolean
        A flag indicating if selfjoin is allowed in this group

    status : boolean
        A flag indicating if the group is active (True) or inactive/marked deleted (False)

    """

    PROJECT_MEMBER_GROUP: str = "http://www.knora.org/ontology/knora-admin#ProjectMember"
    PROJECT_ADMIN_GROUP: str = "http://www.knora.org/ontology/knora-admin#ProjectAdmin"
    ROUTE: str = "/admin/groups"

    _iri: Optional[str]
    _name: str | None
    _descriptions: LangString
    _project: str
    _selfjoin: bool
    _status: bool

    def __init__(
        self,
        iri: Optional[str] = None,
        name: Optional[str] = None,
        descriptions: Optional[LangString] = None,
        project: Optional[Union[str, Project]] = None,
        selfjoin: Optional[bool] = None,
        status: Optional[bool] = None,
    ) -> None:
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

    @property
    def descriptions(self) -> LangString:
        return self._descriptions

    @property
    def project(self) -> str:
        return self._project

    @property
    def selfjoin(self) -> bool:
        return self._selfjoin

    @property
    def status(self) -> bool:
        return self._status

    @classmethod
    def fromJsonObj(cls, json_obj: Any) -> Group:
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
            name=name,
            iri=group_id,
            descriptions=descriptions,
            project=project,
            selfjoin=selfjoin,
            status=status,
        )

    @staticmethod
    def getAllGroups(con: Connection) -> list[Group]:
        result = con.get(Group.ROUTE)
        return [Group.fromJsonObj(group_item) for group_item in result["groups"]]

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
