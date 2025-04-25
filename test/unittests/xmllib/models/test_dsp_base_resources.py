# mypy: disable-error-code="method-assign,no-untyped-def"

import warnings

import pytest
import regex

from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib import VideoSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import SegmentBounds
from dsp_tools.xmllib.models.dsp_base_resources import _check_strings

# The warning matches are constructed so that the line number is not checked as that is prone to change.


class TestRegionResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            RegionResource.create_new("id", "lbl", "regionOfId")
        assert len(caught_warnings) == 0

    def test_warns(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            RegionResource.create_new("", "", "")
        assert len(caught_warnings) == 3


class TestLinkResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            LinkResource.create_new("id", "lbl", ["link_to"])
        assert len(caught_warnings) == 0

    def test_warns(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            LinkResource.create_new("", "", [])
        assert len(caught_warnings) == 0


def test_segment_bounds():
    expected = regex.escape(
        " | Resource ID 'res_id' | Segment bounds must be a float or integer. "
        "The following places have an unexpected type: \n"
        "    - Segment Start Value: string | Type: <class 'str'>"
    )
    with pytest.warns(XmllibInputWarning, match=expected):
        SegmentBounds("string", "1", "res_id")


class TestVideoSegmentResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            VideoSegmentResource.create_new("id", "lbl", "segment_of", "0", "1")
        assert len(caught_warnings) == 0

    def test_warns_strings(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            VideoSegmentResource.create_new("", "", "", "0", "1")
        assert len(caught_warnings) == 3

    def test_warns_segment_bounds(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            VideoSegmentResource.create_new("id", "lbl", "segment_of", "", "")
        assert len(caught_warnings) == 2


class TestAudioSegmentResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            AudioSegmentResource.create_new("id", "lbl", "segment_of", "0", "1")
        assert len(caught_warnings) == 0

    def test_warns_strings(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            AudioSegmentResource.create_new("", "", "", "0", "1")
        assert len(caught_warnings) == 3

    def test_warns_segment_bounds(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            AudioSegmentResource.create_new("id", "lbl", "segment_of", "", "")
        assert len(caught_warnings) == 2


def test_check_strings_prop():
    expected = "asdf"
    with pytest.warns(XmllibInputWarning, match=expected):
        _check_strings(string_to_check="", res_id="id", prop_name="prop")


def test_check_strings_field():
    expected = "asdf"
    with pytest.warns(XmllibInputWarning, match=expected):
        _check_strings(string_to_check="", res_id="id", field_name="field")
