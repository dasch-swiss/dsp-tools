from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol


@dataclass
class DataDeserialised:
    shortcode: str
    default_onto: str
    resources: list[DataResource]


@dataclass
class DataResource:
    res_id: str
    res_class: str
    label: str
    values: list[DataValue]


@dataclass
class DataValue(Protocol):
    prop_name: str
    prop_value: Any


@dataclass
class DataSimpleText(DataValue):
    prop_name: str
    prop_value: str


@dataclass
class DataIntValue(DataValue):
    prop_name: str
    prop_value: str


@dataclass
class DataListValue(DataValue):
    prop_name: str
    prop_value: str
    list_name: str


@dataclass
class DataLinkValue(DataValue):
    prop_name: str
    prop_value: str
