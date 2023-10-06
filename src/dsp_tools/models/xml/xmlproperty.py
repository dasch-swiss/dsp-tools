from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from dsp_tools.models.exceptions import XmlError
from dsp_tools.models.xml.xmlvalue import XMLValue


@dataclass
class XMLProperty:  # pylint: disable=too-few-public-methods
    """
    Represents a property of a resource in the XML used for data import.

    Attributes:
        name: The name of the property
        valtype: The type of the property
        values: The list of values of the property
    """

    name: str
    valtype: str
    values: list[XMLValue]

    @staticmethod
    def fromXml(node: etree._Element, valtype: str, default_ontology: str) -> XMLProperty:
        """
        The constructor for the DSP property

        Args:
            node: the property node, p.ex. <decimal-prop></decimal-prop>
            valtype: the type of value given by the name of the property node, p.ex. decimal in <decimal-prop>
            default_ontology: the name of the ontology
        """
        # get the property name which is in format namespace:propertyname, p.ex. rosetta:hasName
        tmp_prop_name = node.attrib["name"].split(":")
        if len(tmp_prop_name) > 1:
            if tmp_prop_name[0]:
                name = node.attrib["name"]
            else:
                # replace an empty namespace with the default ontology name
                name = default_ontology + ":" + tmp_prop_name[1]
        else:
            name = "knora-api:" + tmp_prop_name[0]
        listname = node.attrib.get("list")  # safe the list name if given (only for lists)
        values = []

        # parse the subnodes of the property nodes which contain the actual values of the property
        for subnode in node:
            if subnode.tag == valtype:  # the subnode must correspond to the expected value type
                values.append(XMLValue.fromXml(subnode, valtype, listname))
            else:
                raise XmlError(f"ERROR Unexpected tag: '{subnode.tag}'. Property may contain only value tags!")
        return XMLProperty(name, valtype, values)
