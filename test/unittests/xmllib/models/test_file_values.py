# mypy: disable-error-code="method-assign,no-untyped-def"

import warnings

import pytest
import regex

from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.file_values import Metadata
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended


class TestMetadata:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            Metadata.new(
                LicenseRecommended.DSP.UNKNOWN,
                "copyright",
                ["authorship"],
                Permissions.PROJECT_SPECIFIC_PERMISSIONS,
                "id",
            )
        assert len(caught_warnings) == 0

    def test_good_author_not_a_list(self):
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

    def test_wrong_license(self):
        expected = regex.escape(
            "Field 'license (bistream/iiif-uri)' | "
            "The input should be a valid xmllib.License, your input 'license' does not match the type."
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            Metadata.new("license", "copyright", ["authorship"], Permissions.PROJECT_SPECIFIC_PERMISSIONS, "id")  # type: ignore[arg-type]

    def test_wrong_copyright(self):
        expected = regex.escape(
            "Field 'copyright_holder (bistream/iiif-uri)' | Your input '' is empty. Please enter a valid string."
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            Metadata.new(
                LicenseRecommended.DSP.UNKNOWN, "", ["authorship"], Permissions.PROJECT_SPECIFIC_PERMISSIONS, "id"
            )

    def test_wrong_authorship(self):
        expected = regex.escape(
            "Field 'authorship (bistream/iiif-uri)' | Your input '' is empty. Please enter a valid string."
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            Metadata.new(
                LicenseRecommended.DSP.UNKNOWN, "copyright", [""], Permissions.PROJECT_SPECIFIC_PERMISSIONS, "id"
            )

    def test_wrong_permissions(self):
        expected = regex.escape(
            "Field 'permissions (bistream/iiif-uri)' | "
            "The input should be a valid xmllib.Permissions, your input 'string' does not match the type."
        )
        with pytest.warns(XmllibInputWarning, match=expected):
            Metadata.new(LicenseRecommended.DSP.UNKNOWN, "copyright", ["authorship"], "string", "id")  # type: ignore[arg-type]
