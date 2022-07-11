from typing import Union, Optional

from lxml import etree

from knora.dsplib.models.value import KnoraStandoffXml


class XMLValue:
    """Represents a value of a resource property in the XML used for data import"""

    _value: Union[str, KnoraStandoffXml]
    _resrefs: Optional[list[str]]
    _comment: str
    _permissions: str
    _is_richtext: bool

    def __init__(self, node: etree.Element, val_type: str, listname: Optional[str] = None) -> None:

        self._resrefs = None
        self._comment = node.get('comment')
        self._permissions = node.get('permissions')
        if node.get('encoding') == 'xml':
            node.attrib.clear()
            xmlstr = etree.tostring(node, encoding="unicode", method="xml")
            xmlstr = xmlstr.replace('<text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', '')
            xmlstr = xmlstr.replace('</text>', '')
            self._value = KnoraStandoffXml(xmlstr)
            tmp_id_list = self._value.get_all_iris()
            if tmp_id_list:
                refs = set()
                for tmp_id in tmp_id_list:
                    refs.add(tmp_id.split(':')[1])
                self._resrefs = list(refs)
        else:
            if val_type == 'list':
                self._value = listname + ':' + "".join(node.itertext())
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
    def comment(self) -> str:
        """Comment about the value"""
        return self._comment

    @property
    def permissions(self) -> str:
        """Reference to the set of permissions for the value"""
        return self._permissions

    @property
    def is_richtext(self) -> bool:
        """true if text value is of type richtext, false otherwise"""
        return self._is_richtext

    def print(self) -> None:
        """Prints the value and its attributes."""
        print('   Value: ' + str(self._value))
        if self._comment:
            print('   Comment:' + self._comment)
        if self._resrefs is not None:
            for i in self._resrefs:
                print('   res_ref: ' + i)
