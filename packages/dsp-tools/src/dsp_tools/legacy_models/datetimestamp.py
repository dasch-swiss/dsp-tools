from __future__ import annotations

from typing import Any
from typing import Union

import regex

from dsp_tools.error.exceptions import BaseError


class DateTimeStamp:
    """
    Class to hold and process an xsd:dateTimeStamp
    """

    _dateTimeStamp: str
    _validation_regex = (
        r"^-?([1-9][0-9]{3,}|0[0-9]{3})"
        r"-(0[1-9]|1[0-2])"
        r"-(0[1-9]|[12][0-9]|3[01])"
        r"T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))"
        r"(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))$"
    )

    def __init__(self, val: Any):
        """
        The constructor works for different inputs: a string, an instance of "DateTimeStamp",
        or a JSON-LD construct of the form { "@type": "xsd:dateTimeStamp", "@value": "date-str" }

        Args:
            val: xsd:dateTimeStamp as string, instance of "DateTimeStamp" or json-ld construct

        Raises:
            BaseError: if the JSON-LD construct is not correct
        """
        if isinstance(val, str):
            if not regex.search(self._validation_regex, val):
                raise BaseError(f"Invalid xsd:dateTimeStamp: '{val}'")
            self._dateTimeStamp = val
        elif isinstance(val, DateTimeStamp):
            self._dateTimeStamp = str(val)
        elif val.get("@type") == "xsd:dateTimeStamp" and regex.search(self._validation_regex, str(val.get("@value"))):
            self._dateTimeStamp = val["@value"]
        else:
            raise BaseError(f"Invalid xsd:dateTimeStamp: '{val}'")

    def __eq__(self, other: Union[str, DateTimeStamp]) -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp == other._dateTimeStamp

    def __lt__(self, other: DateTimeStamp) -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp < other._dateTimeStamp

    def __le__(self, other: DateTimeStamp) -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp <= other._dateTimeStamp

    def __gt__(self, other: DateTimeStamp) -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp > other._dateTimeStamp

    def __ge__(self, other: DateTimeStamp) -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp >= other._dateTimeStamp

    def __ne__(self, other: DateTimeStamp) -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp != other._dateTimeStamp

    def __str__(self: DateTimeStamp) -> str:
        return self._dateTimeStamp

    def toJsonObj(self) -> dict[str, str]:
        return {"@type": "xsd:dateTimeStamp", "@value": self._dateTimeStamp}
