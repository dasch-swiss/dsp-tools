from __future__ import annotations

from dataclasses import dataclass

from lxml import etree


@dataclass
class ProjectXML:
    shortcode: str
    default_onto: str
    permissions: list[PermissionsXML]
    xml_data: list[ResourceXML]


@dataclass
class ResourceXML:
    res_id: str
    res_attrib: dict[str, str]
    values: list[etree._Element]


@dataclass
class PermissionsXML:
    permission_id: str
    permission_eles: list[etree._Element]
