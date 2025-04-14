from __future__ import annotations

from enum import Enum
from enum import unique
from typing import Optional


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
        self._permissions = permissions or {}

    def __str__(self) -> str:
        tmpstr = ""
        for permission, groups in self._permissions.items():
            if tmpstr:
                tmpstr += "|"
            tmpstr += f"{permission!s} " + ",".join(groups)
        return tmpstr

    def add(self, key: PermissionValue, val: str) -> None:
        if self._permissions.get(key) is None:
            self._permissions[key] = [val]
        else:
            self._permissions[key].append(val)
