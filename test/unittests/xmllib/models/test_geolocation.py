from typing import Any

import pytest

from dsp_tools.xmllib.models.geolocation import GeographicCRS84
from dsp_tools.xmllib.models.geolocation import GeolocationCoordinates
from dsp_tools.xmllib.models.geolocation import ProjectedLV03
from dsp_tools.xmllib.models.geolocation import ProjectedLV95
from dsp_tools.xmllib.models.internal.geolocation import CoordinateSystem


@pytest.mark.parametrize(
    ("coordinates", "expected_ordinates", "expected_crs"),
    [
        (
            GeographicCRS84.create_new(longitude="8.55", latitude=47.37),
            {"longitude": "8.55", "latitude": 47.37},
            CoordinateSystem.GEOGRAPHIC_CRS84,
        ),
        (
            ProjectedLV95.create_new(easting=2600000, northing="1200000"),
            {"easting": 2600000, "northing": "1200000"},
            CoordinateSystem.PROJECTED_LV95,
        ),
        (
            ProjectedLV03.create_new(easting="600000", northing="200000"),
            {"easting": "600000", "northing": "200000"},
            CoordinateSystem.PROJECTED_LV03,
        ),
    ],
)
def test_to_tuple(
    coordinates: GeolocationCoordinates, expected_ordinates: dict[str, Any], expected_crs: CoordinateSystem
) -> None:
    assert coordinates.to_tuple() == (expected_ordinates, expected_crs)


def test_create_new_returns_the_concrete_class() -> None:
    assert isinstance(ProjectedLV95.create_new(easting="2600000", northing="1200000"), ProjectedLV95)


def test_create_new_accepts_empty_coordinates() -> None:
    coordinates = GeographicCRS84.create_new(longitude=None, latitude="")
    assert coordinates.to_tuple() == ({"longitude": None, "latitude": ""}, CoordinateSystem.GEOGRAPHIC_CRS84)


def test_the_base_class_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        GeolocationCoordinates()  # type: ignore[abstract]
