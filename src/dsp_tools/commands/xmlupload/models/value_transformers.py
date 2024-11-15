from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TypeAlias
from typing import Union
from typing import assert_never

from dsp_tools.utils.date_util import Date

InputTypes: TypeAlias = Union[str]
OutputTypes: TypeAlias = Union[str, Date]


@dataclass(frozen=True)
class ValueTransformer(ABC):
    @abstractmethod
    def transform(self, input_value: InputTypes) -> OutputTypes: ...

    @staticmethod
    def _assert_is_string(value: str) -> str:
        match value:
            case str() as s:
                return s
            case _:
                assert_never(value)


class DecimalTransformer(ValueTransformer):
    def transform(self, input_value: str) -> str:
        val = self._assert_is_string(input_value)
        return str(float(val))
