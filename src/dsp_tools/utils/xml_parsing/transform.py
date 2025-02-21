from __future__ import annotations

from copy import deepcopy

from lxml import etree


def transform_special_tags(tree: etree._Element) -> etree._Element:
    """Transforms the special resource and property tags so that it is consistent with the regular ones."""
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
