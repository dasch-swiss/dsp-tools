from pathlib import Path

from lxml import etree

from dsp_tools.commands.xml_validate.models.xml_deserialised import PermissionsXML
from dsp_tools.commands.xml_validate.models.xml_deserialised import ProjectXML
from dsp_tools.commands.xml_validate.models.xml_deserialised import ResourceXML
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file
from dsp_tools.utils.xml_validation import validate_xml


def parse_file(file: Path) -> ProjectXML:
    root = _parse_file_validate_with_schema(file)
    return _transform_into_xml_deserialised(root)


def _parse_file_validate_with_schema(file: Path) -> etree._Element:
    root = parse_and_clean_xml_file(file)
    validate_xml(root)
    return root


def _transform_into_xml_deserialised(root: etree._Element) -> ProjectXML:
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    permissions = [_get_permissions(x) for x in root.iterdescendants(tag="permissions")]
    resources = [_get_resources(x) for x in root.iterdescendants(tag="resource")]
    return ProjectXML(shortcode=shortcode, default_onto=default_ontology, permissions=permissions, xml_data=resources)


def _get_resources(ele: etree._Element) -> ResourceXML:
    res_id = ele.attrib["id"]
    values = list(ele.iterchildren())
    return ResourceXML(res_id=res_id, res_attrib=ele.attrib, values=values)


def _get_permissions(permission_ele: etree._Element) -> PermissionsXML:
    per_id = permission_ele.attrib["id"]
    permissions = list(permission_ele.iterchildren())
    return PermissionsXML(permission_id=per_id, permission_eles=permissions)
