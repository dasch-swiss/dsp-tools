from __future__ import annotations

import copy
from copy import deepcopy

from lxml import etree


def transform_into_localnames(root: etree._Element) -> etree._Element:
    """Removes the namespace of the tags."""
    tree = deepcopy(root)
    for elem in tree.iter():
        elem.tag = etree.QName(elem).localname
    return tree


def remove_comments_from_element_tree(input_tree: etree._Element) -> etree._Element:
    """Removes comments and processing instructions."""
    root = copy.deepcopy(input_tree)
    for c in root.xpath("//comment()"):
        c.getparent().remove(c)
    for c in root.xpath("//processing-instruction()"):
        c.getparent().remove(c)
    return root


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
