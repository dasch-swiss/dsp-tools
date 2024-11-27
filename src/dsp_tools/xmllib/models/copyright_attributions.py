from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from lxml import etree

from dsp_tools.xmllib.constants import DASCH_SCHEMA
from dsp_tools.xmllib.constants import XML_NAMESPACE_MAP


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
