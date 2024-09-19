from __future__ import annotations

from dataclasses import dataclass


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
class ValueData:
    prop_name: str
    prop_value: str


@dataclass
class BooleanValueData(ValueData): ...


@dataclass
class ColorValueData(ValueData): ...


@dataclass
class DateValueData(ValueData): ...


@dataclass
class DecimalValueData(ValueData): ...


@dataclass
class GeonameValueData(ValueData): ...


@dataclass
class IntValueData(ValueData): ...


@dataclass
class ListValueData(ValueData):
    prop_name: str
    prop_value: str
    list_name: str


@dataclass
class SimpleTextData(ValueData): ...


@dataclass
class RichtextData(ValueData): ...


@dataclass
class TimeValueData(ValueData): ...


@dataclass
class UriValueData(ValueData): ...


@dataclass
class LinkValueData(ValueData): ...
