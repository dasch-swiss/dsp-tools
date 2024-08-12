from __future__ import annotations

from lxml import etree

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.models.exceptions import XmlUploadError
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
        self._allows.extend(XmlAllow(allow_node, project_context) for allow_node in node)

    def get_permission_instance(self) -> Permissions:
        """Returns a list of allow elements of this permission instance"""
        permissions = Permissions()
        for allow in self._allows:
            permissions.add(allow.permission, allow.group)
        return permissions

    def __str__(self) -> str:
        allow_str: list[str] = [f"{allow.permission} {allow.group}" for allow in self._allows]
        return "|".join(allow_str)


class XmlAllow:
    """Represents the allow element of the XML used for data import"""

    _group: str
    _permission: PermissionValue

    def __init__(self, node: etree._Element, project_context: ProjectContext) -> None:
        """
        Constructor which parses the XML DOM allow element

        Args:
            node: The DOM node to be processed (represents a single right in a permission set)
            project_context: Context for DOM node traversal

        Raises:
            XmlUploadError: If an upload fails
        """
        tmp = node.attrib["group"].split(":")

        sysgroups = ["UnknownUser", "KnownUser", "ProjectMember", "Creator", "ProjectAdmin", "SystemAdmin"]
        if len(tmp) > 1:
            if tmp[0]:
                if tmp[0] == "knora-admin" and tmp[1] in sysgroups:
                    self._group = node.attrib["group"]
                else:
                    _group = project_context.group_map.get(node.attrib["group"])
                    if _group is None:
                        raise XmlUploadError(f'Group "{node.attrib["group"]}" is not known: Cannot find project!')
                    self._group = _group
            elif project_context.project_name is None:
                raise XmlUploadError("Project shortname has not been set in ProjectContext")
            else:
                prefixed_custom_groupname = f"{project_context.project_name}:{tmp[1]}"
                if _group := project_context.group_map.get(prefixed_custom_groupname):
                    self._group = _group
        elif tmp[0] in sysgroups:
            self._group = "knora-admin:" + node.attrib["group"]
        else:
            raise XmlUploadError(f'Group "{node.attrib["group"]}" is not known: ')

        if not node.text:
            raise XmlUploadError("No permission set specified")
        self._permission = PermissionValue[node.text]

    @property
    def group(self) -> str:
        """The group specified in the allow element"""
        return self._group

    @property
    def permission(self) -> PermissionValue:
        """The reference to a set of permissions"""
        return self._permission
