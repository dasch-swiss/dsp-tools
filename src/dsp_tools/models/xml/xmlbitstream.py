from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, cast

from lxml import etree


@dataclass
class XMLBitstream:  # pylint: disable=too-few-public-methods
    """
    Represents a bitstream object (file) of a resource in the XML used for data import

    Attributes:
        value: The file path of the bitstream object
        permissions: Reference to the set of permissions for the bitstream object
    """

    value: str
    permissions: Optional[str]

    @staticmethod
    def fromXml(node: etree._Element) -> XMLBitstream:
        """
        Factory method which parses a XML DOM bitstream element representing a bitstream object.

        Args:
            node: The DOM node to be processed (representing a bitstream object)

        Returns:
            XMLBitstream: An instance of XMLBitstream
        """
        value = cast(str, node.text)
        permissions = node.get("permissions")
        return XMLBitstream(value, permissions)
