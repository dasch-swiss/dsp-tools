from lxml import etree


class XMLBitstream:
    """Represents a bitstream object (file) of a resource in the XML used for data import"""

    _value: str
    _permissions: str

    def __init__(self, node: etree.Element) -> None:
        self._value = node.text
        self._permissions = node.get("permissions")

    @property
    def value(self) -> str:
        """The file path of the bitstream object"""
        return self._value

    @property
    def permissions(self) -> str:
        """Reference to the set of permissions for the bitstream object"""
        return self._permissions
