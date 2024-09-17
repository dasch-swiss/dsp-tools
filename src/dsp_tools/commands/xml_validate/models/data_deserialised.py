from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class DataDeserialised:
    shortcode: str
    default_onto: str
    resources: list[ResourceData]


@dataclass
class ResourceData:
    res_id: str
    res_class: str
    label: str
    values: list[ValueData]


@dataclass
class ValueData(Protocol):
    prop_name: str
    prop_value: str


@dataclass
class BooleanValueData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class ColorValueData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class DateValueData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class DecimalValueData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class GeonameValueData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class IntValueData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class ListValueData(ValueData):
    prop_name: str
    prop_value: str
    list_name: str


@dataclass
class SimpleTextData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class RichtextData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class TimeValueData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class UriValueData(ValueData):
    prop_name: str
    prop_value: str


@dataclass
class LinkValueData(ValueData):
    prop_name: str
    prop_value: str
