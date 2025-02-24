from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias
from typing import Union

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.utils.date_util import Date


@dataclass
class IntervalFloats:
    start: float
    end: float


IntermediaryValueTypes: TypeAlias = Union[bool, str, float, int, FormattedTextValue, Date, IntervalFloats]


@dataclass
class IntermediaryValue:
    value: IntermediaryValueTypes
    prop_iri: str
    comment: str | None
    permissions: Permissions | None


@dataclass
class IntermediaryBoolean(IntermediaryValue):
    value: bool


@dataclass
class IntermediaryColor(IntermediaryValue):
    value: str


@dataclass
class IntermediaryDate(IntermediaryValue):
    value: Date


@dataclass
class IntermediaryDecimal(IntermediaryValue):
    value: float


@dataclass
class IntermediaryGeoname(IntermediaryValue):
    value: str


@dataclass
class IntermediaryGeometry(IntermediaryValue):
    value: str


@dataclass
class IntermediaryInt(IntermediaryValue):
    value: int


@dataclass
class IntermediaryInterval(IntermediaryValue):
    value: IntervalFloats


@dataclass
class IntermediaryLink(IntermediaryValue):
    value: str
    value_uuid: str

    def __post_init__(self) -> None:
        self.prop_iri = f"{self.prop_iri}Value"


@dataclass
class IntermediaryList(IntermediaryValue):
    value: str


@dataclass
class IntermediarySimpleText(IntermediaryValue):
    value: str


@dataclass
class IntermediaryRichtext(IntermediaryValue):
    value: FormattedTextValue
    resource_references: set[str]
    value_uuid: str


@dataclass
class IntermediaryTime(IntermediaryValue):
    value: str


@dataclass
class IntermediaryUri(IntermediaryValue):
    value: str
