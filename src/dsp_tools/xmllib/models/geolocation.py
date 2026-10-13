from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any

from dsp_tools.xmllib.models.internal.geolocation import CoordinateSystem


class GeolocationCoordinates(ABC):
    @classmethod
    def to_tuple(cls) -> tuple[dict[str, Any], CoordinateSystem]: ...


@dataclass
class GeographicCRS84(GeolocationCoordinates):
    longitude: Any
    latitude: Any

    @classmethod
    def create_new(cls, longitude: Any, latitude: Any) -> GeolocationCoordinates:
        return cls(longitude=longitude, latitude=latitude)

    @classmethod
    def to_tuple(cls) -> tuple[dict[str, Any], CoordinateSystem]:
        return {"longitude": cls.longitude, "latitude": cls.latitude}, CoordinateSystem.GEOGRAPHIC_CRS84


@dataclass
class ProjectedLV95(GeolocationCoordinates):
    easting: Any
    northing: Any

    @classmethod
    def create_new(cls, easting: float | int | None, northing: Any) -> GeolocationCoordinates:
        return cls(easting=easting, northing=northing)

    @classmethod
    def to_tuple(cls) -> tuple[dict[str, Any], CoordinateSystem]:
        return {"easting": cls.easting, "northing": cls.northing}, CoordinateSystem.PROJECTED_LV95


@dataclass
class ProjectedLV03(GeolocationCoordinates):
    easting: Any
    northing: Any

    @classmethod
    def create_new(cls, easting: float | int | None, northing: Any) -> GeolocationCoordinates:
        return cls(easting=easting, northing=northing)

    @classmethod
    def to_tuple(cls) -> tuple[dict[str, Any], CoordinateSystem]:
        return {"easting": cls.easting, "northing": cls.northing}, CoordinateSystem.PROJECTED_LV03


# TODO: test, implement as value in add_geolocation functions, remove crs coordinate system enum from public models

# TODO: is this the best implementation, because in optional we need to accept empty input. while we would like to have it typed cleanly

# TODO: add to conventions.md that in the xmllib res.add_[value] methods, should be one method per GuiAttribute in the ontology or if the xml tag is different (like iiif-uri vs. bitstream), so that a mapping can be done easily. If the content cannot be expressed a patter like the Geolocation can be used, it must still be user friendly.
