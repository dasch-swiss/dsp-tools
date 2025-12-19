from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX
from dsp_tools.utils.rdf_constants import SALSAH_GUI_PREFIX


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
    labels: dict[str, str]
    comments: dict[str, str] | None
    supers: list[str]
    onto_iri: str


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
    BOOLEAN = f"{KNORA_API_PREFIX}BooleanValue"
    COLOR = f"{KNORA_API_PREFIX}ColorValue"
    DATE = f"{KNORA_API_PREFIX}DateValue"
    DECIMAL = f"{KNORA_API_PREFIX}DecimalValue"
    GEONAME = f"{KNORA_API_PREFIX}GeonameValue"
    INT = f"{KNORA_API_PREFIX}IntValue"
    LIST = f"{KNORA_API_PREFIX}ListValue"
    TEXT = f"{KNORA_API_PREFIX}TextValue"
    TIME = f"{KNORA_API_PREFIX}TimeValue"
    URI = f"{KNORA_API_PREFIX}UriValue"


class GuiElement(StrEnum):
    CHECKBOX = f"{SALSAH_GUI_PREFIX}Checkbox"
    COLORPICKER = f"{SALSAH_GUI_PREFIX}Colorpicker"
    DATE = f"{SALSAH_GUI_PREFIX}Date"
    SPINBOX = f"{SALSAH_GUI_PREFIX}Spinbox"
    GEONAMES = f"{SALSAH_GUI_PREFIX}Geonames"
    LIST = f"{SALSAH_GUI_PREFIX}List"
    SIMPLETEXT = f"{SALSAH_GUI_PREFIX}SimpleText"
    TEXTAREA = f"{SALSAH_GUI_PREFIX}Textarea"
    RICHTEXT = f"{SALSAH_GUI_PREFIX}Richtext"
    SEARCHBOX = f"{SALSAH_GUI_PREFIX}Searchbox"
    TIME_STAMP = f"{SALSAH_GUI_PREFIX}TimeStamp"


@dataclass
class ParsedClassCardinalities:
    class_iri: str
    cards: list[ParsedPropertyCardinality]


@dataclass
class ParsedPropertyCardinality:
    propname: str
    cardinality: Cardinality
    gui_order: int | None


class Cardinality(StrEnum):
    C_0_1 = "0-1"
    C_1 = "1"
    C_0_N = "0-n"
    C_1_N = "1-n"
