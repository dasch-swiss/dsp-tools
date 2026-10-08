"""
The coordinate reference systems a geolocation value may be given in.

This module is the single source for the CRS table. `xmllib`, `validate-data` and `xmlupload` all import
from here so that a coordinate is accepted or rejected by the same numbers everywhere.
dsp-api's `Geolocation.scala` is the authoritative table; this one mirrors it and is a courtesy that fails fast,
before any request is sent.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CrsKind(StrEnum):
    GEOGRAPHIC = "geographic"
    PROJECTED = "projected"


@dataclass(frozen=True)
class Crs:
    """One coordinate reference system, with the names and bounds of its ordinates."""

    code: str
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
