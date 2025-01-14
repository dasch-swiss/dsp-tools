from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from lxml import etree


@dataclass
class XMLProject:
    shortcode: str
    root: etree._Element
    used_ontologies: set[str]


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
    resources: list[ResourceDeserialised]
    file_values: list[AbstractFileValueDeserialised]


@dataclass
class ResourceDeserialised:
    res_id: str
    unreified_triples: list[UnreifiedTripleObject]
    values: list[ValueDeserialised]


@dataclass
class ReifiedTripleObject:
    prop_name: str
    triples: list[UnreifiedTripleObject]


@dataclass
class UnreifiedTripleObject:
    prop_name: str
    object_value: str | None
    data_type: DataTypes


@dataclass
class KnoraTypePropInfo:
    value_type: str
    knora_prop: str
    data_type: DataTypes


class DataTypes(Enum):
    boolean = "boolean"
    datetime = "datetime"
    decimal = "decimal"
    integer = "integer"
    iri = "iri"
    string = "string"
    uri = "uri"


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


@dataclass
class AbstractFileValueDeserialised:
    res_id: str
    value: str | None


@dataclass
class BitstreamDeserialised(AbstractFileValueDeserialised): ...


@dataclass
class IIIFUriDeserialised(AbstractFileValueDeserialised): ...
