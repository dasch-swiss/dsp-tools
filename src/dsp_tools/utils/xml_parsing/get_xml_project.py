from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from lxml import etree

from dsp_tools.commands.validate_data.constants import KNORA_API_STR
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_parsing.models.data_deserialised import XMLProject
from dsp_tools.utils.xml_parsing.parse_xml import parse_xml_file
from dsp_tools.utils.xml_parsing.transform import remove_comments_from_element_tree
from dsp_tools.utils.xml_parsing.transform import transform_special_tags_make_localname
from dsp_tools.utils.xml_parsing.xml_schema_validation import validate_xml_with_schema


def get_xml_project(file: Path, api_url: str) -> XMLProject:
    """
    Parses, cleans and does some basic transformation of the file and creates the XMLProject.

    Args:
        file: file path
        api_url: API URL to resolve prefixes into namespaces

    Returns:
        Project Information and cleaned root
    """
    root = parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml_with_schema(root)
    root = transform_special_tags_make_localname(root)
    return _replace_namespaces(root, api_url)


def _replace_namespaces(root: etree._Element, api_url: str) -> XMLProject:
    new_root = deepcopy(root)
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    namespace_lookup = _make_namespace_lookup(api_url, shortcode, default_ontology)
    for ele in new_root.iterdescendants():
        if (found := ele.attrib.get("restype")) or (found := ele.attrib.get("name")):
            split_found = found.split(":")
            if len(split_found) == 1:
                ele.set("restype" if "restype" in ele.attrib else "name", f"{KNORA_API_STR}{found}")
            elif len(split_found) == 2:
                if len(split_found[0]) == 0:
                    found_namespace = namespace_lookup[default_ontology]
                elif not (namespace := namespace_lookup.get(split_found[0])):
                    found_namespace = _construct_namespace(api_url, shortcode, split_found[0])
                    namespace_lookup[split_found[0]] = found_namespace
                else:
                    found_namespace = namespace
                ele.set("restype" if "restype" in ele.attrib else "name", f"{found_namespace}{split_found[1]}")
            else:
                raise InputError(
                    f"It is not permissible to have a colon in a property or resource class name. "
                    f"Please correct the following: {found}"
                )
    return XMLProject(
        shortcode=shortcode,
        root=new_root,
        used_ontologies=set(namespace_lookup.values()),
    )


def _make_namespace_lookup(api_url: str, shortcode: str, default_onto: str) -> dict[str, str]:
    return {default_onto: _construct_namespace(api_url, shortcode, default_onto), "knora-api": KNORA_API_STR}


def _construct_namespace(api_url: str, shortcode: str, onto_name: str) -> str:
    return f"{api_url}/ontology/{shortcode}/{onto_name}/v2#"
