from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import TypeAlias
from typing import Union
from typing import assert_never

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.models.exceptions import BaseError

InputTypes: TypeAlias = Union[str, FormattedTextValue]
OutputTypes: TypeAlias = Union[str]


@dataclass(frozen=True)
class ValueTransformer(ABC):
    """Class used to transform an input value."""

    @abstractmethod
    def transform(self, input_value: InputTypes) -> OutputTypes: ...

    @staticmethod
    def _assert_is_string(value: str | FormattedTextValue) -> str:
        match value:
            case str() as s:
                return s
            case FormattedTextValue() as xml:
                raise BaseError(f"Expected string value, but got XML value: {xml.as_xml()}")
            case _:
                assert_never(value)


class DecimalTransformer(ValueTransformer):
    def transform(self, input_value: Any) -> str:
        val = self._assert_is_string(input_value)
        return str(float(val))
