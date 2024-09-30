from __future__ import annotations

import warnings
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib.models.values import ColorValue
from dsp_tools.xmllib.models.values import LinkValue
from dsp_tools.xmllib.models.values import Richtext
from dsp_tools.xmllib.value_checkers import find_geometry_problem
from dsp_tools.xmllib.value_checkers import is_decimal
from dsp_tools.xmllib.value_checkers import is_integer
from dsp_tools.xmllib.value_checkers import is_string_like

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
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        _check_strings(string_to_check=self.label, res_id=self.res_id, field_name="Label")
        match self.comments:
            case list():
                pass
            case set():
                self.comments = list(self.comments)
            case int() | str() | float():
                self.comments = [self.comments]
            case _:
                _warn_invalid_comments(self.comments, self.res_id)

    def new(
        self, res_id: str, label: str, comments: list[str], annotation_of: str, permissions: str = "res-default"
    ) -> AnnotationResource:
        return AnnotationResource(
            res_id=res_id, label=label, comments=comments, annotation_of=annotation_of, permissions=permissions
        )

    def add_comment(self, comment: str) -> AnnotationResource:
        self.comments.append(comment)
        return self

    def add_comments(self, comments: list[str]) -> AnnotationResource:
        self.comments.extend(comments)
        return self

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
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        _check_strings(string_to_check=self.label, res_id=self.res_id, field_name="Label")
        if fail_msg := find_geometry_problem(self.geometry):
            msg = f"The geometry of the resource with the ID '{self.res_id}' failed validation.\n" + fail_msg
            warnings.warn(DspToolsUserWarning(msg))
        match self.comments:
            case list():
                pass
            case set():
                self.comments = list(self.comments)
            case int() | str() | float():
                self.comments = [self.comments]
            case _:
                _warn_invalid_comments(self.comments, self.res_id)

    def add_comment(self, comment: str) -> RegionResource:
        self.comments.append(comment)
        return self

    def add_comments(self, comments: list[str]) -> RegionResource:
        self.comments.extend(comments)
        return self

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
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        _check_strings(string_to_check=self.label, res_id=self.res_id, field_name="Label")
        match self.comments:
            case list():
                pass
            case set():
                self.comments = list(self.comments)
            case int() | str() | float():
                self.comments = [self.comments]
            case _:
                _warn_invalid_comments(self.comments, self.res_id)

    def add_comment(self, comment: str) -> LinkResource:
        self.comments.append(comment)
        return self

    def add_comments(self, comments: list[str]) -> LinkResource:
        self.comments.extend(comments)
        return self

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
        prop_ele = etree.Element(f"{DASCH_SCHEMA}resptr-prop", name="hasLinkTo", nsmap=XML_NAMESPACE_MAP)
        vals = [LinkValue(value=x, prop_name="hasLinkTo", resource_id=self.res_id) for x in self.link_to]
        prop_ele.extend([v.make_element() for v in vals])
        return prop_ele


@dataclass
class VideoSegmentResource:
    res_id: str
    label: str
    segment_of: str
    segment_start: float
    segment_end: float
    title: str | None = None
    comments: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    relates_to: list[str] = field(default_factory=list)
    permissions: str = "res-default"

    def __post_init__(self) -> None:
        _validate_segment(self)
        match self.comments:
            case list():
                pass
            case set():
                self.comments = list(self.comments)
            case int() | str() | float():
                self.comments = [self.comments]
            case _:
                _warn_invalid_comments(self.comments, self.res_id)

    def add_title(self, title: str) -> VideoSegmentResource:
        if self.title:
            _warn_value_exists(self.title, title, "title", self.res_id)
        self.title = title
        return self

    def add_comment(self, comment: str) -> VideoSegmentResource:
        self.comments.append(comment)
        return self

    def add_comments(self, comments: list[str]) -> VideoSegmentResource:
        self.comments.extend(comments)
        return self

    def add_description(self, description: str) -> VideoSegmentResource:
        self.descriptions.append(description)
        return self

    def add_descriptions(self, descriptions: list[str]) -> VideoSegmentResource:
        self.descriptions.extend(descriptions)
        return self

    def add_keyword(self, keywords: str) -> VideoSegmentResource:
        self.keywords.append(keywords)
        return self

    def add_keywords(self, keywords: list[str]) -> VideoSegmentResource:
        self.keywords.extend(keywords)
        return self

    def add_relates_to(self, relates_to: str) -> VideoSegmentResource:
        self.relates_to.append(relates_to)
        return self

    def add_relates_to_multiple(self, relates_to: list[str]) -> VideoSegmentResource:
        self.relates_to.extend(relates_to)
        return self

    def serialise(self) -> etree._Element:
        res_ele = self._serialise_resource_element()
        res_ele.extend(_serialise_segment_children(self))
        return res_ele

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions:
            attribs["permissions"] = self.permissions
        return etree.Element(f"{DASCH_SCHEMA}video-segment", attrib=attribs, nsmap=XML_NAMESPACE_MAP)


