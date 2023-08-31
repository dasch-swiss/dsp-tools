from typing import Optional, cast

from lxml import etree


class XMLBitstream:  # pylint: disable=too-few-public-methods
    """
    Represents a bitstream object (file) of a resource in the XML used for data import

    Attributes:
        value: The file path of the bitstream object
        permissions: Reference to the set of permissions for the bitstream object
    """

    value: str
    permissions: Optional[str]

    def __init__(self, node: etree._Element) -> None:
        self.value = cast(str, node.text)
        self.permissions = node.get("permissions")
