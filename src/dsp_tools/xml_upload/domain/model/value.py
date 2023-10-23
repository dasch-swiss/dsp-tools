from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class BooleanValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class ColorValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class DateValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class DecimalValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class GeometryValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class GeonamesValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class IntegerValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class IntervalValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class ListValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class LinkValue:  # resptr
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class UnformattedTextValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class FormattedTextValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class TimeValue:
    property_name: str
    value: str
    permissions: str | None = None


@dataclass(frozen=True)
class UriValue:
    property_name: str
    value: str
    permissions: str | None = None


# XXX: understand <link> element


Value = (
    BooleanValue
    | ColorValue
    | DateValue
    | DecimalValue
    | GeometryValue
    | GeonamesValue
    | IntegerValue
    | IntervalValue
    | ListValue
    | LinkValue
    | UnformattedTextValue
    | FormattedTextValue
    | TimeValue
    | UriValue
)
