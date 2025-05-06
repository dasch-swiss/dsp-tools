from __future__ import annotations

from typing import cast

from lxml import etree

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.error.xmllib_warnings_util import raise_input_error
from dsp_tools.xmllib.internal.constants import DASCH_SCHEMA
from dsp_tools.xmllib.internal.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.internal.serialise_file_value import serialise_file_value
from dsp_tools.xmllib.internal.serialise_values import serialise_values
from dsp_tools.xmllib.internal.type_aliases import AnyResource
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.internal.file_values import AuthorshipLookup
from dsp_tools.xmllib.models.internal.values import ColorValue
from dsp_tools.xmllib.models.internal.values import Value
from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.value_checkers import is_nonempty_value


def serialise_resources(resources: list[AnyResource], authorship_lookup: AuthorshipLookup) -> list[etree._Element]:
    """
    Serialise all the resources

    Args:
        resources: list of resources
        authorship_lookup: lookup to map the authors to the corresponding IDs

    Returns:
        serialised resources
    """
    return [_serialise_one_resource(x, authorship_lookup) for x in resources]


def _serialise_one_resource(res: AnyResource, authorship_lookup: AuthorshipLookup) -> etree._Element:
    match res:
        case Resource():
            return _serialise_generic_resource(res, authorship_lookup)
        case RegionResource():
            return _serialise_region(res)
        case LinkResource():
            return _serialise_link(res)
        case AudioSegmentResource():
            return _serialise_segment(res, "audio-segment")
        case VideoSegmentResource():
            return _serialise_segment(res, "video-segment")
        case _:
            raise_input_error(
                MessageInfo(
                    f"An unknown resource was added to the root. "
                    f"Only Resource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource "
                    f"are permitted."
                    f"The input type is {res.__class__.__name__}"
                )
            )


def _serialise_generic_resource(res: Resource, authorship_lookup: AuthorshipLookup) -> etree._Element:
    ele = _make_generic_resource_element(res, "resource")
    ele.attrib["restype"] = res.restype
    if res.file_value:
        auth_id = authorship_lookup.get_id(res.file_value.metadata.authorship)
        ele.append(serialise_file_value(res.file_value, auth_id))
    ele.extend(serialise_values(res.values))
    return ele


def _serialise_region(res: RegionResource) -> etree._Element:
    ele = _make_generic_resource_element(res, "region")
    ele.extend(_serialise_geometry_shape(res))
    props: list[Value] = [res.region_of]
    if res.comments:
        cmnt = cast(list[Value], res.comments)
        props.extend(cmnt)
    ele.extend(serialise_values(props))
    return ele


def _serialise_geometry_shape(res: RegionResource) -> list[etree._Element]:
    prop_list: list[etree._Element] = []
    if not res.geometry:
        emit_xmllib_input_warning(
            MessageInfo(
                "The region resource does not have a geometry. Please note that an xmlupload will fail.", res.res_id
            )
        )

        return prop_list
    geo_prop = etree.Element(f"{DASCH_SCHEMA}geometry-prop", name="hasGeometry", nsmap=XML_NAMESPACE_MAP)
    ele = etree.Element(f"{DASCH_SCHEMA}geometry", nsmap=XML_NAMESPACE_MAP)
    ele.text = res.geometry.to_json_string()
    geo_prop.append(ele)
    prop_list.append(geo_prop)
    prop_list.extend(
        serialise_values([ColorValue(value=res.geometry.color, prop_name="hasColor")]),
    )
    return prop_list


def _serialise_link(res: LinkResource) -> etree._Element:
    problems = []
    if not res.comments:
        problems.append("at least one comment")
    if not res.link_to:
        problems.append("at least two links")
    if problems:
        msg = f"A link object requires {' and '.join(problems)}. Please note that an xmlupload will fail."
        emit_xmllib_input_warning(MessageInfo(msg, res.res_id))
    ele = _make_generic_resource_element(res, "link")
    comments = cast(list[Value], res.comments)
    links_to = cast(list[Value], res.link_to)
    generic_vals = comments + links_to
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
    if not is_nonempty_value(segment.res_id):
        problems.append(f"Field: Resource ID | Value: {segment.res_id}")
    if not is_nonempty_value(segment.label):
        problems.append(f"Field: label | Value: {segment.label}")
    if not is_nonempty_value(segment.segment_of):
        problems.append(f"Field: segment_of | Value: {segment.segment_of}")
    if segment.title and not is_nonempty_value(segment.title):
        problems.append(f"Field: title | Value: {segment.title}")
    if fails := [x for x in segment.comments if not is_nonempty_value(x)]:
        problems.extend([f"Field: comment | Value: {x}" for x in fails])
    if fails := [x for x in segment.descriptions if not is_nonempty_value(x)]:
        problems.extend([f"Field: description | Value: {x}" for x in fails])
    if fails := [x for x in segment.keywords if not is_nonempty_value(x)]:
        problems.extend([f"Field: keywords | Value: {x}" for x in fails])
    if fails := [x for x in segment.relates_to if not is_nonempty_value(x)]:
        problems.extend([f"Field: relates_to | Value: {x}" for x in fails])
    if problems:
        msg = f"This segment resource has the following problem(s):{'\n- '.join(problems)}"
        emit_xmllib_input_warning(MessageInfo(msg, segment.res_id))


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
