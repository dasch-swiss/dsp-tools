from typing import Dict, Optional, Any, Union

from pystrict import strict

from .helpers import Actions
from .langstring import LangString
from .permission import PermissionValue, Permissions


@strict
class Bitstream:
    """
    Represents a bitstream object (file) which is attached to a resource
    """
    _value: str
    _iri: Optional[str]
    _permissions: Optional[Permissions]
    _upermission: Optional[PermissionValue]
    _ark_url: Optional[str]
    _vark_url: Optional[str]

    def __init__(self,
                 value: str,
                 iri: Optional[str] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        self._value = value
        self._iri = iri
        self._permissions = permissions
        self._upermission = upermission
        self._ark_url = ark_url
        self._vark_url = vark_url

    @property
    def value(self) -> str:
        return self._value

    @property
    def iri(self) -> str:
        return self._iri

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

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = {}
        if action == Actions.Create:
            tmp["knora-api:fileValueHasFilename"] = self._value
            if self._permissions:
                tmp["knora-api:hasPermissions"] = self.permissions.toJsonLdObj()
        return tmp
