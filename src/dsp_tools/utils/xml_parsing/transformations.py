from __future__ import annotations

from copy import deepcopy

from lxml import etree

from dsp_tools.commands.validate_data.constants import KNORA_API_STR
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_parsing.models.data_deserialised import XMLProject


def transform_special_resource_tags(tree: etree._Element) -> etree._Element:
    """
    Transforms the special resource tags into generic versions.
    Moves the resource type in the corresponding resource type.
    """
    tree = deepcopy(tree)
    for elem in tree.iter():
        if elem.tag == "link":
            elem.attrib["restype"] = "LinkObj"
            elem.tag = "resource"
        elif elem.tag == "region":
            elem.attrib["restype"] = "Region"
            elem.tag = "resource"
        elif elem.tag == "video-segment":
            elem.attrib["restype"] = "VideoSegment"
            _correct_is_segment_of_property(elem, "VideoSegment")
            elem.tag = "resource"
        elif elem.tag == "audio-segment":
            elem.attrib["restype"] = "AudioSegment"
            _correct_is_segment_of_property(elem, "AudioSegment")
            elem.tag = "resource"
    return tree


def _correct_is_segment_of_property(segment: etree._Element, restype: str) -> None:
    for child in segment.iterchildren():
        if child.tag == "isSegmentOf":
            child.tag = f"is{restype}Of"
            break


def resolve_prefixes_for_properties_and_resources(root: etree._Element, api_url: str) -> XMLProject:
    """
    Resolves the prefixes in the root with the proper namespaces.
    """
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
