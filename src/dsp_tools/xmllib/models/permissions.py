from enum import Enum

from lxml import etree

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


class PermissionTypes(Enum):
    RV = "RV"
    V = "V"
    D = "D"
    CR = "CR"


class XMLPermissions:
    def serialise(self) -> list[etree._Element]:
        return [self._serialise_open(), self._serialise_restricted(), self._serialise_restricted_view()]

    def _serialise_open(self) -> etree._Element:
        permissions = {
            "UnknownUser": PermissionTypes.V,
            "KnownUser": PermissionTypes.V,
            "ProjectMember": PermissionTypes.D,
            "ProjectAdmin": PermissionTypes.CR,
        }
        return self._serialise_one_permission_element("open", permissions)

    def _serialise_restricted(self) -> etree._Element:
        permissions = {
            "ProjectMember": PermissionTypes.D,
            "ProjectAdmin": PermissionTypes.CR,
        }
        return self._serialise_one_permission_element("restricted", permissions)

    def _serialise_restricted_view(self) -> etree._Element:
        permissions = {
            "UnknownUser": PermissionTypes.RV,
            "KnownUser": PermissionTypes.RV,
            "ProjectMember": PermissionTypes.D,
            "ProjectAdmin": PermissionTypes.CR,
        }
        return self._serialise_one_permission_element("restricted-view", permissions)

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
