from typing import Any, Optional

from dsp_tools.models.helpers import Actions
from dsp_tools.models.permission import Permissions


class Bitstream:
    """
    Represents a bitstream object (file) which is attached to a resource
    """

    _value: str
    _permissions: Optional[Permissions]

    def __init__(self, value: str, permissions: Optional[Permissions] = None):
        self._value = value
        self._permissions = permissions

    @property
    def value(self) -> str:
        """File path of the bitstream"""
        return self._value

    @property
    def permissions(self) -> Optional[Permissions]:
        """Permissions of the bitstream"""
        return self._permissions

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:  # pylint: disable=missing-function-docstring
        tmp = {}
        if action == Actions.Create:
            tmp["knora-api:fileValueHasFilename"] = self._value
            if self._permissions:
                tmp["knora-api:hasPermissions"] = self.permissions.toJsonLdObj()
        return tmp
