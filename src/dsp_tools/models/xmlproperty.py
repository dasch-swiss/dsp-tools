from lxml import etree

from dsp_tools.models.exceptions import XmlError
from dsp_tools.models.xmlvalue import XMLValue


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

    def __init__(self, node: etree._Element, valtype: str, default_ontology: str):
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
                self.name = node.attrib["name"]
            else:
                # replace an empty namespace with the default ontology name
                self.name = default_ontology + ":" + tmp_prop_name[1]
        else:
            self.name = "knora-api:" + tmp_prop_name[0]
        listname = node.attrib.get("list")  # safe the list name if given (only for lists)
        self.valtype = valtype
        self.values = []

        # parse the subnodes of the property nodes which contain the actual values of the property
        for subnode in node:
            if subnode.tag == valtype:  # the subnode must correspond to the expected value type
                self.values.append(XMLValue(subnode, valtype, listname))
            else:
                raise XmlError(f"ERROR Unexpected tag: '{subnode.tag}'. Property may contain only value tags!")
