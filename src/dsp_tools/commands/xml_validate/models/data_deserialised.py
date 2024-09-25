from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass
class ProjectDeserialised:
    info: ProjectInformation
    data: DataDeserialised


@dataclass
class ProjectInformation:
    shortcode: str
    default_onto: str


@dataclass
class DataDeserialised:
    resources: list[AbstractResource]


@dataclass
class AbstractResource(ABC):
    res_id: str
    label: str


@dataclass
class ResourceDeserialised(AbstractResource):
    res_class: str
    values: list[ValueDeserialised]


@dataclass
class AnnotationDeserialised(AbstractResource): ...


@dataclass
class RegionDeserialised(AbstractResource): ...


@dataclass
class LinkObjDeserialised(AbstractResource): ...


@dataclass
class VideoSegmentDeserialised(AbstractResource): ...


@dataclass
class AudioSegmentDeserialised(AbstractResource): ...


@dataclass
class ValueDeserialised:
    prop_name: str
    object_value: str | None


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
