from typing import Optional

from lxml import etree

from knora.dsplib.models.xmlvalue import XMLValue
from knora.dsplib.models.xmlerror import XmlError


class XMLProperty:
    """Represents a property of a resource in the XML used for data import"""

    _name: str
    _valtype: str
    _values: list[XMLValue]

    def __init__(self, node: etree.Element, valtype: str, default_ontology: Optional[str] = None):
        """
        The constructor for the DSP property

        Args:
            node: the property node, p.ex. <decimal-prop></decimal-prop>
            valtype: the type of value given by the name of the property node, p.ex. decimal in <decimal-prop>
            default_ontology: the name of the ontology
        """
        # get the property name which is in format namespace:propertyname, p.ex. rosetta:hasName
        tmp_prop_name = node.attrib['name'].split(':')
        if len(tmp_prop_name) > 1:
            if tmp_prop_name[0]:
                self._name = node.attrib['name']
            else:
                # replace an empty namespace with the default ontology name
                self._name = default_ontology + ':' + tmp_prop_name[1]
        else:
            self._name = 'knora-api:' + tmp_prop_name[0]
        listname = node.attrib.get('list')  # safe the list name if given (only for lists)
        self._valtype = valtype
        self._values = []

        # parse the subnodes of the property nodes which contain the actual values of the property
        for subnode in node:
            if subnode.tag == valtype:  # the subnode must correspond to the expected value type
                self._values.append(XMLValue(subnode, valtype, listname))
            else:
                raise XmlError(f"ERROR Unexpected tag: '{subnode.tag}'. Property may contain only value tags!")

    @property
    def name(self) -> str:
        """The name of the property"""
        return self._name

    @property
    def valtype(self) -> str:
        """The value type of the property"""
        return self._valtype

    @property
    def values(self) -> list[XMLValue]:
        """List of values of this property"""
        return self._values

    def print(self) -> None:
        """Prints the property."""
        print('  Property: {} Type: {}'.format(self._name, self._valtype))
        for value in self._values:
            value.print()
