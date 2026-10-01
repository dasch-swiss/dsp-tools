"""
The coordinate reference systems a geolocation value may be given in, and the composition and checking
of geolocation values.

This module is the single source for the CRS table. `xmllib`, `validate-data` and `xmlupload` all import
from here so that a coordinate is accepted or rejected by the same numbers everywhere. dsp-api's
`Geolocation.scala` is the authoritative table; this one mirrors it and is a courtesy that fails fast,
before any request is sent.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any

import regex

# The same form the XML schema admits: a plain decimal, no exponent, no thousands separator.
_DECIMAL_ORDINATE_PATTERN = regex.compile(r"^[+-]?[0-9]+(\.[0-9]+)?$")


class CrsKind(StrEnum):
    GEOGRAPHIC = "geographic"
    PROJECTED = "projected"


@dataclass(frozen=True)
class Crs:
    """One coordinate reference system, with the names and bounds of its ordinates."""

    code: str
    iri: str
    label: str
    kind: CrsKind
    x_name: str
    y_name: str
    x_min: Decimal
    x_max: Decimal
    y_min: Decimal
    y_max: Decimal


# Bounds are inclusive. X is longitude for geographic systems and easting for projected ones,
# Y is latitude or northing. The names are also the XML attribute names of the ordinates.
CRS84 = Crs(
    code="CRS84",
    iri="http://www.opengis.net/def/crs/OGC/1.3/CRS84",
    label="WGS84 (CRS84)",
    kind=CrsKind.GEOGRAPHIC,
    x_name="longitude",
    y_name="latitude",
    x_min=Decimal("-180"),
    x_max=Decimal("180"),
    y_min=Decimal("-90"),
    y_max=Decimal("90"),
)
LV95 = Crs(
    code="LV95",
    iri="http://www.opengis.net/def/crs/EPSG/0/2056",
    label="Swiss LV95",
    kind=CrsKind.PROJECTED,
    x_name="easting",
    y_name="northing",
    x_min=Decimal("2484273.3"),
    x_max=Decimal("2837939.88"),
    y_min=Decimal("1073150.16"),
    y_max=Decimal("1299970.97"),
)
LV03 = Crs(
    code="LV03",
    iri="http://www.opengis.net/def/crs/EPSG/0/21781",
    label="Swiss LV03",
    kind=CrsKind.PROJECTED,
    x_name="easting",
    y_name="northing",
    x_min=Decimal("484273.3"),
    x_max=Decimal("837939.88"),
    y_min=Decimal("73150.16"),
    y_max=Decimal("299970.97"),
)

ALL_CRS: tuple[Crs, ...] = (CRS84, LV95, LV03)
CRS_BY_CODE: dict[str, Crs] = {crs.code: crs for crs in ALL_CRS}
ORDINATE_NAMES: tuple[str, ...] = tuple(dict.fromkeys(name for crs in ALL_CRS for name in (crs.x_name, crs.y_name)))


def ordinate_to_str(value: Any) -> str:
    """
    Convert an ordinate to the string that is written to the XML.

    Floats are written without an exponent, because the XML schema admits plain decimals only.
    Strings are kept as they are, so that trailing zeroes survive.
    """
    if isinstance(value, float):
        # float() first: a numpy float is a float subclass whose repr is e.g. "np.float64(8.55)"
        return format(Decimal(repr(float(value))), "f")
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value).strip()


def compose_geolocation_literal(crs_code: str, x: str, y: str) -> str:
    """
    Compose the stored literal from a CRS code and its two ordinates.

    This is the only place that knows the literal's form: the CRS IRI, then a WKT point with X first.
    The ordinates are inserted verbatim, so that their precision is preserved.

    Args:
        crs_code: one of the codes in `CRS_BY_CODE`
        x: longitude or easting
        y: latitude or northing

    Returns:
        the CRS-prefixed literal, e.g. `<http://www.opengis.net/def/crs/OGC/1.3/CRS84> POINT(8.55 47.37)`
    """
    return f"<{CRS_BY_CODE[crs_code].iri}> POINT({x.strip()} {y.strip()})"


def compose_geolocation_literal_from_ordinates(crs_code: str, ordinates: Mapping[str, str]) -> str | None:
    """
    Compose the stored literal from a CRS code and named ordinates.

    Args:
        crs_code: the CRS code
        ordinates: the ordinates, keyed by their names, e.g. `{"longitude": "8.55", "latitude": "47.37"}`

    Returns:
        the literal, or None if the CRS is unknown or its pair of ordinates is incomplete
    """
    if not (crs := CRS_BY_CODE.get(crs_code)):
        return None
    x, y = ordinates.get(crs.x_name), ordinates.get(crs.y_name)
    if x is None or y is None:
        return None
    return compose_geolocation_literal(crs_code, x, y)


def get_geolocation_problem(crs_code: str, ordinates: Mapping[str, str]) -> str | None:
    """
    Check a CRS code and its named ordinates, and describe the first problem found.

    Returns a message rather than a bool because an author needs to know which of several things is wrong:
    an unsupported CRS, ordinates that do not belong to the CRS, a missing ordinate, or one out of range.

    Args:
        crs_code: the CRS code
        ordinates: the ordinates, keyed by their names, e.g. `{"easting": "2600000", "northing": "1200000"}`

    Returns:
        a message naming the problem, or None if the value is valid
    """
    if not (crs := CRS_BY_CODE.get(crs_code)):
        supported = ", ".join(f"'{x.code}'" for x in ALL_CRS)
        return f"Unsupported coordinate reference system '{crs_code}'. Supported are: {supported}."
    if pair_problem := _get_pair_problem(crs, ordinates):
        return pair_problem
    if x_problem := _get_ordinate_problem(crs, crs.x_name, ordinates[crs.x_name], crs.x_min, crs.x_max):
        return x_problem
    return _get_ordinate_problem(crs, crs.y_name, ordinates[crs.y_name], crs.y_min, crs.y_max)


def _get_pair_problem(crs: Crs, ordinates: Mapping[str, str]) -> str | None:
    expected = (crs.x_name, crs.y_name)
    if foreign := [name for name in ordinates if name not in expected]:
        found = " and ".join(f"'{name}'" for name in foreign)
        msg = f"Given crs=\"{crs.code}\", expected the attributes '{crs.x_name}' and '{crs.y_name}'. Found {found}"
        if foreign_kinds := {x.kind for x in ALL_CRS if set(foreign) <= {x.x_name, x.y_name}} - {crs.kind}:
            belong = "belongs" if len(foreign) == 1 else "belong"
            msg += f", which {belong} to a {foreign_kinds.pop()} CRS"
        return msg + "."
    if missing := [name for name in expected if name not in ordinates]:
        missing_str = "both are missing" if len(missing) == 2 else f"'{missing[0]}' is missing"
        return (
            f"Given crs=\"{crs.code}\", expected both '{crs.x_name}' and '{crs.y_name}'. "
            f"{missing_str[0].upper()}{missing_str[1:]}."
        )
    return None


def _get_ordinate_problem(crs: Crs, name: str, ordinate: str, minimum: Decimal, maximum: Decimal) -> str | None:
    if not _DECIMAL_ORDINATE_PATTERN.match(ordinate.strip()):
        return f"The {name} '{ordinate}' is not a decimal number, e.g. '8.55'."
    value = Decimal(ordinate.strip())
    if not minimum <= value <= maximum:
        return f"The {name} '{ordinate}' is outside the valid range for {crs.label}: {minimum} to {maximum} inclusive."
    return None
