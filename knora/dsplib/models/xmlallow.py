from lxml import etree

from knora.dsplib.models.projectContext import ProjectContext
from knora.dsplib.models.xmlerror import XmlError


class XmlAllow:
    """Represents the allow element of the XML used for data import"""

    _group: str
    _permission: str

    def __init__(self, node: etree.Element, project_context: ProjectContext) -> None:
        """
        Constructor which parses the XML DOM allow element

        Args:
            node: The DOM node to be processed (represents a single right in a permission set)
            project_context: Context for DOM node traversal

        Returns:
            None
        """
        tmp = node.attrib['group'].split(':')
        sysgroups = ['UnknownUser', 'KnownUser', 'ProjectMember', 'Creator', 'ProjectAdmin', 'SystemAdmin']
        if len(tmp) > 1:
            if tmp[0]:
                if tmp[0] == 'knora-admin' and tmp[1] in sysgroups:
                    self._group = node.attrib['group']
                else:
                    self._group = project_context.group_map.get(node.attrib['group'])
                    if self._group is None:
                        raise XmlError("Group \"{}\" is not known: Cannot find project!".format(node.attrib['group']))
            else:
                if project_context.project_name is None:
                    raise XmlError("Project shortcode has not been set in ProjectContext")
                self._group = project_context.project_name + ':' + tmp[1]
        else:
            if tmp[0] in sysgroups:
                self._group = 'knora-admin:' + node.attrib['group']
            else:
                raise XmlError("Group \"{}\" is not known: ".format(node.attrib['group']))
        self._permission = node.text

    @property
    def group(self) -> str:
        """The group specified in the allow element"""
        return self._group

    @property
    def permission(self) -> str:
        """The reference to a set of permissions"""
        return self._permission

    def print(self) -> None:
        """Prints the attributes of the XmlAllow instance"""
        print("  group=", self._group, " permission=", self._permission)
