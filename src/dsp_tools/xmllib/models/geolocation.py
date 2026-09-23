from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class GeographicCoordinates:
    """
    A pair of coordinates in a geographic coordinate reference system, such as `CRS84`.

    The arguments must be named, so that longitude and latitude cannot be swapped by accident.
    Pass them as strings to preserve their decimal precision: a float drops trailing zeroes.

    Args:
        longitude: the east-west coordinate
        latitude: the north-south coordinate

    Examples:
        ```python
        coordinates = xmllib.GeographicCoordinates(longitude="8.550", latitude="47.37")
        ```
    """

    longitude: str | float | int
    latitude: str | float | int


@dataclass(frozen=True, kw_only=True)
class ProjectedCoordinates:
    """
    A pair of coordinates in a projected coordinate reference system, such as `LV95` or `LV03`.

    The arguments must be named, so that easting and northing cannot be swapped by accident.

    Args:
        easting: the east-west coordinate
        northing: the north-south coordinate

    Examples:
        ```python
        coordinates = xmllib.ProjectedCoordinates(easting="2600000", northing="1200000")
        ```
    """

    easting: str | float | int
    northing: str | float | int
