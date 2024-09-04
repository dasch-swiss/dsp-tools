from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lxml import etree


@dataclass
class DSPAnnotation:
    res_id: str
    label: str
    comments: list[str]
    annotation_of: str
    permissions: str = "res-default"

    def serialise(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class DSPRegion:
    res_id: str
    label: str
    color: str
    region_of: str
    geometry: dict[str, Any]
    comments: list[str]
    permissions: str = "res-default"

    def serialise(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class DSPLink:
    res_id: str
    label: str
    link_to: list[str]
    comments: list[str]
    permissions: str = "res-default"

    def serialise(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class DSPVideoSegment:
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

    def serialise(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class DSPAudioSegment:
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

    def serialise(self) -> etree._Element:
        raise NotImplementedError
