# mypy: disable-error-code="method-assign,no-untyped-def"

import warnings

import pytest
import regex

from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import SegmentBounds
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import _check_strings
from dsp_tools.xmllib.models.dsp_base_resources import _warn_value_exists
from dsp_tools.xmllib.models.permissions import Permissions


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
        assert len(caught_warnings) == 3


def test_segment_bounds():
    expected = regex.escape(
        " | Resource ID 'res_id' | Segment bounds must be a float or integer. "
        "The following places have an unexpected type: \n"
        "    - Segment Start Value: string | Type: <class 'str'>"
    )
    with pytest.warns(XmllibInputWarning, match=expected):
        SegmentBounds("string", "1", Permissions.PROJECT_SPECIFIC_PERMISSIONS, "res_id")


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
        assert len(caught_warnings) == 1


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
        assert len(caught_warnings) == 1


# The warning matches are constructed so that the line number is not checked as that is prone to change.


def test_check_strings_prop():
    expected = (
        regex.escape("File 'test_dsp_base_resources.py:")
        + r"\d+"
        + regex.escape("' | Resource ID 'id' | Property 'prop' | The entered string is not valid.")
    )
    with pytest.warns(XmllibInputWarning, match=expected):
        _check_strings(string_to_check="", res_id="id", prop_name="prop")


def test_check_strings_field():
    expected = (
        regex.escape("File 'test_dsp_base_resources.py:")
        + r"\d+"
        + regex.escape("' | Resource ID 'id' | Field 'field' | The entered string is not valid.")
    )
    with pytest.warns(XmllibInputWarning, match=expected):
        _check_strings(string_to_check="", res_id="id", field_name="field")


def test_warn_value_exists():
    expected = (
        regex.escape("File 'test_dsp_base_resources.py:")
        + r"\d+"
        + regex.escape(
            "' | Resource ID 'id' | Field 'field' | "
            "This resource already has a value in this location. The old value 'old' is being replace with 'new'."
        )
    )
    with pytest.warns(XmllibInputWarning, match=expected):
        _warn_value_exists(old_value="old", new_value="new", res_id="id", value_field="field")
