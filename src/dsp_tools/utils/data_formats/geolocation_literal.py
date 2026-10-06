"""
The composition of the geolocation literal that is sent to dsp-api.

This module is used by `xmlupload` and `validate-data`, never by `xmllib`.
"""

from __future__ import annotations

from collections.abc import Mapping

from dsp_tools.utils.geolocation_constants import CRS_BY_CODE

CRS_IRI_BY_CODE: dict[str, str] = {
    "CRS84": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
    "LV95": "http://www.opengis.net/def/crs/EPSG/0/2056",
    "LV03": "http://www.opengis.net/def/crs/EPSG/0/21781",
}


def compose_geolocation_literal(crs_code: str, x: str, y: str) -> str:
    """
    Compose the stored literal from a CRS code and its two ordinates.

    This is the only place that knows the literal's form: the CRS IRI, then a WKT point with X first.
    The ordinates are inserted verbatim, so that their precision is preserved.

    Args:
        crs_code: one of the codes in `CRS_IRI_BY_CODE`
        x: longitude or easting
        y: latitude or northing

    Returns:
        the CRS-prefixed literal, e.g. `<http://www.opengis.net/def/crs/OGC/1.3/CRS84> POINT(8.55 47.37)`
    """
    return f"<{CRS_IRI_BY_CODE[crs_code]}> POINT({x.strip()} {y.strip()})"


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