@dataclass
class AudioSegmentResource:
    res_id: str
    label: str
    segment_of: str
    segment_start: float
    segment_end: float
    title: str | None = None
    comments: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    relates_to: list[str] = field(default_factory=list)
    permissions: str = "res-default"

    def __post_init__(self) -> None:
        _validate_segment(self)
        match self.comments:
            case list():
                pass
            case set():
                self.comments = list(self.comments)
            case int() | str() | float():
                self.comments = [self.comments]
            case _:
                _warn_invalid_comments(self.comments, self.res_id)

    def add_title(self, title: str) -> AudioSegmentResource:
        if self.title:
            _warn_value_exists(self.title, title, "title", self.res_id)
        self.title = title
        return self

    def add_comment(self, comment: str) -> AudioSegmentResource:
        self.comments.append(comment)
        return self

    def add_comments(self, comments: list[str]) -> AudioSegmentResource:
        self.comments.extend(comments)
        return self

    def add_description(self, description: str) -> AudioSegmentResource:
        self.descriptions.append(description)
        return self

    def add_descriptions(self, descriptions: list[str]) -> AudioSegmentResource:
        self.descriptions.extend(descriptions)
        return self

    def add_keyword(self, keywords: str) -> AudioSegmentResource:
        self.keywords.append(keywords)
        return self

    def add_keywords(self, keywords: list[str]) -> AudioSegmentResource:
        self.keywords.extend(keywords)
        return self

    def add_relates_to(self, relates_to: str) -> AudioSegmentResource:
        self.relates_to.append(relates_to)
        return self

    def add_relates_to_multiple(self, relates_to: list[str]) -> AudioSegmentResource:
        self.relates_to.extend(relates_to)
        return self

    def serialise(self) -> etree._Element:
        res_ele = self._serialise_resource_element()
        res_ele.extend(_serialise_segment_children(self))
        return res_ele

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions:
            attribs["permissions"] = self.permissions
        return etree.Element(f"{DASCH_SCHEMA}audio-segment", attrib=attribs, nsmap=XML_NAMESPACE_MAP)


def _check_strings(string_to_check: str, res_id: str, field_name: str) -> None:
    if not is_string_like(string_to_check):
        msg = (
            f"The resource with the ID '{res_id}' has an invalid string at the following location:\n"
            f"Field: {field_name} | Value: {string_to_check}"
        )
        warnings.warn(DspToolsUserWarning(msg))


def _serialise_has_comment(comments: list[str], res_id: str) -> etree._Element:
    cmts = [Richtext(value=x, prop_name="hasComment", resource_id=res_id) for x in comments]
    cmt_prop = cmts[0].make_prop()
    cmt_prop.extend([cmt.make_element() for cmt in cmts])
    return cmt_prop


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
    problems.extend(_validate_segment_bounds(segment.segment_start, segment.segment_end))
    if problems:
        msg = f"The resource with the ID '{segment.res_id}' has the following problem(s):{'\n- '.join(problems)}"
        warnings.warn(DspToolsUserWarning(msg))


def _validate_segment_bounds(segment_start: Any, segment_end: Any) -> list[str]:
    seg_bounds_msg = []
    if not is_decimal(segment_start) or not is_integer(segment_start):
        seg_bounds_msg.append(f"Segment start should be an integer or float, but it is: {segment_start}")
    if not is_decimal(segment_end) or not is_integer(segment_end):
        seg_bounds_msg.append(f"Segment end should be an integer or float, but it is: {segment_start}")
    return seg_bounds_msg


def _serialise_segment_children(segment: AudioSegmentResource | VideoSegmentResource) -> list[etree._Element]:
    segment_elements = []
    segment_of = etree.Element(f"{DASCH_SCHEMA}isSegmentOf", nsmap=XML_NAMESPACE_MAP)
    segment_of.text = segment.segment_of
    segment_elements.append(segment_of)
    segment_elements.append(
        etree.Element(
            f"{DASCH_SCHEMA}hasSegmentBounds",
            attrib={"start": str(segment.segment_start), "end": str(segment.segment_end)},
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


def _warn_invalid_comments(value: Any, res_id: str | None) -> None:
    msg = (
        f"The resource: {res_id} should have a list of strings for the field 'comments'. "
        f"Your input: '{value}' is of type {type(value)}"
    )
    warnings.warn(DspToolsUserWarning(msg))


def _warn_value_exists(old_value: Any, new_value: Any, value_field: str, res_id: str | None) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = (
        f"The resource with the ID '{res_id}' already has a value in the field '{value_field}'. "
        f"The old value '{old_value}' is being replace with '{new_value}'."
    )
    warnings.warn(DspToolsUserWarning(msg))
