from lxml import etree

from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.models.exceptions import XmlError
from dsp_tools.models.projectContext import ProjectContext


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

        Returns:
            None
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
                        raise XmlError(f'Group "{node.attrib["group"]}" is not known: Cannot find project!')
                    self._group = _group
            else:
                if project_context.project_name is None:
                    raise XmlError("Project shortcode has not been set in ProjectContext")
                self._group = project_context.project_name + ":" + tmp[1]
        else:
            if tmp[0] in sysgroups:
                self._group = "knora-admin:" + node.attrib["group"]
            else:
                raise XmlError(f'Group "{node.attrib["group"]}" is not known: ')
        if not node.text:
            raise XmlError("No permission set specified")
        self._permission = PermissionValue[node.text]

    @property
    def group(self) -> str:
        """The group specified in the allow element"""
        return self._group

    @property
    def permission(self) -> PermissionValue:
        """The reference to a set of permissions"""
        return self._permission
