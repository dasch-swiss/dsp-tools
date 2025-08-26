from __future__ import annotations

import os

from dotenv import load_dotenv
from lxml import etree

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.error.xmllib_warnings_util import raise_xmllib_input_error
from dsp_tools.xmllib.internal.constants import DASCH_SCHEMA
from dsp_tools.xmllib.internal.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.internal.serialise_file_value import serialise_file_value
from dsp_tools.xmllib.internal.serialise_values import serialise_values
from dsp_tools.xmllib.internal.type_aliases import AnyResource
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.internal.file_values import AuthorshipLookup
from dsp_tools.xmllib.models.internal.values import ColorValue
from dsp_tools.xmllib.models.internal.values import LinkValue
from dsp_tools.xmllib.models.internal.values import Richtext
from dsp_tools.xmllib.models.internal.values import Value
from dsp_tools.xmllib.models.permissions import Permissions
from dsp_tools.xmllib.models.res import Resource

load_dotenv()


def serialise_resources(resources: list[AnyResource], authorship_lookup: AuthorshipLookup) -> list[etree._Element]:
    """
    Serialise all the resources

    Args:
        resources: list of resources
        authorship_lookup: lookup to map the authors to the corresponding IDs

    Returns:
        serialised resources
    """
    env_var = str(os.getenv("XMLLIB_SORT_RESOURCES")).lower()
    if env_var == "true":
        resources = sorted(resources, key=lambda x: x.res_id)
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
            raise_xmllib_input_error(
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
    ele.extend(serialise_values(res.values))
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
    geo_attrib = (
        {"permissions": res.permissions.value} if res.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS else {}
    )
    ele = etree.Element(f"{DASCH_SCHEMA}geometry", nsmap=XML_NAMESPACE_MAP, attrib=geo_attrib)
    ele.text = res.geometry.to_json_string()
    geo_prop.append(ele)
    prop_list.append(geo_prop)
    prop_list.extend(
        serialise_values([ColorValue(value=res.geometry.color, prop_name="hasColor", permissions=res.permissions)]),
    )
    return prop_list


def _serialise_link(res: LinkResource) -> etree._Element:
    problems = []
    if not any([isinstance(x, Richtext) for x in res.values]):
        problems.append("at least one comment")
    if not any([isinstance(x, LinkValue) for x in res.values]):
        problems.append("at least two links")
    if problems:
        msg = f"A link object requires {' and '.join(problems)}. Please note that an xmlupload will fail."
        emit_xmllib_input_warning(MessageInfo(msg, res.res_id))
    ele = _make_generic_resource_element(res, "link")
    ele.extend(serialise_values(res.values))
    return ele


def _serialise_segment(res: AudioSegmentResource | VideoSegmentResource, segment_type: str) -> etree._Element:
    seg = _make_generic_resource_element(res, segment_type)
    seg.extend(_serialise_segment_children(res))
    return seg


def _make_generic_resource_element(res: AnyResource, res_type: str) -> etree._Element:
    attribs = {"label": res.label, "id": res.res_id}
    if res.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
        attribs["permissions"] = res.permissions.value
    return etree.Element(f"{DASCH_SCHEMA}{res_type}", attrib=attribs, nsmap=XML_NAMESPACE_MAP)


def _serialise_segment_children(segment: AudioSegmentResource | VideoSegmentResource) -> list[etree._Element]:
    # The segment elements need to be in a specific order in order to pass the XSD validation
    # Therefore, this filtering according to the properties is necessary
    segment_elements = _serialise_according_to_prop_name(segment.values, "isSegmentOf")
    bounds_attrib = {
        "segment_start": str(segment.segment_bounds.segment_start),
        "segment_end": str(segment.segment_bounds.segment_end),
    }
    if segment.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
        bounds_attrib["permissions"] = segment.permissions.value
    segment_elements.append(
        etree.Element(
            f"{DASCH_SCHEMA}hasSegmentBounds",
            attrib=bounds_attrib,
            nsmap=XML_NAMESPACE_MAP,
        )
    )
    segment_elements.extend(_serialise_according_to_prop_name(segment.values, "hasTitle"))
    segment_elements.extend(_serialise_according_to_prop_name(segment.values, "hasComment"))
    segment_elements.extend(_serialise_according_to_prop_name(segment.values, "hasDescription"))
    segment_elements.extend(_serialise_according_to_prop_name(segment.values, "hasKeyword"))
    segment_elements.extend(_serialise_according_to_prop_name(segment.values, "relatesTo"))
    return segment_elements


def _serialise_according_to_prop_name(values: list[Value], prop_name: str) -> list[etree._Element]:
    to_serialise = (x for x in values if x.prop_name == prop_name)
    return [_make_element_with_text(x) for x in to_serialise]


def _make_element_with_text(value: Value) -> etree._Element:
    attribs = {}
    if value.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
        attribs["permissions"] = value.permissions.value
    if value.comment is not None:
        attribs["comment"] = str(value.comment)
    ele = etree.Element(f"{DASCH_SCHEMA}{value.prop_name}", nsmap=XML_NAMESPACE_MAP, attrib=attribs)
    ele.text = value.value
    return ele
