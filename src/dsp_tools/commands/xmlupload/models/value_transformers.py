from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TypeAlias
from typing import Union
from typing import assert_never

InputTypes: TypeAlias = Union[str]
OutputTypes: TypeAlias = Union[str]


@dataclass(frozen=True)
class ValueTransformer(ABC):
    """Class used to transform an input value."""

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
