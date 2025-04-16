from __future__ import annotations

from typing import cast

import regex
from lxml import etree

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permissions_parsed import XmlPermission
from dsp_tools.legacy_models.projectContext import ProjectContext


def get_authorship_lookup(root: etree._Element) -> dict[str, list[str]]:
    def get_one_author(ele: etree._Element) -> str:
        # The xsd file ensures that the body of the element contains valid non-whitespace characters
        txt = cast(str, ele.text)
        txt = regex.sub(r"[\n\t]", " ", txt)
        txt = regex.sub(r" +", " ", txt)
        return txt.strip()

    authorship_lookup = {}
    for auth in root.iter(tag="authorship"):
        individual_authors = [get_one_author(child) for child in auth.iterchildren()]
        authorship_lookup[auth.attrib["id"]] = individual_authors
    return authorship_lookup


def get_permissions_lookup(root: etree._Element, proj_context: ProjectContext) -> dict[str, Permissions]:
    permission_ele = list(root.iter(tag="permissions"))
    permissions = [XmlPermission(permission, proj_context) for permission in permission_ele]
    permissions_dict = {permission.permission_id: permission for permission in permissions}
    permissions_lookup = {name: perm.get_permission_instance() for name, perm in permissions_dict.items()}
    return permissions_lookup
