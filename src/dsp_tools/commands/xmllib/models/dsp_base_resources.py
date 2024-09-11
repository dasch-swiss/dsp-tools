from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

from lxml import etree

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
        raise NotImplementedError

    def _serialise_resource_element(self) -> etree._Element:
        raise NotImplementedError

    def _serialise_values(self) -> etree._Element:
        raise NotImplementedError


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

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def _serialise_resource_element(self) -> etree._Element:
        raise NotImplementedError

    def _serialise_values(self) -> etree._Element:
        raise NotImplementedError


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
        raise NotImplementedError

    def _serialise_resource_element(self) -> etree._Element:
        raise NotImplementedError

    def _serialise_values(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class VideoSegmentResource:
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
        _check_and_warn_strings(self.res_id, self.res_id, "Resource ID")
        _check_and_warn_strings(self.res_id, self.label, "Label")

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
        _check_and_warn_strings(self.res_id, self.res_id, "Resource ID")
        _check_and_warn_strings(self.res_id, self.label, "Label")

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
