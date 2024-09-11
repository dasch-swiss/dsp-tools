from __future__ import annotations

import warnings
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from lxml import etree

from dsp_tools.commands.xmllib.models.values import ColorValue
from dsp_tools.commands.xmllib.models.values import LinkValue
from dsp_tools.commands.xmllib.models.values import SimpleText
from dsp_tools.commands.xmllib.value_checkers import is_decimal
from dsp_tools.commands.xmllib.value_checkers import is_geometry
from dsp_tools.commands.xmllib.value_checkers import is_integer
from dsp_tools.commands.xmllib.value_checkers import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class AnnotationResource:
    res_id: str
    label: str
    comments: list[str]
    annotation_of: str
    permissions: str = "res-default"

    def __post_init__(self) -> None:
        _check_and_warn_strings(self.res_id, self.res_id, "Resource ID")
        _check_and_warn_strings(self.res_id, self.label, "Label")

    def serialise(self) -> etree._Element:
        res_ele = self._serialise_resource_element()
        res_ele.append(self._serialise_annotation_of())
        res_ele.append(_serialise_has_comment(self.comments, self.res_id))
        return res_ele

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions:
            attribs["permissions"] = self.permissions
        return etree.Element(f"{DASCH_SCHEMA}annotation", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_annotation_of(self) -> etree._Element:
        return LinkValue(value=self.annotation_of, prop_name="isAnnotationOf", resource_id=self.res_id).serialise()


@dataclass
class RegionResource:
    res_id: str
    label: str
    color: str
    region_of: str
    geometry: dict[str, Any]
    comments: list[str]
    permissions: str = "res-default"

    def __post_init__(self) -> None:
        _check_and_warn_strings(self.res_id, self.res_id, "Resource ID")
        _check_and_warn_strings(self.res_id, self.label, "Label")
        if fail_msg := is_geometry(self.geometry):
            msg = f"The geometry of the resource with the ID '{self.res_id}' failed validation.\n" + fail_msg
            warnings.warn(DspToolsUserWarning(msg))

    def serialise(self) -> etree._Element:
        res_ele = self._serialise_resource_element()
        res_ele.append(self._serialise_geometry())
        res_ele.extend(self._serialise_values())
        if self.comments:
            res_ele.append(_serialise_has_comment(self.comments, self.res_id))
        return res_ele

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions:
            attribs["permissions"] = self.permissions
        return etree.Element(f"{DASCH_SCHEMA}region", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_values(self) -> list[etree._Element]:
        return [
            ColorValue(value=self.color, prop_name="hasColor", resource_id=self.res_id).serialise(),
            LinkValue(value=self.region_of, prop_name="isRegionOf", resource_id=self.res_id).serialise(),
        ]

    def _serialise_geometry(self) -> etree._Element:
        geo_prop = etree.Element(f"{DASCH_SCHEMA}geometry-prop", name="hasGeometry", nsmap=XML_NAMESPACE_MAP)
        ele = etree.Element(f"{DASCH_SCHEMA}geometry", nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.geometry)
        geo_prop.append(ele)
        return geo_prop


@dataclass
class LinkResource:
    res_id: str
    label: str
    link_to: list[str]
    comments: list[str]
    permissions: str = "res-default"

    def __post_init__(self) -> None:
        _check_and_warn_strings(self.res_id, self.res_id, "Resource ID")
        _check_and_warn_strings(self.res_id, self.label, "Label")

    def serialise(self) -> etree._Element:
        res_ele = self._serialise_resource_element()
        res_ele.append(_serialise_has_comment(self.comments, self.res_id))
        res_ele.append(self._serialise_links())
        return res_ele

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions:
            attribs["permissions"] = self.permissions
        return etree.Element(f"{DASCH_SCHEMA}link", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_links(self) -> etree._Element:
        vals = [LinkValue(value=x, prop_name="hasLinkTo", resource_id=self.res_id) for x in self.link_to]
        prop_ele = vals[0].make_prop()
        for v in vals:
            prop_ele.append(v.make_element())
        return prop_ele


@dataclass
class VideoSegmentResource:
    res_id: str
    label: str
    segment_of: str
    segment_start: float
    segment_end: float
    title: str | None = None
    comment: list[str] = field(default_factory=list)
    description: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    relates_to: list[str] = field(default_factory=list)
    permissions: str = "res-default"

    def __post_init__(self) -> None:
        _validate_segment(self)

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def _serialise_resource_element(self) -> etree._Element:
        raise NotImplementedError

    def _serialise_values(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class AudioSegmentResource:
    res_id: str
    label: str
    segment_of: str
    segment_start: float
    segment_end: float
    title: str | None = None
    comment: list[str] | None = None
    description: list[str] | None = None
    keywords: list[str] | None = None
    relates_to: list[str] | None = None
    permissions: str = "res-default"

    def __post_init__(self) -> None:
        _validate_segment(self)

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def _serialise_resource_element(self) -> etree._Element:
        raise NotImplementedError

    def _serialise_values(self) -> etree._Element:
        raise NotImplementedError


def _check_and_warn_strings(res_id: str, string_to_check: str, field_name: str) -> None:
    if not is_string(str(string_to_check)):
        msg = (
            f"The resource with the ID: '{res_id}' has an invalid string at the following location:\n"
            f"Field: {field_name} | Value: {string_to_check}"
        )
        warnings.warn(DspToolsUserWarning(msg))


def _warn_type_mismatch(expected_type: str, value: Any, field_name: str, res_id: str | None) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = f"At the following location a '{expected_type}' does not conform to the expected format.\n"
    msg += f"Resource: {res_id} | " if res_id else ""
    msg += f"Value: {value} | Field: {field_name}"
    warnings.warn(DspToolsUserWarning(msg))


def _serialise_has_comment(comments: list[str], res_id: str) -> etree._Element:
    cmts = [SimpleText(value=x, prop_name="hasComment", resource_id=res_id) for x in comments]
    cmt_prop = cmts[0].make_prop()
    for cmt in cmts:
        cmt_prop.append(cmt.make_element())
    return cmt_prop


def _validate_segment(segment: AudioSegmentResource | VideoSegmentResource) -> None:
    _check_and_warn_strings(segment.res_id, segment.res_id, "Resource ID")
    _check_and_warn_strings(segment.res_id, segment.label, "Label")
    _check_and_warn_strings(segment.res_id, segment.segment_of, "isSegmentOf")
    if segment.title:
        _check_and_warn_strings(segment.res_id, segment.segment_of, "isSegmentOf")
    for c in segment.comment:
        _check_and_warn_strings(segment.res_id, c, "comment")
    for c in segment.description:
        _check_and_warn_strings(segment.res_id, c, "description")
    for c in segment.keywords:
        _check_and_warn_strings(segment.res_id, c, "keywords")
    for c in segment.relates_to:
        _check_and_warn_strings(segment.res_id, c, "relates_to")
    seg_bounds_msg = ""
    if not is_decimal(segment.segment_start) or not is_integer(segment.segment_start):
        seg_bounds_msg += f"\nSegment start: {segment.segment_start}"
    if not is_decimal(segment.segment_end) or not is_integer(segment.segment_end):
        seg_bounds_msg += f"\nSegment end: {segment.segment_start}"
    if seg_bounds_msg:
        msg = (
            f"The segment bounds should be valid integers or decimals. The resource with the ID: "
            f"'{segment.res_id}' has the following invalid value(s){seg_bounds_msg}"
        )
        warnings.warn(DspToolsUserWarning(msg))
