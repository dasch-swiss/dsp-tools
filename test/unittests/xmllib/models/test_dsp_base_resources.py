import warnings

import pytest
from lxml import etree

from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource


@pytest.fixture
def region_no_warnings() -> RegionResource:
    region = RegionResource.create_new("res_id", "label", "region_of")
    return region.add_rectangle((0.1, 0.1), (0.2, 0.2))


@pytest.fixture
def link_obj_no_warnings() -> LinkResource:
    return LinkResource.create_new("id", "lbl", ["link"]).add_comment("cmt")


class TestRegionResource:
    def test_serialise_no_warnings(self, region_no_warnings: RegionResource) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            region_no_warnings.serialise()
            assert len(caught_warnings) == 0

    def test_serialised_string_no_warnings(self, region_no_warnings: RegionResource) -> None:
        serialised = etree.tostring(region_no_warnings.serialise())
        expected = (
            b'<region xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'label="label" id="res_id">'
            b'<geometry-prop name="hasGeometry">'
            b'<geometry>{"status": "active", "type": "rectangle", "lineWidth": 2, '
            b'"points": [{"x": 0.1, "y": 0.1}, {"x": 0.2, "y": 0.2}]}</geometry>'
            b"</geometry-prop>"
            b'<color-prop name="hasColor"><color>#5b24bf</color></color-prop>'
            b'<resptr-prop name="isRegionOf"><resptr>region_of</resptr></resptr-prop>'
            b"</region>"
        )
        assert serialised == expected

    def test_serialise_no_region(self) -> None:
        region = RegionResource.create_new("res_id", "label", "region_of")
        with warnings.catch_warnings(record=True) as caught_warnings:
            region.serialise()
            assert len(caught_warnings) == 1


class TestLinkResource:
    def test_serialise_no_warnings(self, link_obj_no_warnings: LinkResource) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            link_obj_no_warnings.serialise()
            assert len(caught_warnings) == 0

    def test_serialised_string_no_warnings(self, link_obj_no_warnings: RegionResource) -> None:
        serialised = etree.tostring(link_obj_no_warnings.serialise())
        expected = (
            b'<link xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'label="lbl" id="id">'
            b'<text-prop name="hasComment"><text encoding="xml">cmt</text></text-prop>'
            b'<resptr-prop name="hasLinkTo"><resptr>link</resptr></resptr-prop>'
            b"</link>"
        )
        assert serialised == expected

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
