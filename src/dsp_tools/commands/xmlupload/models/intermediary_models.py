from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import TypeAlias
from typing import Union

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.permission import Permissions

OutputTypes: TypeAlias = Union[str, FormattedTextValue, bool, float, int]


@dataclass
class ResourceTransformationProblems:
    res_id: str
    problems: list[str]


@dataclass
class PermissionsNotFound(Exception):
    permission_str: str


@dataclass
class CollectedProblems:
    problems: list[str]


@dataclass
class ResolvingInformationProblem:
    problem: str


@dataclass
class TransformationSteps:
    intermediary_value: Callable[[str, Any, str | None, Permissions | None], IntermediaryValue]
    transformer: Callable[[Any], OutputTypes]


@dataclass
class IntermediaryResource:
    res_id: str
    res_type: str
    values: list[IntermediaryValue]
    permissions: Permissions | None
    file_value: IntermediaryAbstractFileValue | None


@dataclass
class IntermediaryValue:
    prop_name: str
    value: bool | str | int | float | FormattedTextValue
    comment: str | None
    permissions: Permissions | None


@dataclass
class IntermediaryBoolean:
    value: bool


@dataclass
class IntermediaryRichtext:
    value: FormattedTextValue


@dataclass
class IntermediarySimpleText:
    value: str


@dataclass
class IntermediaryAbstractFileValue:
    value: str
    permissions: Permissions | None
