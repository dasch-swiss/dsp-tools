from __future__ import annotations

import warnings

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.constants import DASCH_SCHEMA
from dsp_tools.xmllib.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.constants import AnyResource
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.models.values import ColorValue
from dsp_tools.xmllib.models.values import Value
from dsp_tools.xmllib.serialise.serialise_file_value import serialise_file_value
from dsp_tools.xmllib.serialise.serialise_values import serialise_values
from dsp_tools.xmllib.value_checkers import is_string_like


def serialise_resources(resources: list[AnyResource]) -> etree._Element:
    """
    Serialise all the resources

    Args:
        resources: list of resources

    Returns:
        serialised resources
    """
    return [_serialise_one_resource(x) for x in resources]


def _serialise_one_resource(res: AnyResource) -> etree._Element:
    match res:
        case Resource():
            return _serialise_generic_resource(res)
        case RegionResource():
            return _serialise_region(res)
        case LinkResource():
            return _serialise_link(res)
        case AudioSegmentResource():
            return _serialise_segment(res, "audio-segment")
        case VideoSegmentResource():
            return _serialise_segment(res, "video-segment")
        case _:
            raise InputError(
                f"An unknown resource was added to the root. "
                f"Only Resource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource "
                f"are permitted."
                f"The input type is {res.__class__.__name__}"
            )


def _serialise_generic_resource(res: Resource) -> etree._Element:
    ele = _make_generic_resource_element(res, "resource")
    ele.attrib["restype"] = res.restype
    if res.file_value:
        ele.append(serialise_file_value(ele.file_value))
    ele.extend(serialise_values(ele.values))
    return ele


def _serialise_region(res: RegionResource) -> etree._Element:
    ele = _make_generic_resource_element(res, "region")
    ele.extend(_serialise_geometry_shape(res))
    props: list[Value] = [res.region_of]
    if res.comments:
        props.append(res.comments)
    ele.extend(serialise_values(props))
    return ele


def _serialise_geometry_shape(res: RegionResource) -> list[etree._Element]:
    prop_list: list[etree._Element] = []
    if not res.geometry:
        msg = (
            f"The region resource with the ID '{res.res_id}' does not have a geometry, "
            f"please note that an xmlupload will fail."
        )
        warnings.warn(DspToolsUserWarning(msg))

        return prop_list
    geo_prop = etree.Element(f"{DASCH_SCHEMA}geometry-prop", name="hasGeometry", nsmap=XML_NAMESPACE_MAP)
    ele = etree.Element(f"{DASCH_SCHEMA}geometry", nsmap=XML_NAMESPACE_MAP)
    ele.text = res.geometry.to_json_string()
    geo_prop.append(ele)
    prop_list.append(geo_prop)
    prop_list.extend(
        serialise_values([ColorValue(value=res.geometry.color, prop_name="hasColor", resource_id=res.res_id)]),
    )
    return prop_list


def _serialise_link(res: LinkResource) -> etree._Element:
    problem = []
    if not res.comments:
        problem.append("at least one comment")
    if not res.link_to:
        problem.append("at least two links")
    if problem:
        msg = (
            f"The link object with the ID '{res.res_id}' requires: {' and '.join(problem)} "
            f"Please note that an xmlupload will fail."
        )
        warnings.warn(DspToolsUserWarning(msg))
    ele = _make_generic_resource_element(res, "link")
    generic_vals = res.comments + res.link_to
    ele.extend(serialise_values(generic_vals))
    return ele


def _serialise_segment(res: AudioSegmentResource | VideoSegmentResource, segment_type: str) -> etree._Element:
    _validate_segment(res)
    seg = _make_generic_resource_element(res, segment_type)
    seg.extend(_serialise_segment_children(res))
    return seg


def _make_generic_resource_element(res: AnyResource, res_type: str) -> etree._Element:
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
