from dataclasses import dataclass
from typing import Optional

from dsp_tools.models.helpers import Actions
from dsp_tools.models.permission import Permissions


@dataclass(frozen=True)
class Bitstream:
    """
    Represents a bitstream object (file) which is attached to a resource.

    Attributes:
        value: File path of the bitstream
        permissions: Permissions of the bitstream
    """

    value: str
    permissions: Optional[Permissions] = None

    def toJsonLdObj(self, action: Actions) -> dict[str, str]:
        """
        Create a JSON-LD object from this python object.

        Args:
            action: action for which this JSON-LD is used for: create, read, update, or delete

        Returns:
            JSON-LD object
        """
        tmp = {}
        if action == Actions.Create:
            tmp["knora-api:fileValueHasFilename"] = self.value
            if self.permissions:
                tmp["knora-api:hasPermissions"] = self.permissions.toJsonLdObj()
        return tmp
