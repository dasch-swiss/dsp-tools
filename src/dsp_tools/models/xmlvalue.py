from typing import Optional, Union, cast

from lxml import etree
import regex

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
        if val_type == "formatted-text":  # "unformatted-text" is handled by the else branch
            node.attrib.clear()
            xmlstr = etree.tostring(node, encoding="unicode", method="xml")
            xmlstr = regex.sub("<text.*?>", "", xmlstr)
            xmlstr = regex.sub("</text>", "", xmlstr)
            xmlstr = regex.sub("\n", " ", xmlstr)
            xmlstr = regex.sub(" +", " ", xmlstr)
            xmlstr = xmlstr.strip()
            self.value = KnoraStandoffXml(xmlstr)
            self.resrefs = list({x.split(":")[1] for x in self.value.get_all_iris() or []})
        elif val_type == "list":
            listname = cast(str, listname)
            self.value = listname + ":" + "".join(node.itertext())
        else:
            self.value = "".join(node.itertext())
