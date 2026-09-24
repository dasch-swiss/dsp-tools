from decimal import Decimal

import numpy as np
import pytest

from dsp_tools.xmllib.internal.geolocation import CRS84
from dsp_tools.xmllib.internal.geolocation import LV03
from dsp_tools.xmllib.internal.geolocation import LV95
from dsp_tools.xmllib.internal.geolocation import compose_geolocation_literal
from dsp_tools.xmllib.internal.geolocation import compose_geolocation_literal_from_ordinates
from dsp_tools.xmllib.internal.geolocation import get_geolocation_problem
from dsp_tools.xmllib.internal.geolocation import ordinate_to_str


class TestComposeLiteral:
    @pytest.mark.parametrize(
        ("crs_code", "expected_iri"),
        [("CRS84", CRS84.iri), ("LV95", LV95.iri), ("LV03", LV03.iri)],
    )
    def test_tags_the_given_crs(self, crs_code: str, expected_iri: str) -> None:
        assert compose_geolocation_literal(crs_code, "1", "2") == f"<{expected_iri}> POINT(1 2)"

    def test_keeps_the_submitted_decimal_precision(self) -> None:
        # 8.550 must not come back as 8.55: the ordinates are never re-serialised through a number
        assert compose_geolocation_literal("CRS84", "8.550", "47.370").endswith("POINT(8.550 47.370)")

    def test_from_ordinates_puts_x_first(self) -> None:
        literal = compose_geolocation_literal_from_ordinates("CRS84", {"latitude": "47.37", "longitude": "8.55"})
        assert literal == f"<{CRS84.iri}> POINT(8.55 47.37)"

    def test_from_ordinates_puts_easting_first(self) -> None:
        literal = compose_geolocation_literal_from_ordinates("LV95", {"northing": "1200000", "easting": "2600000"})
        assert literal == f"<{LV95.iri}> POINT(2600000 1200000)"

    def test_from_ordinates_with_an_incomplete_pair_is_none(self) -> None:
        assert compose_geolocation_literal_from_ordinates("CRS84", {"longitude": "8.55"}) is None

    def test_from_ordinates_with_the_wrong_pair_is_none(self) -> None:
        assert compose_geolocation_literal_from_ordinates("LV95", {"longitude": "8.55", "latitude": "47.37"}) is None

    def test_from_ordinates_with_an_unknown_crs_is_none(self) -> None:
        assert compose_geolocation_literal_from_ordinates("EPSG:4326", {"longitude": "8.55", "latitude": "1"}) is None


