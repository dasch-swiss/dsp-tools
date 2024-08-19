from pathlib import Path

from lxml import etree

from dsp_tools.commands.xml_validate.models.deserialised import AbstractFileValue
from dsp_tools.commands.xml_validate.models.deserialised import BooleanDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ExternalFileValueDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import FileValueDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ListDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import PermissionsDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ResourceDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import RichtextDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import SimpleTextDeserialised
from dsp_tools.commands.xml_validate.models.deserialised import ValueDeserialised
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
    return ProjectXML(
        shortcode=shortcode, default_onto=default_ontology, permissions=permissions, xml_resources=resources
    )


def _get_resources(ele: etree._Element) -> ResourceXML:
    values = list(ele.iterchildren())
    return ResourceXML(res_attrib=ele.attrib, values=values, file_value=_find_file_value(ele))


def _find_file_value(ele: etree._Element) -> etree._Element | None:
    if bitstream := ele.find(".//bitstream") is not None:
        return bitstream
    return ele.find(".//iiif-uri")


def _get_permissions(permission_ele: etree._Element) -> PermissionsXML:
    per_id = permission_ele.attrib["id"]
    permissions = list(permission_ele.iterchildren())
    return PermissionsXML(permission_id=per_id, permission_eles=permissions)


def deserialise_xml_project(project: ProjectXML) -> ProjectDeserialised:
    permissions = [_deserialise_one_permission(x) for x in project.permissions]
    resources = [_deserialise_one_resource(x) for x in project.xml_resources]
    return ProjectDeserialised(
        shortcode=project.shortcode, default_onto=project.default_onto, permissions=permissions, resources=resources
    )


def _deserialise_one_permission(permission: PermissionsXML) -> PermissionsDeserialised:
    permission_dict = {x.attrib["group"]: x.text for x in permission.permission_eles}
    return PermissionsDeserialised(permission_id=permission.permission_id, permission_dict=permission_dict)


def _deserialise_one_resource(resource: ResourceXML) -> ResourceDeserialised:
    res_id = resource.res_attrib["id"]
    values = []
    file_value = None
    for val in resource.values:
        values.extend(_deserialise_one_property(val))
    if resource.file_value:
        file_value = _deserialise_file_value(resource.file_value)
    return ResourceDeserialised(
        res_id=res_id,
        res_class=resource.res_attrib["restype"],
        label=resource.res_attrib["label"],
        permissions=resource.res_attrib.get("permissions"),
        values=values,
        file_value=file_value,
    )


def _deserialise_file_value(value_ele: etree._Element) -> AbstractFileValue:
    permission = value_ele.attrib.get("permissions")
    match value_ele.tag:
        case "bitstream":
            return FileValueDeserialised(file_path=Path(value_ele.text), permissions=permission)
        case "iiif-uri":
            return ExternalFileValueDeserialised(iiif_uri=value_ele.text, permissions=permission)


def _deserialise_one_property(prop_ele: etree._Element) -> list[ValueDeserialised]:
    match prop_ele.tag:
        case "text-prop":
            return _deserialise_text_prop(prop_ele)
        case "list-prop":
            return _deserialise_list_prop(prop_ele)
        case "boolean-prop":
            return _deserialise_bool_prop(prop_ele)
        case "bitstream" | "iiif-uri":
            return []


def _deserialise_text_prop(prop: etree._Element) -> list[ValueDeserialised]:
    prop_name = prop.attrib["name"]
    all_vals: list[ValueDeserialised] = []
    for child in prop.iterchildren():
        permissions = child.attrib.get("permissions")
        comments = child.attrib.get("comments")
        match child.attrib["encoding"]:
            case "utf8":
                all_vals.append(
                    SimpleTextDeserialised(
                        prop_name=prop_name, prop_value=child.text, permissions=permissions, comments=comments
                    )
                )
            case "xml":
                all_vals.append(
                    RichtextDeserialised(
                        prop_name=prop_name, prop_value=child.text, permissions=permissions, comments=comments
                    )
                )
    return all_vals


def _deserialise_list_prop(prop: etree._Element) -> list[ValueDeserialised]:
    prop_name = prop.attrib["name"]
    list_name = prop.attrib["list"]
    all_vals: list[ValueDeserialised] = []
    for val in prop.iterchildren():
        all_vals.append(
            ListDeserialised(
                prop_name=prop_name,
                prop_value=val.text,
                list_name=list_name,
                permissions=val.attrib.get("permissions"),
                comments=val.attrib.get("comments"),
            )
        )
    return all_vals


def _deserialise_bool_prop(prop: etree._Element) -> list[ValueDeserialised]:
    val = next(prop.iterchildren())
    return [
        BooleanDeserialised(
            prop_name=prop.attrib["name"],
            prop_value=val.text,
            permissions=val.attrib.get("permissions"),
            comments=val.attrib.get("comments"),
        )
    ]
