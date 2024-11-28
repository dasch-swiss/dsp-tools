from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias
from typing import Union

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.utils.date_util import Date

ValueTypes: TypeAlias = Union[bool, str, float, int, FormattedTextValue, Date]


@dataclass
class IntermediaryValue:
    value: ValueTypes
    prop_iri: str
    comment: str | None
    permissions: Permissions | None


@dataclass
class IntermediaryBoolean(IntermediaryValue): ...


@dataclass
class IntermediaryColor(IntermediaryValue): ...


@dataclass
class IntermediaryDate(IntermediaryValue): ...


@dataclass
class IntermediaryDecimal(IntermediaryValue): ...


@dataclass
class IntermediaryGeoname(IntermediaryValue): ...


@dataclass
class IntermediaryInt(IntermediaryValue): ...


@dataclass
class IntermediaryLink(IntermediaryValue):
    resource_references: list[str]


@dataclass
class IntermediaryList(IntermediaryValue): ...


@dataclass
class IntermediarySimpleText(IntermediaryValue): ...


@dataclass
class IntermediaryRichtext(IntermediaryValue):
    resource_references: list[str]


@dataclass
class IntermediaryTime(IntermediaryValue): ...


@dataclass
class IntermediaryUri(IntermediaryValue): ...
