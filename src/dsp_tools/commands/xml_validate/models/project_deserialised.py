from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ListDeserialised:
    list_name: str
    iri: str
    nodes: list[str]


@dataclass
class ResourceDeserialised:
    cls_id: str
    subClassOf: list[str]
    restrictions: dict[str, Cardinality]


@dataclass
class Cardinality(Protocol):
    onProperty: str


@dataclass
class CardinalityOne(Cardinality):
    onProperty: str


@dataclass
class CardinalityMaxOne(Cardinality):
    onProperty: str


@dataclass
class Property(Protocol):
    prop_name: str


@dataclass
class ListProperty(Property):
    prop_name: str
    list_name: str
    nodes: list[str]


@dataclass
class SimpleTextProperty(Property):
    # there are gui-attributes (eg. max-length) that are not considered in this test
    prop_name: str


@dataclass
class LinkProperty(Property):
    prop_name: str
    objectType: str
