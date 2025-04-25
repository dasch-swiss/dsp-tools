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

# The warning matches are constructed so that the line number is not checked as that is prone to change.


class TestRegionResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            RegionResource.create_new("id", "lbl", "regionOfId")
        assert len(caught_warnings) == 0

    def test_warns_res_id(self):
        expected = (
            regex.escape("Trace 'test_test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            RegionResource.create_new("", "lbl", "regionOfId")

    def test_warns_label(self):
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            RegionResource.create_new("id", "", "regionOfId")

    def test_warns_region_of(self):
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            RegionResource.create_new("id", "lbl", "")


class TestLinkResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            LinkResource.create_new("id", "lbl", ["link_to"])
        assert len(caught_warnings) == 0

    def test_warns_res_id(self):
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            LinkResource.create_new("", "lbl", ["link_to"])

    def test_warns_label(self):
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            LinkResource.create_new("id", "", ["link_to"])


def test_segment_bounds():
    expected = regex.escape("sadf")
    with pytest.warns(XmllibInputWarning, match=expected):
        SegmentBounds("string", "1", "res_id")


class TestVideoSegmentResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            VideoSegmentResource.create_new("id", "lbl", "segment_of", "0", "1")
        assert len(caught_warnings) == 0

    def test_warns_res_id(self):
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            VideoSegmentResource.create_new("", "lbl", "segment_of", "0", "1")

    def test_warns_label(self):
        expected = regex.escape("asdf")
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            VideoSegmentResource.create_new("id", "", "segment_of", "0", "1")

    def test_warns_segment_of(self):
        expected = regex.escape("asdf")
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            VideoSegmentResource.create_new("id", "lbl", "", "0", "1")


class TestAudioSegmentResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            AudioSegmentResource.create_new("id", "lbl", "segment_of", "0", "1")
        assert len(caught_warnings) == 0

    def test_warns_res_id(self):
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            AudioSegmentResource.create_new("", "lbl", "segment_of", "0", "1")

    def test_warns_label(self):
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            AudioSegmentResource.create_new("id", "", "segment_of", "0", "1")

    def test_warns_segment_of(self):
        expected = (
            regex.escape("Trace 'test_dsp_base_resources.py:")
            + r"\d+"
            + regex.escape("' | Field 'Resource ID' | The entered string is not valid.")
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            AudioSegmentResource.create_new("id", "lbl", "", "0", "1")
