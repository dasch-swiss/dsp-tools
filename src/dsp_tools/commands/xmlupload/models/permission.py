from __future__ import annotations

from enum import Enum
from enum import unique
from typing import Optional
from typing import Union

import regex


@unique
class PermissionValue(Enum):
    RV = 1
    V = 2
    M = 4
    D = 8
    CR = 16

    def __str__(self) -> str:
        tmp = {
            1: "RV",
            2: "V",
            4: "M",
            8: "D",
            16: "CR",
        }
        return tmp[self.value]


class Permissions:
    _permissions: dict[PermissionValue, list[str]]

    def __init__(self, permissions: Optional[dict[PermissionValue, list[str]]] = None):
        if permissions is None:
            self._permissions = {}
        else:
            self._permissions = permissions

    def __getitem__(self, key: PermissionValue) -> Union[list[str], None]:
        return self._permissions.get(key)

    def __setitem__(self, key: PermissionValue, value: list[str]) -> None:
        self._permissions[key] = value

    def __delitem__(self, key: PermissionValue) -> None:
        del self._permissions[key]

    def __missing__(self, key: PermissionValue) -> None:
        return None

    def __contains__(self, key: PermissionValue) -> bool:
        return key in self._permissions

    def __str__(self) -> str:
        tmpstr = ""
        for permission, groups in self._permissions.items():
            if tmpstr:
                tmpstr += "|"
            tmpstr += str(permission) + " " + ",".join(groups)
        return tmpstr

    def add(self, key: PermissionValue, val: str) -> None:
        if self._permissions.get(key) is None:
            self._permissions[key] = [val]
        else:
            self._permissions[key].append(val)

    def toJsonLdObj(self) -> str:
        tmpstr = ""
        for permission, groups in self._permissions.items():
            if tmpstr:
                tmpstr += "|"
            tmpstr += str(permission) + " " + ",".join(groups)
        return tmpstr

    @classmethod
    def fromString(cls, permstr: str) -> Permissions:
        tmpstr = permstr.split("|")
        permissions: dict[PermissionValue, list[str]] = {}
        for s in tmpstr:
            key, *vals = regex.split("[\\s,]+", s)
            permissions[PermissionValue[key]] = vals
        return cls(permissions)

    @property
    def permissions(self) -> Union[dict[PermissionValue, list[str]], None]:
        return self._permissions
