from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.utils.data_formats.date_util import Date


@dataclass
class IntervalFloats:
    start: float
    end: float


type ProcessedValueTypes = Union[bool, str, float, int, FormattedTextValue, Date, IntervalFloats]


@dataclass
class ProcessedValue:
    value: ProcessedValueTypes
    prop_iri: str
    comment: str | None
    permissions: Permissions | None


@dataclass
class ProcessedBoolean(ProcessedValue):
    value: bool


@dataclass
class ProcessedColor(ProcessedValue):
    value: str


@dataclass
class ProcessedDate(ProcessedValue):
    value: Date


@dataclass
class ProcessedDecimal(ProcessedValue):
    value: float


@dataclass
class ProcessedGeoname(ProcessedValue):
    value: str


@dataclass
class ProcessedGeometry(ProcessedValue):
    value: str


@dataclass
class ProcessedInt(ProcessedValue):
    value: int


@dataclass
class ProcessedInterval(ProcessedValue):
    value: IntervalFloats


@dataclass
class ProcessedLink(ProcessedValue):
    value: str
    value_uuid: str

    def __post_init__(self) -> None:
        self.prop_iri = f"{self.prop_iri}Value"


@dataclass
class ProcessedList(ProcessedValue):
    value: str


@dataclass
class ProcessedSimpleText(ProcessedValue):
    value: str


@dataclass
class ProcessedRichtext(ProcessedValue):
    value: FormattedTextValue
    resource_references: set[str]
    value_uuid: str


@dataclass
class ProcessedTime(ProcessedValue):
    value: str


@dataclass
class ProcessedUri(ProcessedValue):
    value: str
