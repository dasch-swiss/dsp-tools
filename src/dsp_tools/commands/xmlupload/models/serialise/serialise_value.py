from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import TypeAlias
from typing import Union

from dsp_tools.utils.date_util import Date
from dsp_tools.utils.date_util import DayMonthYearEra
from dsp_tools.utils.date_util import SingleDate
from dsp_tools.utils.date_util import StartEnd

ValueTypes: TypeAlias = Union[str, Date, "Interval"]
ValueSerialiser: TypeAlias = Callable[[ValueTypes, str | None, str | None], "SerialiseValue"]


@dataclass(frozen=True)
class SerialiseProperty:
    property_name: str
    values: Sequence[SerialiseValue]

    def serialise(self) -> dict[str, Any]:
        """Serialise the property and all its values."""
        return {self.property_name: [value.serialise() for value in self.values]}


@dataclass(frozen=True)
class SerialiseValue(ABC):
    """A value to be serialised."""

    value: ValueTypes
    permissions: str | None
    comment: str | None

    @abstractmethod
    def serialise(self) -> dict[str, Any]:
        """Serialise the value."""

    def _get_optionals(self) -> dict[str, str]:
        optionals = {"knora-api:valueHasComment": self.comment} if self.comment else {}
        if self.permissions:
            optionals["knora-api:hasPermissions"] = self.permissions
        return optionals


class SerialiseDate(SerialiseValue):  # TODO
    """A DateValue to be serialised."""

    value: Date

    def serialise(self) -> dict[str, Any]:
        serialised = {"knora-api:dateValueHasCalendar": self.value.calendar.value} if self.value.calendar else {}
        serialised["@type"] = "knora-api:DateValue"
        serialised.update(self._get_one_date_dict(self.value.start, StartEnd.START))
        if self.value.end:
            serialised.update(self._get_one_date_dict(self.value.end, StartEnd.END))
        serialised.update(self._get_optionals())
        return serialised

    def _get_one_date_dict(self, date: SingleDate, start_end: StartEnd) -> dict[str, Any]:
        def get_prop(precision: DayMonthYearEra) -> str:
            return f"knora-api:dateValueHas{start_end.value}{precision.value}"

        date_dict: dict[str, Any] = {get_prop(DayMonthYearEra.YEAR): date.year} if date.year else {}
        if date.month:
            date_dict[get_prop(DayMonthYearEra.MONTH)] = date.month
        if date.day:
            date_dict[get_prop(DayMonthYearEra.DAY)] = date.day
        if date.era:
            date_dict[get_prop(DayMonthYearEra.ERA)] = date.era.value
        return date_dict


class SerialiseInterval(SerialiseValue):  # TODO
    """An IntervalValue to be serialised."""

    value: Interval

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:IntervalValue",
            "knora-api:intervalValueHasStart": self.value.interval_start(),
            "knora-api:intervalValueHasEnd": self.value.interval_end(),
        }
        serialised.update(self._get_optionals())
        return serialised


@dataclass
class Interval:  # TODO
    start: str
    end: str

    def interval_start(self) -> dict[str, str]:
        return self._to_dict(self.start)

    def interval_end(self) -> dict[str, str]:
        return self._to_dict(self.end)

    def _to_dict(self, interval_value: str) -> dict[str, str]:
        return {
            "@type": "xsd:decimal",
            "@value": interval_value,
        }


class SerialiseList(SerialiseValue):  # TODO
    """An ListValue to be serialised."""

    value: str

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:ListValue",
            "knora-api:listValueAsListNode": {
                "@id": self.value,
            },
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseLink(SerialiseValue):  # TODO
    """A LinkValue to be serialised."""

    value: str

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:LinkValue",
            "knora-api:linkValueHasTargetIri": {
                "@id": self.value,
            },
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseSimpletext(SerialiseValue):
    """A Simpletext to be serialised."""

    value: str

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:TextValue",
            "knora-api:valueAsString": self.value,
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseRichtext(SerialiseValue):
    """A Richtext to be serialised."""

    value: str

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:TextValue",
            "knora-api:textValueAsXml": self.value,
            "knora-api:textValueHasMapping": {
                "@id": "http://rdfh.ch/standoff/mappings/StandardMapping",
            },
        }
        serialised.update(self._get_optionals())
        return serialised
