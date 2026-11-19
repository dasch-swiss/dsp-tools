from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from dsp_tools.xmllib.models.internal.geolocation import CoordinateSystem


class GeolocationCoordinates(ABC):
    """
    The coordinates of a geographic location, in one coordinate reference system.
    Use one of the subclasses: `GeographicCRS84`, `ProjectedLV95` or `ProjectedLV03`.
    """

    @abstractmethod
    def to_tuple(self) -> tuple[dict[str, Any], CoordinateSystem]:
        """Returns the coordinates by their XML attribute name, and the coordinate reference system."""


@dataclass(frozen=True, kw_only=True)
class GeographicCRS84(GeolocationCoordinates):
    """
    Coordinates in WGS84, with the longitude first (CRS84).

    Attributes:
        longitude: between -180 and 180
        latitude: between -90 and 90

    Examples:
        ```python
        coordinates = xmllib.GeographicCRS84.create_new(longitude="8.550", latitude="47.37")
        ```
    """

    longitude: Any
    latitude: Any

    @classmethod
    def create_new(cls, *, longitude: Any, latitude: Any) -> GeographicCRS84:
        """
        Creates new coordinates in CRS84.
        Pass the coordinates as strings to preserve their decimal precision: a float drops trailing zeroes.

        Args:
            longitude: the longitude, between -180 and 180
            latitude: the latitude, between -90 and 90

        Returns:
            The coordinates
        """
        return cls(longitude=longitude, latitude=latitude)

    def to_tuple(self) -> tuple[dict[str, Any], CoordinateSystem]:
        return {"longitude": self.longitude, "latitude": self.latitude}, CoordinateSystem.GEOGRAPHIC_CRS84


@dataclass(frozen=True, kw_only=True)
class ProjectedLV95(GeolocationCoordinates):
    """
    Coordinates in the Swiss coordinate system LV95.

    Attributes:
        easting: between 2484273.3 and 2837939.88
        northing: between 1073150.16 and 1299970.97

    Examples:
        ```python
        coordinates = xmllib.ProjectedLV95.create_new(easting="2600000", northing="1200000")
        ```
    """

    easting: Any
    northing: Any

    @classmethod
    def create_new(cls, *, easting: Any, northing: Any) -> ProjectedLV95:
        """
        Creates new coordinates in LV95.
        Pass the coordinates as strings to preserve their decimal precision: a float drops trailing zeroes.

        Args:
            easting: the easting
            northing: the northing

        Returns:
            The coordinates
        """
        return cls(easting=easting, northing=northing)

    def to_tuple(self) -> tuple[dict[str, Any], CoordinateSystem]:
        return {"easting": self.easting, "northing": self.northing}, CoordinateSystem.PROJECTED_LV95


@dataclass(frozen=True, kw_only=True)
class ProjectedLV03(GeolocationCoordinates):
    """
    Coordinates in the old Swiss coordinate system LV03.

    Attributes:
        easting: between 484273.3 and 837939.88
        northing: between 73150.16 and 299970.97

    Examples:
        ```python
        coordinates = xmllib.ProjectedLV03.create_new(easting="600000", northing="200000")
        ```
    """

    easting: Any
    northing: Any

    @classmethod
    def create_new(cls, *, easting: Any, northing: Any) -> ProjectedLV03:
        """
        Creates new coordinates in LV03.
        Pass the coordinates as strings to preserve their decimal precision: a float drops trailing zeroes.

        Args:
            easting: the easting
            northing: the northing

        Returns:
            The coordinates
        """
        return cls(easting=easting, northing=northing)

    def to_tuple(self) -> tuple[dict[str, Any], CoordinateSystem]:
        return {"easting": self.easting, "northing": self.northing}, CoordinateSystem.PROJECTED_LV03
