from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from dsp_tools.models.permission import Permissions
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.models.xml.xmlallow import XmlAllow


@dataclass
class XmlPermission:
    """Represents the permission set containing several XmlAllow elements in the XML used for data import"""

    id_: str
    allows: list[XmlAllow]

    @staticmethod
    def fromXml(node: etree._Element, project_context: ProjectContext) -> XmlPermission:
        """
        Factory method which parses a XML DOM permissions element representing an named permission set

        Args:
            node: The DOM node to be processed (representing an a permission set)
            project_context: Context for DOM node traversal
        """
        allows = []
        id_ = node.attrib["id"]
        for allow_node in node:
            allows.append(XmlAllow.fromXml(allow_node, project_context))
        return XmlPermission(id_, allows)

    def get_permission_instance(self) -> Permissions:
        """Returns a list of allow elements of this permission instance"""
        permissions = Permissions()
        for allow in self.allows:
            permissions.add(allow.permission, allow.group)
        return permissions

    def __str__(self) -> str:
        allow_str: list[str] = []
        for allow in self.allows:
            allow_str.append(f"{allow.permission} {allow.group}")
        return "|".join(allow_str)
