# mypy: disable-error-code="method-assign,no-untyped-def"

import warnings
from pathlib import Path

import pandas as pd
import pytest
import regex

from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.internal.file_values import FileValue
from dsp_tools.xmllib.models.internal.file_values import IIIFUri
from dsp_tools.xmllib.models.internal.file_values import Metadata
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended


@pytest.fixture
def metadata():
    return Metadata.new(
        LicenseRecommended.DSP.UNKNOWN,
        "copyright",
        ["authorship"],
        Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        "id",
    )


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
        assert res.authorship == ("authorship",)

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


class TestFileValue:
    def test_good(self, metadata):
        with warnings.catch_warnings(record=True) as caught_warnings:
            val = FileValue.new(
                Path("file.jpg"),
                metadata,
                pd.NA,  # type: ignore[arg-type]
                "id",
            )
        assert len(caught_warnings) == 0
        assert val.comment is None
        assert val.value == "file.jpg"

    def test_empty_path(self, metadata):
        expected = regex.escape("Field 'bitstream' | Your input '' is empty. Please enter a valid file name.")
        with pytest.warns(XmllibInputWarning, match=expected):
            val = FileValue.new(Path(""), metadata, None, "id")
        assert val.value == ""

    def test_path_is_none(self, metadata):
        expected = regex.escape("Field 'bitstream' | Your input 'None' is empty. Please enter a valid file name.")
        with pytest.warns(XmllibInputWarning, match=expected):
            val = FileValue.new(None, metadata, None, "id")  # type: ignore[arg-type]
        assert val.value == "None"


class TestIIIFUri:
    def test_good(self, metadata):
        with warnings.catch_warnings(record=True) as caught_warnings:
            val = IIIFUri.new(
                "https://example.org/image-service/abcd1234/full/max/0/default.jpg",
                metadata,
                pd.NA,  # type: ignore[arg-type]
                "id",
            )
        assert len(caught_warnings) == 0
        assert val.comment is None

    def test_wrong_val(self, metadata):
        expected = regex.escape("The input should be a valid IIIF uri, your input 'not a uri' does not match the type.")
        with pytest.warns(XmllibInputWarning, match=expected):
            IIIFUri.new("not a uri", metadata, None, "id")
