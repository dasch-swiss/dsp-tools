from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol


@dataclass
class DataDeserialised:
    shortcode: str
    default_onto: str
    resources: list[ResourceDeserialised]


@dataclass
class ResourceDeserialised:
    res_id: str
    res_class: str
    label: str
    values: list[ValueDeserialised]


@dataclass
class ValueDeserialised(Protocol):
    prop_name: str
    prop_value: Any
    res_id: str
    comments: str | None


@dataclass
class SimpleTextValueDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    res_id: str
    comments: str | None


@dataclass
class ListValueDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    list_name: str
    res_id: str
    comments: str | None


@dataclass
class LinkValueDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    res_id: str
    comments: str | None
