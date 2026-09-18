"""
The coordinate reference systems a geolocation value may be tagged with, and the composition and
bounds-checking of geolocation literals.

This module is the single source for the CRS table. `validate-data` and `xmlupload` both import from
here so that a coordinate rejected locally and a coordinate rejected before upload are rejected by the
same numbers. dsp-api's `Geolocation.scala` is the authoritative table; this one mirrors it and is a
courtesy that fails fast, before any request is sent.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from decimal import InvalidOperation

import regex

# An optional CRS definition IRI in angle brackets, whitespace, then a WKT geometry.
_CRS_PREFIX_PATTERN = regex.compile(r"^<([^<>\s]*)>\s+(.*)$", regex.DOTALL)
_POINT_PATTERN = regex.compile(r"^POINT\s*\((.*)\)$", regex.IGNORECASE | regex.DOTALL)


@dataclass(frozen=True)
class Crs:
    """One coordinate reference system, with the bounds its ordinates must fall within."""

    code: str
    iri: str
    label: str
    x_name: str
    y_name: str
    x_min: Decimal
    x_max: Decimal
    y_min: Decimal
    y_max: Decimal


# Bounds are inclusive. The first ordinate is always X (longitude for geographic systems, easting for
# projected ones), the second always Y (latitude or northing).
CRS84 = Crs(
    code="CRS84",
    iri="http://www.opengis.net/def/crs/OGC/1.3/CRS84",
    label="WGS84 (CRS84)",
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
    x_name="easting",
    y_name="northing",
    x_min=Decimal("484273.3"),
    x_max=Decimal("837939.88"),
    y_min=Decimal("73150.16"),
    y_max=Decimal("299970.97"),
)

ALL_CRS: tuple[Crs, ...] = (CRS84, LV95, LV03)
CRS_BY_CODE: dict[str, Crs] = {crs.code: crs for crs in ALL_CRS}
CRS_BY_IRI: dict[str, Crs] = {crs.iri: crs for crs in ALL_CRS}

# The CRS an untagged literal is understood to be in, per GeoSPARQL 1.1 §10.8.
DEFAULT_CRS = CRS84

# WGS84 with latitude-first axis order. dsp-api rejects it in favour of CRS84, and the XML schema does
# not admit it, so it is named here only to explain itself when it turns up.
REJECTED_EPSG_4326 = "http://www.opengis.net/def/crs/EPSG/0/4326"


def compose_geolocation_literal(crs_code: str | None, wkt: str) -> str:
    """
    Compose the stored literal from a CRS code and a WKT geometry.

    The literal is always CRS-tagged, so that no stored value is ambiguous. An absent code means
    CRS84.

    Args:
        crs_code: one of the codes in `CRS_BY_CODE`, or None for the default
        wkt: the WKT geometry, e.g. `POINT(8.55 47.37)`

    Returns:
        the CRS-prefixed literal
    """
    crs = CRS_BY_CODE.get(crs_code, DEFAULT_CRS) if crs_code else DEFAULT_CRS
    return f"<{crs.iri}> {wkt.strip()}"


def get_geolocation_problem(literal: str) -> str | None:
    """
    Check a composed geolocation literal, and describe the first problem found.

    Returns a message rather than a bool because a coordinate can be wrong in ways the author needs
    told apart: an unsupported CRS, a geometry that is not yet accepted, or an out-of-range ordinate
    that is really a swapped axis.

    Args:
        literal: the CRS-prefixed literal, as `compose_geolocation_literal` produces it

    Returns:
        a message naming the problem, or None if the literal is valid
    """
    crs, geometry, unsupported_iri = _split_crs(literal.strip())
    if crs is None:
        return _unsupported_crs_message(unsupported_iri)
    point_match = _POINT_PATTERN.match(geometry)
    if not point_match:
        return (
            f"Unsupported geometry '{geometry}': only a two-dimensional POINT is accepted. "
            f"Lines, areas and elevations are not yet supported."
        )
    return _check_ordinates(crs, point_match.group(1).strip())


def _split_crs(literal: str) -> tuple[Crs | None, str, str]:
    """Split a literal into its CRS and geometry. An unrecognised CRS yields a None CRS and its IRI."""
    if match := _CRS_PREFIX_PATTERN.match(literal):
        iri, geometry = match.group(1), match.group(2).strip()
        return CRS_BY_IRI.get(iri), geometry, iri
    # An untagged literal is CRS84 by GeoSPARQL's default.
    return DEFAULT_CRS, literal, ""


def _unsupported_crs_message(iri: str) -> str:
    if iri == REJECTED_EPSG_4326:
        return (
            f"Unsupported coordinate reference system <{iri}>: it declares latitude before longitude. "
            f"Use <{CRS84.iri}> (CRS84) instead, which is WGS84 with longitude first, and give the "
            f"coordinates as longitude then latitude."
        )
    supported = ", ".join(f"<{crs.iri}>" for crs in ALL_CRS)
    return f"Unsupported coordinate reference system <{iri}>. Supported are: {supported}."


def _check_ordinates(crs: Crs, body: str) -> str | None:
    if "," in body:
        return "Malformed geolocation: a POINT carries a single coordinate pair, separated by whitespace."
    ordinates = body.split()
    if len(ordinates) != 2:
        return (
            f"Unsupported geometry: POINT carries {len(ordinates)} ordinates. Only a two-dimensional "
            f"POINT is accepted; an elevation is not yet supported."
        )
    x_str, y_str = ordinates
    x, y = _as_decimal(x_str), _as_decimal(y_str)
    if x is None or y is None:
        position, ordinate = ("first", x_str) if x is None else ("second", y_str)
        return f"Malformed geolocation: the {position} ordinate '{ordinate}' is not a number."
    return _check_bounds(crs, x_str, y_str, x, y)


def _check_bounds(crs: Crs, x_str: str, y_str: str, x: Decimal, y: Decimal) -> str | None:
    if not crs.x_min <= x <= crs.x_max:
        return _out_of_range_message(crs, "first", x_str, crs.x_name, crs.x_min, crs.x_max, x, y)
    if not crs.y_min <= y <= crs.y_max:
        return _out_of_range_message(crs, "second", y_str, crs.y_name, crs.y_min, crs.y_max, x, y)
    return None


def _out_of_range_message(
    crs: Crs,
    position: str,
    ordinate: str,
    axis_name: str,
    minimum: Decimal,
    maximum: Decimal,
    x: Decimal,
    y: Decimal,
) -> str:
    message = (
        f"The {position} ordinate '{ordinate}' is outside the valid {axis_name} range of "
        f"{crs.label} ({minimum}…{maximum})."
    )
    if _would_be_valid_transposed(crs, x, y):
        message += (
            f" The coordinates would be valid if transposed — {crs.label} takes {crs.x_name} first, then {crs.y_name}."
        )
    return message


def _would_be_valid_transposed(crs: Crs, x: Decimal, y: Decimal) -> bool:
    return crs.x_min <= y <= crs.x_max and crs.y_min <= x <= crs.y_max


def _as_decimal(value: str) -> Decimal | None:
    # The numeric parse, not a regex, is the authority on what is a number, so that a malformed
    # ordinate is a rejection rather than an escaping exception.
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError):
        return None
    return None if parsed.is_nan() or parsed.is_infinite() else parsed
