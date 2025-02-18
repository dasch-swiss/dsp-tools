from __future__ import annotations

import warnings

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib.constants import DASCH_SCHEMA
from dsp_tools.xmllib.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.constants import AnyResource
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.value_checkers import is_string_like


def serialise_resources(resources: list[AnyResource]) -> etree._Element:
    pass


def _serialise_one_resource(res: AnyResource) -> etree._Element:
    pass


def _serialise_generic_resource(res: Resource) -> etree._Element:
    pass


def _serialise_region(res: RegionResource) -> etree._Element:
    # region
    pass


def _serialise_link(res: LinkResource) -> etree._Element:
    # link
    pass


def _serialise_segment(res: AudioSegmentResource | VideoSegmentResource, segment_type: str) -> etree._Element:
    # audio-segment
    # video-segment
    pass


def _serialise_dsp_in_built_resource_element(res: AnyResource, res_type: str) -> etree._Element:
    attribs = {"label": res.label, "id": res.res_id}
    if res.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
        attribs["permissions"] = res.permissions.value
    return etree.Element(f"{DASCH_SCHEMA}{res_type}", attrib=attribs, nsmap=XML_NAMESPACE_MAP)


def _validate_segment(segment: AudioSegmentResource | VideoSegmentResource) -> None:
    problems = []
    if not is_string_like(segment.res_id):
        problems.append(f"Field: Resource ID | Value: {segment.res_id}")
    if not is_string_like(segment.label):
        problems.append(f"Field: label | Value: {segment.label}")
    if not is_string_like(segment.segment_of):
        problems.append(f"Field: segment_of | Value: {segment.segment_of}")
    if segment.title and not is_string_like(segment.title):
        problems.append(f"Field: title | Value: {segment.title}")
    if fails := [x for x in segment.comments if not is_string_like(x)]:
        problems.extend([f"Field: comment | Value: {x}" for x in fails])
    if fails := [x for x in segment.descriptions if not is_string_like(x)]:
        problems.extend([f"Field: description | Value: {x}" for x in fails])
    if fails := [x for x in segment.keywords if not is_string_like(x)]:
        problems.extend([f"Field: keywords | Value: {x}" for x in fails])
    if fails := [x for x in segment.relates_to if not is_string_like(x)]:
        problems.extend([f"Field: relates_to | Value: {x}" for x in fails])
    if problems:
        msg = f"The resource with the ID '{segment.res_id}' has the following problem(s):{'\n- '.join(problems)}"
        warnings.warn(DspToolsUserWarning(msg))


def _serialise_segment_children(segment: AudioSegmentResource | VideoSegmentResource) -> list[etree._Element]:
    segment_elements = []
    segment_of = etree.Element(f"{DASCH_SCHEMA}isSegmentOf", nsmap=XML_NAMESPACE_MAP)
    segment_of.text = segment.segment_of
    segment_elements.append(segment_of)
    segment_elements.append(
        etree.Element(
            f"{DASCH_SCHEMA}hasSegmentBounds",
            attrib={
                "segment_start": str(segment.segment_bounds.segment_start),
                "segment_end": str(segment.segment_bounds.segment_end),
            },
            nsmap=XML_NAMESPACE_MAP,
        )
    )
    if segment.title:
        segment_elements.append(_make_element_with_text("hasTitle", segment.title))
    segment_elements.extend([_make_element_with_text("hasComment", x) for x in segment.comments])
    segment_elements.extend([_make_element_with_text("hasDescription", x) for x in segment.descriptions])
    segment_elements.extend([_make_element_with_text("hasKeyword", x) for x in segment.keywords])
    segment_elements.extend([_make_element_with_text("relatesTo", x) for x in segment.relates_to])
    return segment_elements


def _make_element_with_text(tag_name: str, text_content: str) -> etree._Element:
    ele = etree.Element(f"{DASCH_SCHEMA}{tag_name}", nsmap=XML_NAMESPACE_MAP)
    ele.text = text_content
    return ele
