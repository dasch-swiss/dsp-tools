from __future__ import annotations

from copy import deepcopy

from lxml import etree

from dsp_tools.utils.xml_parsing.xx_parse_and_transform_file import transform_into_localnames


def transform_special_tags_make_localname(input_tree: etree._Element) -> etree._Element:
    """
    This function removes the namespace URIs from the elements' names
    and transforms the special tags `<region>`, `<link>`, `<video-segment>`, `<audio-segment>`
    to their technically correct form
    `<resource restype="Region">`, `<resource restype="LinkObj">`,
    `<resource restype="VideoSegment">`, `<resource restype="AudioSegment">`.

    Args:
        input_tree: unclean tree

    Returns:
        cleaned tree
    """
    tree = transform_into_localnames(input_tree)
    return _transform_special_tags(tree)


def _transform_special_tags(tree: etree._Element) -> etree._Element:
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
