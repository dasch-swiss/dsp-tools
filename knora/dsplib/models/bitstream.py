import re
from typing import List, Dict, Optional, Any, Union

from pystrict import strict

from .group import Group
from .helpers import IriTest, Actions, BaseError
from .langstring import LangString
from .listnode import ListNode
from .permission import PermissionValue, Permissions


@strict
class Bitstream:
    _permissions: Union[Permissions, None]
    _upermission: Union[PermissionValue, None]
    _ark_url: Union[str, None]
    _vark_url: Union[str, None]

    def __init__(self,
                 iri: Optional[str] = None,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        self._iri = iri
        self._comment = comment
        self._permissions = permissions
        self._upermission = upermission
        self._ark_url = ark_url
        self._vark_url = vark_url

    def __str__(self):
        if self._iri:
            tmpstr = "(iri: " + self._iri
        else:
            tmpstr = '(iri: -'
        if self._permissions:
            tmpstr = ", permissions: " + str(self._permissions)
        if self._comment:
            tmpstr += ", comment: " + self._comment
        tmpstr += ")"
        return tmpstr

    @property
    def iri(self) -> str:
        return self.iri

    @property
    def ark_url(self) -> str:
        return self._ark_url

    @property
    def vark_url(self) -> str:
        return self._vark_url

    @property
    def permissions(self) -> Optional[Permissions]:
        return self._permissions

    @property
    def upermission(self) -> Optional[PermissionValue]:
        return self._upermission

    @property
    def comment(self):
        return self._comment

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = {}
        if action == Actions.Create:
            if self._permissions is not None:
                tmp["knora-api:hasPermissions"] = self.permissions.toJsonLdObj()

            if self._comment is not None:
                tmp["knora-api:valueHasComment"] = str(self._comment)
        else:
            pass
        return tmp

    @staticmethod
    def getFromJsonLd(jsonld_obj) -> Dict[str, Union[str, float]]:
        return {
            'iri': jsonld_obj.get("@id"),
            'comment': jsonld_obj.get("knora-api:valueHasComment"),
            'ark_url': jsonld_obj.get("knora-api:arkUrl"),
            'vark_url': jsonld_obj.get("knora-api:versionArkUrl"),
            'permissions': Permissions.fromString(jsonld_obj.get("knora-api:hasPermissions")),
            'upermission': PermissionValue[jsonld_obj.get("knora-api:userHasPermission", jsonld_obj)]
        }
