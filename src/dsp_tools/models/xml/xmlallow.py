from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from dsp_tools.models.exceptions import XmlError
from dsp_tools.models.permission import PermissionValue
from dsp_tools.models.projectContext import ProjectContext


@dataclass
class XmlAllow:
    """Represents the allow element of the XML used for data import"""

    group: str
    permission: PermissionValue

    @staticmethod
    def fromXml(node: etree._Element, project_context: ProjectContext) -> XmlAllow:
        """
        Factory method which parses the XML DOM allow element

        Args:
            node: The DOM node to be processed (represents a single right in a permission set)
            project_context: Context for DOM node traversal

        Returns:
            An instance of XmlAllow
        """
        tmp = node.attrib["group"].split(":")
        sysgroups = ["UnknownUser", "KnownUser", "ProjectMember", "Creator", "ProjectAdmin", "SystemAdmin"]
        if len(tmp) > 1:
            if tmp[0]:
                if tmp[0] == "knora-admin" and tmp[1] in sysgroups:
                    group = node.attrib["group"]
                else:
                    _group = project_context.group_map.get(node.attrib["group"])
                    if _group is None:
                        raise XmlError(f'Group "{node.attrib["group"]}" is not known: Cannot find project!')
                    group = _group
            else:
                if project_context.project_name is None:
                    raise XmlError("Project shortcode has not been set in ProjectContext")
                group = project_context.project_name + ":" + tmp[1]
        else:
            if tmp[0] in sysgroups:
                group = "knora-admin:" + node.attrib["group"]
            else:
                raise XmlError(f'Group "{node.attrib["group"]}" is not known: ')
        if not node.text:
            raise XmlError("No permission set specified")
        permission = PermissionValue[node.text]
        return XmlAllow(group, permission)
