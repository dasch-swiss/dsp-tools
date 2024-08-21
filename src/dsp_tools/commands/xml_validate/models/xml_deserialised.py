from __future__ import annotations

from dataclasses import dataclass

from lxml import etree


@dataclass
class ProjectXML:
    shortcode: str
    default_onto: str
    xml_resources: list[ResourceXML]


@dataclass
class ResourceXML:
    res_attrib: dict[str, str]
    values: list[etree._Element]
