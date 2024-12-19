import warnings

import pytest

from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource


class TestRegionResource:
    def test_serialise_no_warnings(self) -> None:
        region = RegionResource.create_new("res_id", "label", "region_of")
        region = region.add_rectangle((0.1, 0.1), (0.2, 0.2))
        with warnings.catch_warnings(record=True) as caught_warnings:
            region.serialise()
            assert len(caught_warnings) == 0

    def test_serialise_no_region(self) -> None:
        region = RegionResource.create_new("res_id", "label", "region_of")
        with warnings.catch_warnings(record=True) as caught_warnings:
            region.serialise()
            assert len(caught_warnings) == 1


class TestLinkResource:
    def test_serialise_no_warnings(self) -> None:
        linkobj = LinkResource.create_new("id", "lbl", ["link"]).add_comment("cmt")
        with warnings.catch_warnings(record=True) as caught_warnings:
            linkobj.serialise()
            assert len(caught_warnings) == 0

    def test_serialise_no_comment(self) -> None:
        linkobj = LinkResource.create_new("id", "lbl", ["link"])
        with warnings.catch_warnings(record=True) as caught_warnings:
            linkobj.serialise()
            assert len(caught_warnings) == 1

    def test_serialise_no_link(self) -> None:
        linkobj = LinkResource.create_new("id", "lbl", []).add_comment("cmt")
        with warnings.catch_warnings(record=True) as caught_warnings:
            linkobj.serialise()
            assert len(caught_warnings) == 1


if __name__ == "__main__":
    pytest.main([__file__])