class TestBounds:
    @pytest.mark.parametrize(
        ("crs_code", "ordinates"),
        [
            ("CRS84", {"longitude": "-180", "latitude": "-90"}),
            ("CRS84", {"longitude": "180", "latitude": "90"}),
            ("LV95", {"easting": "2484273.3", "northing": "1073150.16"}),
            ("LV95", {"easting": "2837939.88", "northing": "1299970.97"}),
            ("LV03", {"easting": "484273.3", "northing": "73150.16"}),
            ("LV03", {"easting": "837939.88", "northing": "299970.97"}),
        ],
    )
    def test_the_bounds_are_inclusive(self, crs_code: str, ordinates: dict[str, str]) -> None:
        assert get_geolocation_problem(crs_code, ordinates) is None

    @pytest.mark.parametrize(
        ("crs_code", "ordinates", "name"),
        [
            ("CRS84", {"longitude": "-180.001", "latitude": "0"}, "longitude"),
            ("CRS84", {"longitude": "180.001", "latitude": "0"}, "longitude"),
            ("CRS84", {"longitude": "0", "latitude": "-90.001"}, "latitude"),
            ("CRS84", {"longitude": "0", "latitude": "90.001"}, "latitude"),
            ("LV95", {"easting": "2484273.2", "northing": "1200000"}, "easting"),
            ("LV95", {"easting": "2600000", "northing": "1299970.98"}, "northing"),
            ("LV03", {"easting": "837939.89", "northing": "200000"}, "easting"),
            ("LV03", {"easting": "600000", "northing": "73150.15"}, "northing"),
        ],
    )
    def test_just_outside_the_bounds_is_rejected(self, crs_code: str, ordinates: dict[str, str], name: str) -> None:
        problem = get_geolocation_problem(crs_code, ordinates)
        assert problem is not None
        assert f"The {name} '{ordinates[name]}'" in problem

    def test_names_the_attribute_its_range_and_its_crs(self) -> None:
        problem = get_geolocation_problem("CRS84", {"longitude": "200", "latitude": "47.37"})
        assert problem == "The longitude '200' is outside the valid range for WGS84 (CRS84): -180 to 180 inclusive."

    def test_negative_zero_is_zero(self) -> None:
        assert get_geolocation_problem("CRS84", {"longitude": "-0.0", "latitude": "0"}) is None

    @pytest.mark.parametrize(
        "ordinate", ["abc", "8,55", "1e5", "", "NaN", "Infinity", "\u0668.\u0665\u0665", "\uff18.\uff15\uff15"]
    )
    def test_a_non_decimal_ordinate_is_rejected(self, ordinate: str) -> None:
        problem = get_geolocation_problem("CRS84", {"longitude": ordinate, "latitude": "47.37"})
        assert problem is not None
        assert "is not a decimal number" in problem


class TestPair:
    def test_a_geographic_pair_with_a_projected_crs(self) -> None:
        problem = get_geolocation_problem("LV95", {"longitude": "8.55", "latitude": "47.37"})
        assert problem == (
            "Given crs=\"LV95\", expected the attributes 'easting' and 'northing'. "
            "Found 'longitude' and 'latitude', which belong to a geographic CRS."
        )

    def test_a_projected_pair_with_a_geographic_crs(self) -> None:
        problem = get_geolocation_problem("CRS84", {"easting": "2600000", "northing": "1200000"})
        assert problem == (
            "Given crs=\"CRS84\", expected the attributes 'longitude' and 'latitude'. "
            "Found 'easting' and 'northing', which belong to a projected CRS."
        )

    def test_a_mixed_pair(self) -> None:
        problem = get_geolocation_problem("CRS84", {"longitude": "8.55", "northing": "1200000"})
        assert problem == (
            "Given crs=\"CRS84\", expected the attributes 'longitude' and 'latitude'. Found 'northing', "
            "which belongs to a projected CRS."
        )

    def test_one_ordinate_missing(self) -> None:
        problem = get_geolocation_problem("CRS84", {"longitude": "8.55"})
        assert problem == "Given crs=\"CRS84\", expected both 'longitude' and 'latitude'. 'latitude' is missing."

    def test_both_ordinates_missing(self) -> None:
        problem = get_geolocation_problem("LV03", {})
        assert problem == "Given crs=\"LV03\", expected both 'easting' and 'northing'. Both are missing."

    def test_an_unknown_crs_lists_the_supported_ones(self) -> None:
        problem = get_geolocation_problem("EPSG:4326", {"longitude": "8.55", "latitude": "47.37"})
        assert problem == "Unsupported coordinate reference system 'EPSG:4326'. Supported are: 'CRS84', 'LV95', 'LV03'."


class TestOrdinateToStr:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("8.550", "8.550"),
            (" 8.55 ", "8.55"),
            (8.55, "8.55"),
            (2600000, "2600000"),
            (0.00001, "0.00001"),
            (2600000.0, "2600000.0"),
            (Decimal("0.0000001"), "0.0000001"),
            (np.float64(8.55), "8.55"),
            (np.float64(0.00001), "0.00001"),
        ],
    )
    def test_converts_without_exponent_and_keeps_strings(
        self, value: str | float | int | Decimal | np.float64, expected: str
    ) -> None:
        assert ordinate_to_str(value) == expected
