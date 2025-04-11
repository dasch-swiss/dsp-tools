from __future__ import annotations

from enum import StrEnum
from enum import unique
from typing import Optional


@unique
class PermissionValue(StrEnum):
    RV = "RV"
    V = "V"
    M = "M"
    D = "D"
    CR = "CR"


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
