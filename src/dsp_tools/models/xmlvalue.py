from typing import Optional, Union, cast

from lxml import etree

from dsp_tools.models.value import KnoraStandoffXml


class XMLValue:  # pylint: disable=too-few-public-methods
    """Represents a value of a resource property in the XML used for data import"""

    value: Union[str, KnoraStandoffXml]
    resrefs: Optional[list[str]]
    comment: Optional[str]
    permissions: Optional[str]

    def __init__(
        self,
        node: etree._Element,
        val_type: str,
        listname: Optional[str] = None,
    ) -> None:
        self.resrefs = None
        self.comment = node.get("comment")
        self.permissions = node.get("permissions")
        if val_type == "text" and node.get("encoding") == "xml":
            node.attrib.clear()
            xmlstr = etree.tostring(node, encoding="unicode", method="xml")
            xmlstr = xmlstr.replace('<text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', "")
            xmlstr = xmlstr.replace("</text>", "")
            self.value = KnoraStandoffXml(xmlstr)
            self.resrefs = list({x.split(":")[1] for x in self.value.get_all_iris() or []})
        elif val_type == "list":
            listname = cast(str, listname)
            self.value = listname + ":" + "".join(node.itertext())
        else:
            self.value = "".join(node.itertext())
