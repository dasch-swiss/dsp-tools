from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering

import regex

from dsp_tools.error.exceptions import BaseError

VALIDATION_REGEX = (
    r"^-?([1-9][0-9]{3,}|0[0-9]{3})"
    r"-(0[1-9]|1[0-2])"
    r"-(0[1-9]|[12][0-9]|3[01])"
    r"T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))"
    r"(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))$"
)


@total_ordering
@dataclass(frozen=True)
class DateTimeStamp:
    """Holds a validated xsd:dateTimeStamp string."""

    value: str

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, DateTimeStamp):
            return self.value == other.value
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.value < other
        if isinstance(other, DateTimeStamp):
            return self.value < other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)


def create_date_time_stamp(val: str) -> DateTimeStamp:
    """Create a DateTimeStamp from a string, validating the format."""
    if not regex.search(VALIDATION_REGEX, val):
        raise BaseError(f"Invalid xsd:dateTimeStamp: '{val}'")
    return DateTimeStamp(value=val)
