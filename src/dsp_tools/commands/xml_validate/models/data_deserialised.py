from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProjectData:
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
class AnnotationDeserialised:
    res_id: str


@dataclass
class RegionDeserialised:
    res_id: str


@dataclass
class LinkObjDeserialised:
    res_id: str


@dataclass
class VideoSegmentDeserialised:
    res_id: str


@dataclass
class AudioSegmentDeserialised:
    res_id: str


@dataclass
class ValueDeserialised:
    prop_name: str
    object_value: str


@dataclass
class BooleanValueDeserialised(ValueDeserialised): ...


@dataclass
class ColorValueDeserialised(ValueDeserialised): ...


@dataclass
class DateValueDeserialised(ValueDeserialised): ...


@dataclass
class DecimalValueDeserialised(ValueDeserialised): ...


@dataclass
class GeonameValueDeserialised(ValueDeserialised): ...


@dataclass
class IntValueDeserialised(ValueDeserialised): ...


@dataclass
class LinkValueDeserialised(ValueDeserialised): ...


@dataclass
class ListValueDeserialised(ValueDeserialised):
    list_name: str


@dataclass
class SimpleTextDeserialised(ValueDeserialised): ...


@dataclass
class RichtextDeserialised(ValueDeserialised): ...


@dataclass
class TimeValueDeserialised(ValueDeserialised): ...


@dataclass
class UriValueDeserialised(ValueDeserialised): ...
