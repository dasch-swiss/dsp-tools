from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import StrEnum
from enum import auto
from typing import Any

from dsp_tools.commands.create.constants import KNORA_API_STR
from dsp_tools.commands.create.constants import SALSAH_GUI_STR


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
    labels: dict[str, str]
    comments: dict[str, str] | None
    supers: list[str]
    object: KnoraObjectType | str
    subject: str | None
    gui_element: GuiElement
    node_name: str | None
    onto_iri: str


class KnoraObjectType(StrEnum):
    BOOLEAN = f"{KNORA_API_STR}BooleanValue"
    COLOR = f"{KNORA_API_STR}ColorValue"
    DATE = f"{KNORA_API_STR}DateValue"
    DECIMAL = f"{KNORA_API_STR}DecimalValue"
    GEONAME = f"{KNORA_API_STR}GeonameValue"
    INT = f"{KNORA_API_STR}IntValue"
    LIST = f"{KNORA_API_STR}ListValue"
    TEXT = f"{KNORA_API_STR}TextValue"
    TIME = f"{KNORA_API_STR}TimeValue"
    URI = f"{KNORA_API_STR}UriValue"


class GuiElement(StrEnum):
    CHECKBOX = f"{SALSAH_GUI_STR}Checkbox"
    COLORPICKER = f"{SALSAH_GUI_STR}Colorpicker"
    DATE = f"{SALSAH_GUI_STR}Date"
    SPINBOX = f"{SALSAH_GUI_STR}Spinbox"
    GEONAMES = f"{SALSAH_GUI_STR}Geonames"
    LIST = f"{SALSAH_GUI_STR}List"
    SIMPLETEXT = f"{SALSAH_GUI_STR}SimpleText"
    TEXTAREA = f"{SALSAH_GUI_STR}Textarea"
    RICHTEXT = f"{SALSAH_GUI_STR}Richtext"
    SEARCHBOX = f"{SALSAH_GUI_STR}Searchbox"
    TIME_STAMP = f"{SALSAH_GUI_STR}TimeStamp"


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
