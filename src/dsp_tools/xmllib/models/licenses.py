from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from lxml import etree

from dsp_tools.xmllib.constants import DASCH_SCHEMA
from dsp_tools.xmllib.constants import XML_NAMESPACE_MAP


@dataclass
class Licenses:
    licenses: list[License] = field(default_factory=list)

    def get_license_ids(self) -> set[str]:
        return {x.id_ for x in self.licenses}

    def serialise(self) -> etree._Element:
        licenses = etree.Element(f"{DASCH_SCHEMA}licenses", nsmap=XML_NAMESPACE_MAP)
        for one_license in self.licenses:
            attrib = {"id": one_license.id_}
            if one_license.uri:
                attrib["uri"] = one_license.uri
                ele = etree.Element(f"{DASCH_SCHEMA}license", attrib=attrib, nsmap=XML_NAMESPACE_MAP)
                ele.text = one_license.text
                licenses.append(ele)
        return licenses


@dataclass
class License:
    id_: str
    text: str
    uri: str | None
