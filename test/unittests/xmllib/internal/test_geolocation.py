import pytest

from dsp_tools.xmllib.internal.geolocation import CRS84
from dsp_tools.xmllib.internal.geolocation import LV03
from dsp_tools.xmllib.internal.geolocation import LV95
from dsp_tools.xmllib.internal.geolocation import compose_geolocation_literal
from dsp_tools.xmllib.internal.geolocation import get_geolocation_problem


class TestComposeLiteral:
    @pytest.mark.parametrize(
        ("crs_code", "expected_iri"),
        [("CRS84", CRS84.iri), ("LV95", LV95.iri), ("LV03", LV03.iri)],
    )
    def test_tags_the_given_crs(self, crs_code: str, expected_iri: str) -> None:
        assert compose_geolocation_literal(crs_code, "POINT(0 0)") == f"<{expected_iri}> POINT(0 0)"

    def test_an_absent_crs_becomes_crs84(self) -> None:
        assert compose_geolocation_literal(None, "POINT(8.55 47.37)") == f"<{CRS84.iri}> POINT(8.55 47.37)"

    def test_keeps_the_submitted_decimal_precision(self) -> None:
        # 8.550 must not come back as 8.55: the ordinates are never re-serialised through a number
        literal = compose_geolocation_literal("CRS84", "POINT(8.550 47.370)")
        assert literal.endswith("POINT(8.550 47.370)")


class TestBounds:
    @pytest.mark.parametrize(
        ("crs_code", "wkt"),
        [
            ("CRS84", "POINT(-180 -90)"),
            ("CRS84", "POINT(180 90)"),
            ("LV95", "POINT(2484273.3 1073150.16)"),
            ("LV95", "POINT(2837939.88 1299970.97)"),
            ("LV03", "POINT(484273.3 73150.16)"),
            ("LV03", "POINT(837939.88 299970.97)"),
        ],
    )
    def test_the_bounds_are_inclusive(self, crs_code: str, wkt: str) -> None:
        assert get_geolocation_problem(compose_geolocation_literal(crs_code, wkt)) is None

    def test_names_the_offending_ordinate_and_its_range(self) -> None:
        problem = get_geolocation_problem(compose_geolocation_literal("CRS84", "POINT(200 47.37)"))
        assert problem is not None
        assert "first ordinate '200'" in problem
        assert "longitude" in problem
        assert "-180…180" in problem

    def test_names_the_axis_by_the_name_the_crs_uses(self) -> None:
        # a projected system has eastings and northings, not longitude and latitude
        problem = get_geolocation_problem(compose_geolocation_literal("LV95", "POINT(0 1200000)"))
        assert problem is not None
        assert "easting" in problem
        assert "longitude" not in problem


class TestSwappedAxes:
    def test_hints_at_swapped_axes_when_the_transposed_pair_would_be_valid(self) -> None:
        problem = get_geolocation_problem(compose_geolocation_literal("LV95", "POINT(1200000 2600000)"))
        assert problem is not None
        assert "would be valid if transposed" in problem
        assert "easting first, then northing" in problem

    def test_stays_silent_when_transposing_would_not_help(self) -> None:
        problem = get_geolocation_problem(compose_geolocation_literal("CRS84", "POINT(200 300)"))
        assert problem is not None
        assert "transposed" not in problem

    def test_a_transposed_crs84_pair_within_90_degrees_is_undetectable(self) -> None:
        # Documented gap: 47.37 is a valid longitude and 8.55 a valid latitude, so nothing here or on
        # the server can tell this from a deliberate coordinate. Recorded so its absence is not read
        # as an oversight.
        assert get_geolocation_problem(compose_geolocation_literal("CRS84", "POINT(47.37 8.55)")) is None


class TestRejections:
    def test_epsg_4326_explains_itself(self) -> None:
        problem = get_geolocation_problem("<http://www.opengis.net/def/crs/EPSG/0/4326> POINT(47.37 8.55)")
        assert problem is not None
        assert "latitude before longitude" in problem
        assert CRS84.iri in problem

    def test_an_unknown_crs_lists_the_supported_ones(self) -> None:
        problem = get_geolocation_problem("<http://example.org/crs/1> POINT(0 0)")
        assert problem is not None
        assert LV95.iri in problem
        assert LV03.iri in problem

    @pytest.mark.parametrize(
        ("wkt", "expected"),
        [
            ("POINT(8.55, 47.37)", "single coordinate pair"),
            ("POINT(8.55 47.37 500)", "elevation is not yet supported"),
            ("POINT(8.55)", "ordinates"),
            ("POINT(abc 47.37)", "is not a number"),
            ("LINESTRING(0 0, 1 1)", "only a two-dimensional POINT"),
            ("POLYGON((0 0, 1 1, 1 0, 0 0))", "only a two-dimensional POINT"),
        ],
    )
    def test_says_what_is_wrong(self, wkt: str, expected: str) -> None:
        problem = get_geolocation_problem(compose_geolocation_literal("CRS84", wkt))
        assert problem is not None
        assert expected in problem


class TestUntaggedLiteral:
    def test_an_untagged_literal_is_read_as_crs84(self) -> None:
        # GeoSPARQL 1.1 §10.8 — and it must be bounds-checked as CRS84, not waved through
        assert get_geolocation_problem("POINT(8.55 47.37)") is None
        assert get_geolocation_problem("POINT(2600000 1200000)") is not None
