from enum import Enum, unique
from typing import List, Set, Dict, Tuple, Optional, Any, Union, Type
from pystrict import strict
import re

from dsplib.models.group import Group
from dsplib.models.helpers import BaseError


@unique
class PermissionValue(Enum):
    RV = 1
    V = 2
    M = 4
    D = 8
    CR = 16

    def __str__(self):
        tmp = {
            1: 'RV',
            2: 'V',
            4: 'M',
            8: 'D',
            16: 'CR'
        }
        return tmp[self.value]


@strict
class PermissionsIterator:
    _permissions: 'Permissions'
    _group: List[str]
    _index: int

    def __init__(self, permissions: 'Permissions'):
        self._permissions = permissions
        self._index = 0

    def __next__(self):
        if len(self._permissions.permissions) == 0 and self._index == 0:
            return None, None
        elif self._index < len(self._permissions.permissions):
            tmp = self._prefixes[self._index]
            self._index += 1
            return tmp, self._permissions.permissions[tmp]
        else:
            raise StopIteration


@strict
class Permissions:
    _permissions: Union[Dict[PermissionValue, List[str]], None]

    def __init__(self,
                 permissions: Optional[Dict[PermissionValue, List[str]]] = None):
        if permissions is None:
            self._permissions = {}
        else:
            self._permissions = permissions

    def __getitem__(self, key: PermissionValue) -> Union[List[str], None]:
        return self._permissions.get(key)

    def __setitem__(self, key: PermissionValue, value: List[str]) -> None:
        self._permissions[key] = value

    def __delitem__(self, key: PermissionValue) -> None:
        del self._permissions[key]

    def __missing__(self, key: PermissionValue) -> None:
        return None

    def __iter__(self) -> PermissionsIterator:
        return PermissionsIterator(self)

    def __contains__(self, key: PermissionValue) -> bool:
        return key in self._permissions

    def __str__(self):
        tmpstr = ''
        for permission, groups in self._permissions.items():
            if tmpstr:
                tmpstr += '|'
            tmpstr += str(permission) + ' ' + ",".join(groups)
        return tmpstr

    def add(self, key: PermissionValue, val: str):
        if self._permissions.get(key) is None:
            self._permissions[key] = [val]
        else:
            self._permissions[key].append(val)

    def toJsonLdObj(self):
        tmpstr = ''
        for permission, groups in self._permissions.items():
            if tmpstr:
                tmpstr += '|'
            tmpstr += str(permission) + ' ' + ",".join(groups)
        return tmpstr

    @classmethod
    def fromString(cls, permstr: str):
        tmpstr = permstr.split('|')
        permissions: Dict[PermissionValue, List[str]] = {}
        for s in tmpstr:
            key, *vals = re.split("[\\s,]+", s)
            permissions[PermissionValue[key]] = vals
        return cls(permissions)

    @property
    def permissions(self) -> Union[Dict[PermissionValue, List[str]], None]:
        return self._permissions
