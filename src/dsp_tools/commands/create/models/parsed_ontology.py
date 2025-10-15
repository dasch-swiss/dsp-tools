from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Any


@dataclass
class ParsedOntology:
    name: str
    label: str
    comment: str


@dataclass
class ParsedClass:
    info: dict[str, Any]


@dataclass
class ParsedProperty:
    info: dict[str, Any]


@dataclass
class ParsedClassCardinalities:
    class_iri: str


@dataclass
class ParsedPropertyCardinality:
    propname: str
    cardinality: str
    gui_order: int


class Cardinality(Enum):
    C_0_1 = auto()
    C_1 = auto()
    C_1_N = auto()
    C_0_N = auto()
