from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ListDeserialised:
    list_name: str
    iri: str
    nodes: list[str]


@dataclass
class ProjectDeserialised:
    resources: list[ResourceDeserialised]
    properties: list[Property]


@dataclass
class ResourceDeserialised:
    cls_id: str
    restrictions: dict[str, Cardinality]


@dataclass
class Cardinality(Protocol):
    onProperty: str


@dataclass
class CardinalityOne(Cardinality):
    onProperty: str


@dataclass
class CardinalityZeroToN(Cardinality):
    onProperty: str


@dataclass
class Property(Protocol):
    prop_name: str

    def type(self) -> str:
        raise NotImplementedError


@dataclass
class ListProperty(Property):
    prop_name: str
    list_name: str | None
    nodes: list[str]

    def type(self) -> str:
        return "ListValue"


@dataclass
class SimpleTextProperty(Property):
    # there are gui-attributes (eg. max-length) that are not considered in this test,
    # but should be included in the final code
    prop_name: str

    def type(self) -> str:
        return "SimpleText"


@dataclass
class LinkProperty(Property):
    prop_name: str
    objectType: set[str]

    def type(self) -> str:
        return "LinkValue"
