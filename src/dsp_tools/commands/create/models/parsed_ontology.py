from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import StrEnum
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
class Labels:
    values: dict[str, str]


@dataclass
class Comments:
    values: dict[str, str]


@dataclass
class Supers:
    values: list[str]


@dataclass
class ParsedClass:
    name: str
    info: dict[str, Any]


@dataclass
class ParsedProperty:
    name: str
    labels: Labels
    comments: Comments
    supers: Supers
    object: str
    subject: str | None
    gui_element: GuiElement
    list_iri: str


@dataclass
class ParsedClassCardinalities:
    class_iri: str
    cards: list[ParsedPropertyCardinality]


@dataclass
class ParsedPropertyCardinality:
    propname: str
    cardinality: Cardinality
    gui_order: int | None


class GuiElement(StrEnum):
    CHECKBOX = "Checkbox"
    COLORPICKER = "Colorpicker"
    DATE = "Date"
    SPINBOX = "Spinbox"
    GEONAMES = "Geonames"
    LIST = "List"
    SIMPLETEXT = "SimpleText"
    TEXTAREA = "Textarea"
    RICHTEXT = "Richtext"
    SEARCHBOX = "Searchbox"
    TIME_STAMP = "TimeStamp"


class Cardinality(Enum):
    C_0_1 = auto()
    C_1 = auto()
    C_0_N = auto()
    C_1_N = auto()
