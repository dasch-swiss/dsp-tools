import pytest

from dsp_tools.utils.data_formats.geolocation_literal import CRS_IRI_BY_CODE
from dsp_tools.utils.data_formats.geolocation_literal import compose_geolocation_literal
from dsp_tools.utils.data_formats.geolocation_literal import compose_geolocation_literal_from_ordinates
from dsp_tools.utils.geolocation_constants import CRS_BY_CODE


def test_every_supported_crs_has_an_iri() -> None:
    assert set(CRS_IRI_BY_CODE) == set(CRS_BY_CODE)


class TestComposeLiteral:
    @pytest.mark.parametrize(
        ("crs_code", "expected_iri"),
        [
            ("CRS84", "http://www.opengis.net/def/crs/OGC/1.3/CRS84"),
            ("LV95", "http://www.opengis.net/def/crs/EPSG/0/2056"),
            ("LV03", "http://www.opengis.net/def/crs/EPSG/0/21781"),
        ],
    )
    def test_tags_the_given_crs(self, crs_code: str, expected_iri: str) -> None:
        assert compose_geolocation_literal(crs_code, "1", "2") == f"<{expected_iri}> POINT(1 2)"

    def test_keeps_the_submitted_decimal_precision(self) -> None:
        # 8.550 must not come back as 8.55: the ordinates are never re-serialised through a number
        assert compose_geolocation_literal("CRS84", "8.550", "47.370").endswith("POINT(8.550 47.370)")

    def test_from_ordinates_puts_x_first(self) -> None:
        literal = compose_geolocation_literal_from_ordinates("CRS84", {"latitude": "47.37", "longitude": "8.55"})
        assert literal == f"<{CRS_IRI_BY_CODE['CRS84']}> POINT(8.55 47.37)"

    def test_from_ordinates_puts_easting_first(self) -> None:
        literal = compose_geolocation_literal_from_ordinates("LV95", {"northing": "1200000", "easting": "2600000"})
        assert literal == f"<{CRS_IRI_BY_CODE['LV95']}> POINT(2600000 1200000)"

    def test_from_ordinates_with_an_incomplete_pair_is_none(self) -> None:
        assert compose_geolocation_literal_from_ordinates("CRS84", {"longitude": "8.55"}) is None

    def test_from_ordinates_with_the_wrong_pair_is_none(self) -> None:
        assert compose_geolocation_literal_from_ordinates("LV95", {"longitude": "8.55", "latitude": "47.37"}) is None

    def test_from_ordinates_with_an_unknown_crs_is_none(self) -> None:
        assert compose_geolocation_literal_from_ordinates("EPSG:4326", {"longitude": "8.55", "latitude": "1"}) is None
