from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Any


@dataclass
class ParsedOntology:
    name: str
    label: str
    comment: str | None
    classes: list[ParsedClass]
    properties: list[ParsedProperty]
    cardinalities: list[ParsedClassCardinalities]


@dataclass
class ParsedClass:
    name: str
    info: dict[str, Any]


@dataclass
class ParsedProperty:
    name: str
    info: dict[str, Any]


@dataclass
class ParsedClassCardinalities:
    class_iri: str
    cards: list[ParsedPropertyCardinality]


@dataclass
class ParsedPropertyCardinality:
    propname: str
    cardinality: Cardinality
    gui_order: int | None


class Cardinality(Enum):
    C_0_1 = auto()
    C_1 = auto()
    C_0_N = auto()
    C_1_N = auto()
