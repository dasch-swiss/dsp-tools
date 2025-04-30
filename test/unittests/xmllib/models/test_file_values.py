# mypy: disable-error-code="method-assign,no-untyped-def"
import warnings

import pytest
import regex

from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.file_values import Metadata
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended


class TestMetadata:
    def good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            Metadata.new(
                LicenseRecommended.DSP.UNKNOWN,
                "copyright",
                ["authorship"],
                Permissions.PROJECT_SPECIFIC_PERMISSIONS,
                "id",
            )
        assert len(caught_warnings) == 0

    def good_author_not_a_list(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            res = Metadata.new(
                LicenseRecommended.DSP.UNKNOWN,
                "copyright",
                "authorship",
                Permissions.PROJECT_SPECIFIC_PERMISSIONS,
                "id",
            )
        assert len(caught_warnings) == 0
        assert res.authorship == tuple(["authorship"])

    def wrong_license(self):
        expected = regex.escape("fds")
        with pytest.warns(XmllibInputWarning, match=expected):
            Metadata.new("license", "copyright", ["authorship"], Permissions.PROJECT_SPECIFIC_PERMISSIONS, "id")

    def wrong_copyright(self):
        expected = regex.escape("fds")
        with pytest.warns(XmllibInputWarning, match=expected):
            Metadata.new(
                LicenseRecommended.DSP.UNKNOWN, "", ["authorship"], Permissions.PROJECT_SPECIFIC_PERMISSIONS, "id"
            )

    def wrong_authorship(self):
        expected = regex.escape("fds")
        with pytest.warns(XmllibInputWarning, match=expected):
            Metadata.new(
                LicenseRecommended.DSP.UNKNOWN, "copyright", [""], Permissions.PROJECT_SPECIFIC_PERMISSIONS, "id"
            )

    def wrong_permissions(self):
        expected = regex.escape("fds")
        with pytest.warns(XmllibInputWarning, match=expected):
            Metadata.new(LicenseRecommended.DSP.UNKNOWN, "copyright", ["authorship"], "string", "id")
