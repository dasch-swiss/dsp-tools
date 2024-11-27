from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from lxml import etree

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class CopyrightAttributions:
    copyright_attributions: list[CopyrightAttribution] = field(default_factory=list)

    def get_copyright_attribution_ids(self) -> set[str]:
        return {x.id_ for x in self.copyright_attributions}

    def serialise(self) -> etree._Element:
        copyrights = etree.Element(f"{DASCH_SCHEMA}copyright-attributions", nsmap=XML_NAMESPACE_MAP)
        for copy_right in self.copyright_attributions:
            attrib = {"id": copy_right.id_}
            ele = etree.Element(f"{DASCH_SCHEMA}copyright-attribution", attrib=attrib, nsmap=XML_NAMESPACE_MAP)
            ele.text = copy_right.text
            copyrights.append(ele)
        return copyrights


@dataclass
class CopyrightAttribution:
    id_: str
    text: str


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
