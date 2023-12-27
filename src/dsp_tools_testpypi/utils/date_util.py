from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import cast

import regex

from dsp_tools.models.exceptions import BaseError

_calendar = r"GREGORIAN|JULIAN|ISLAMIC"
_era = r"CE|BCE|BC|AD"
_year = r"\d{1,4}"
_month = r"\d{1,2}"
_day = r"\d{1,2}"
_full_date_pattern = rf"""
^
(?:({_calendar}):)?                         # optional calendar
(?:({_era}):)?                              # optional era
({_year}(?:-{_month})?(?:-{_day})?)         # date
(?::({_era}))?                              # optional era
(?::({_year}(?:-{_month})?(?:-{_day})?))?   # optional date
$
"""
_single_date_pattern = rf"^({_year})(?:-({_month}))?(?:-({_day}))?$"


class Calendar(Enum):
    """Enum for calendar types."""

    GREGORIAN = "GREGORIAN"
    ISLAMIC = "ISLAMIC"
    JULIAN = "JULIAN"

    @staticmethod
    def from_string(s: str) -> Calendar:
        """Parses a string into a calendar type, potentially failing with a BaseError."""
        match s:
            case "GREGORIAN":
                return Calendar.GREGORIAN
            case "ISLAMIC":
                return Calendar.ISLAMIC
            case "JULIAN":
                return Calendar.JULIAN
            case _:
                raise BaseError(f"Invalid calendar type: {s}")


class Era(Enum):
    """Enum for era types."""

    AD = "AD"
    BC = "BC"
    BCE = "BCE"
    CE = "CE"

    @staticmethod
    def from_string(s: str) -> Era:
        """Parses a string into an era type, potentially failing with a BaseError."""
        match s:
            case "AD":
                return Era.AD
            case "BC":
                return Era.BC
            case "BCE":
                return Era.BCE
            case "CE":
                return Era.CE
            case _:
                raise BaseError(f"Invalid era type: {s}")


@dataclass(frozen=True)
class SingleDate:
    """Information about a single date."""

    era: Era | None
    year: int
    month: int | None
    day: int | None


@dataclass(frozen=True)
class Date:
    """Information about a date."""

    calendar: Calendar
    start: SingleDate
    end: SingleDate | None


def parse_date_string(s: str) -> Date:
    """Parse a date string into a Date object.

    Args:
        s: date string

    Returns:
        Date object

    Raises:
        BaseError: if the date string cannot be parsed
    """

    calendar, start_era, start_date, end_era, end_date = _split_date_string(s)
    calendar_enum = Calendar.from_string(calendar or "GREGORIAN")
    if not end_date:
        end_date = start_date
    if calendar_enum != Calendar.ISLAMIC:
        if not start_era:
            start_era = "CE"
        if end_date and not end_era:
            end_era = start_era
    start_era_enum = Era.from_string(start_era) if start_era else None
    end_era_enum = Era.from_string(end_era) if end_era else None
    start = _parse_single_date(start_date, start_era_enum)
    end = _parse_single_date(end_date, end_era_enum) if end_date else None

    return Date(calendar_enum, start, end)


def is_full_date(s: str) -> bool:
    """
    Check if a string is a full DSP date string of the scheme calendar:epoch:yyyy-mm-dd:epoch:yyyy-mm-dd.
    """
    return bool(regex.search(_full_date_pattern, s, flags=regex.VERBOSE))


def _split_date_string(s: str) -> tuple[str | None, str | None, str, str | None, str | None]:
    date_match = regex.search(_full_date_pattern, s, flags=regex.VERBOSE)
    if not date_match:
        raise BaseError(f"Could not parse date: {s}")
    date_groups = date_match.groups()
    match date_groups:
        case ("ISLAMIC", start_era, _, end_era, _) if start_era or end_era:
            raise BaseError(f"ISLAMIC calendar does not support eras: {s}")
        case (str() | None, str() | None, str(), str() | None, str() | None):
            return cast(tuple[str | None, str | None, str, str | None, str | None], date_groups)
        case _:
            raise BaseError(f"Could not parse date: {s}")


def _parse_single_date(date: str, era: Era | None) -> SingleDate:
    date_match = regex.search(_single_date_pattern, date)
    if not date_match:
        raise BaseError(f"Could not parse date: {date}")
    match date_match.groups():
        case (str() as year, str() | None as month, str() | None as day):
            y = int(year)
            m = int(month) if month else None
            d = int(day) if day else None
            return SingleDate(era, y, m, d)
        case _:
            raise BaseError(f"Could not parse date: {date}")
