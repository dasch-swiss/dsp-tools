from enum import Enum

from lxml import etree

from dsp_tools.xmllib.internal.constants import DASCH_SCHEMA
from dsp_tools.xmllib.internal.constants import XML_NAMESPACE_MAP


class PermissionTypes(Enum):
    RV = "RV"
    V = "V"
    D = "D"
    CR = "CR"


PUBLIC = {
    "UnknownUser": PermissionTypes.V,
    "KnownUser": PermissionTypes.V,
    "ProjectMember": PermissionTypes.D,
    "ProjectAdmin": PermissionTypes.CR,
}

PRIVATE = {
    "ProjectMember": PermissionTypes.D,
    "ProjectAdmin": PermissionTypes.CR,
}

LIMITED_VIEW = {
    "UnknownUser": PermissionTypes.RV,
    "KnownUser": PermissionTypes.RV,
    "ProjectMember": PermissionTypes.D,
    "ProjectAdmin": PermissionTypes.CR,
}


class XMLPermissions:
    def serialise(self) -> list[etree._Element]:
        return [self._serialise_open(), self._serialise_restricted(), self._serialise_restricted_view()]

    def _serialise_open(self) -> etree._Element:
        return self._serialise_one_permission_element("open", PUBLIC)

    def _serialise_restricted(self) -> etree._Element:
        return self._serialise_one_permission_element("restricted", PRIVATE)

    def _serialise_restricted_view(self) -> etree._Element:
        return self._serialise_one_permission_element("restricted-view", LIMITED_VIEW)

    def _serialise_one_permission_element(
        self, permission_name: str, groups: dict[str, PermissionTypes]
    ) -> etree._Element:
        ele = etree.Element(f"{DASCH_SCHEMA}permissions", attrib={"id": permission_name}, nsmap=XML_NAMESPACE_MAP)
        allows = [self._serialise_one_allow(g, name) for g, name in groups.items()]
        ele.extend(allows)
        return ele

    def _serialise_one_allow(self, group: str, tag_text: PermissionTypes) -> etree._Element:
        ele = etree.Element(f"{DASCH_SCHEMA}allow", attrib={"group": group}, nsmap=XML_NAMESPACE_MAP)
        ele.text = tag_text.value
        return ele
