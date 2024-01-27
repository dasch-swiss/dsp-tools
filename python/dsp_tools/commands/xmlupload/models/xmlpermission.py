from lxml import etree

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.xmlallow import XmlAllow
from dsp_tools.models.projectContext import ProjectContext


class XmlPermission:
    """Represents the permission set containing several XmlAllow elements in the XML used for data import"""

    permission_id: str
    _allows: list[XmlAllow]

    def __init__(self, node: etree._Element, project_context: ProjectContext) -> None:
        """
        Constructor which parses a XML DOM permissions element representing an named permission set

        Args:
            node: The DOM node to be processed (representing an a permission set)
            project_context: Context for DOM node traversal
        """
        self._allows = []
        self.permission_id = node.attrib["id"]
        for allow_node in node:
            self._allows.append(XmlAllow(allow_node, project_context))

    def get_permission_instance(self) -> Permissions:
        """Returns a list of allow elements of this permission instance"""
        permissions = Permissions()
        for allow in self._allows:
            permissions.add(allow.permission, allow.group)
        return permissions

    def __str__(self) -> str:
        allow_str: list[str] = []
        for allow in self._allows:
            allow_str.append(f"{allow.permission} {allow.group}")
        return "|".join(allow_str)
