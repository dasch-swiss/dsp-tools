from typing import Optional, Union, cast

from lxml import etree

from dsp_tools.models.value import KnoraStandoffXml


class XMLValue:
    """Represents a value of a resource property in the XML used for data import"""

    _value: Union[str, KnoraStandoffXml]
    _resrefs: Optional[list[str]]
    _comment: Optional[str]
    _permissions: Optional[str]

    def __init__(
        self, 
        node: etree._Element, 
        val_type: str, 
        listname: Optional[str] = None,
    ) -> None:
        self._resrefs = None
        self._comment = node.get("comment")
        self._permissions = node.get("permissions")
        if node.tag == "text":
            node.attrib.clear()
            xmlstr = etree.tostring(node, encoding="unicode", method="xml")
            xmlstr = xmlstr.replace('<text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', "")
            xmlstr = xmlstr.replace("</text>", "")
            self._value = KnoraStandoffXml(xmlstr)
            self._resrefs = list({x.split(":")[1] for x in self._value.get_all_iris() or []})
        elif val_type == "list":
            listname = cast(str, listname)
            self._value = listname + ":" + "".join(node.itertext())
        else:
            self._value = "".join(node.itertext())

    @property
    def value(self) -> Union[str, KnoraStandoffXml]:
        """The actual value of the value instance"""
        return self._value

    @value.setter
    def value(self, value: Union[str, KnoraStandoffXml]) -> None:
        self._value = value

    @property
    def resrefs(self) -> Optional[list[str]]:
        """List of resource references"""
        return self._resrefs

    @resrefs.setter
    def resrefs(self, resrefs: Optional[list[str]]) -> None:
        self._resrefs = resrefs

    @property
    def comment(self) -> Optional[str]:
        """Comment about the value"""
        return self._comment

    @property
    def permissions(self) -> Optional[str]:
        """Reference to the set of permissions for the value"""
        return self._permissions
