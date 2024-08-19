from __future__ import annotations

from dataclasses import dataclass

from lxml import etree


@dataclass
class ProjectXML:
    shortcode: str
    default_onto: str
    permissions: list[PermissionsXML]
    xml_resources: list[ResourceXML]


@dataclass
class ResourceXML:
    res_attrib: dict[str, str]
    values: list[etree._Element]
    file_value: etree._Element | None


@dataclass
class PermissionsXML:
    permission_id: str
    permission_eles: list[etree._Element]
