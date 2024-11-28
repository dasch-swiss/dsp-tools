import warnings

import pytest

from dsp_tools.xmllib.models.dsp_base_resources import RegionResource


class TestRegion:
    def test_serialise_no_warnings(self) -> None:
        region = RegionResource.create_new("res_id", "label", "region_of", ["comment"])
        region = region.add_rectangle((0.1, 0.1), (0.2, 0.2))
        with warnings.catch_warnings(record=True) as caught_warnings:
            region.serialise()
            assert len(caught_warnings) == 0

    def test_serialise_no_comment(self) -> None:
        region = RegionResource.create_new("res_id", "label", "region_of", [])
        region = region.add_rectangle((0.1, 0.1), (0.2, 0.2))
        with warnings.catch_warnings(record=True) as caught_warnings:
            region.serialise()
            assert len(caught_warnings) == 1

    def test_serialise_no_region(self) -> None:
        region = RegionResource.create_new("res_id", "label", "region_of", ["comment"])
        with warnings.catch_warnings(record=True) as caught_warnings:
            region.serialise()
            assert len(caught_warnings) == 1


if __name__ == "__main__":
    pytest.main([__file__])
