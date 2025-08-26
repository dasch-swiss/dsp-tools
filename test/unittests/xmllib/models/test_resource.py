# mypy: disable-error-code="no-untyped-def"

import warnings
from typing import Any

import pandas as pd
import pytest
import regex

from dsp_tools.error.xmllib_errors import XmllibInputError
from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.internal.input_converters import check_and_fix_collection_input
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.internal.file_values import FileValue
from dsp_tools.xmllib.models.internal.file_values import IIIFUri
from dsp_tools.xmllib.models.internal.values import BooleanValue
from dsp_tools.xmllib.models.internal.values import ColorValue
from dsp_tools.xmllib.models.internal.values import DateValue
from dsp_tools.xmllib.models.internal.values import DecimalValue
from dsp_tools.xmllib.models.internal.values import GeonameValue
from dsp_tools.xmllib.models.internal.values import IntValue
from dsp_tools.xmllib.models.internal.values import LinkValue
from dsp_tools.xmllib.models.internal.values import ListValue
from dsp_tools.xmllib.models.internal.values import Richtext
from dsp_tools.xmllib.models.internal.values import SimpleText
from dsp_tools.xmllib.models.internal.values import TimeValue
from dsp_tools.xmllib.models.internal.values import UriValue
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended
from dsp_tools.xmllib.models.res import Resource


class TestCreateNewResource:
    def test_good(self):
        with warnings.catch_warnings(record=True) as caught_warnings:
            Resource.create_new("res_id", "restype", "label")
            assert len(caught_warnings) == 0

    def test_empty_resource_id(self):
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid xsd:ID, your input '' does not match the type."),
        ):
            Resource.create_new("", "restype", "label")

    def test_invalid_resource_id(self):
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid xsd:ID, your input 'not|ok' does not match the type."),
        ):
            Resource.create_new("not|ok", "restype", "label")

    def test_empty_restype(self):
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid resource type, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "", "label")

    def test_empty_label(self):
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape(
                "The input should be a valid non empty string, your input '<NA>' does not match the type."
            ),
        ):
            res = Resource.create_new("res_id", "restype", pd.NA)  # type: ignore[arg-type]
        assert res.label == ""


class TestAddValues:
    def test_add_bool(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_bool(":prop", "True")
        assert len(res.values) == 1
        assert isinstance(res.values[0], BooleanValue)

    def test_add_bool_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid bool, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_bool("", "")

    def test_add_bool_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_bool_optional("", None)
        assert not res.values
        res = res.add_bool_optional(":prop", "True")
        assert len(res.values) == 1
        assert isinstance(res.values[0], BooleanValue)

    def test_add_color(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_color(":prop", "#000000")
        assert len(res.values) == 1
        assert isinstance(res.values[0], ColorValue)

    def test_add_color_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid color, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_color("", "")

    def test_add_color_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_color_multiple(":prop", ["#000000", "#ffffff"])
        assert len(res.values) == 2
        assert all([isinstance(x, ColorValue) for x in res.values])

    def test_add_color_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_color_optional("", pd.NA)
        assert not res.values
        res = res.add_color_optional(":prop", "#000000")
        assert len(res.values) == 1
        assert isinstance(res.values[0], ColorValue)

    def test_add_date(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_date(":prop", "2024-10-31")
        assert len(res.values) == 1
        assert isinstance(res.values[0], DateValue)

    def test_add_date_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid date, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_date("", "")

    def test_add_date_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_date_multiple(":prop", ["2024-10-30", "2024-10-31"])
        assert len(res.values) == 2
        assert all([isinstance(x, DateValue) for x in res.values])

    def test_add_date_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_date_optional("", None)
        assert not res.values
        res = res.add_date_optional(":prop", "2024-10-30")
        assert len(res.values) == 1
        assert isinstance(res.values[0], DateValue)

    def test_add_decimal(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_decimal(":prop", "0.1")
        assert len(res.values) == 1
        assert isinstance(res.values[0], DecimalValue)

    def test_add_decimal_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid decimal, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_decimal("", "")

    def test_add_decimal_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_decimal_multiple(":prop", ["0.1", "0.2"])
        assert len(res.values) == 2
        assert all([isinstance(x, DecimalValue) for x in res.values])

    def test_add_decimal_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_decimal_optional("", None)
        assert not res.values
        res = res.add_decimal_optional(":prop", "0.1")
        assert len(res.values) == 1
        assert isinstance(res.values[0], DecimalValue)

    def test_add_geoname(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_geoname(":prop", "123456")
        assert len(res.values) == 1
        assert isinstance(res.values[0], GeonameValue)

    def test_add_geoname_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid geoname, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_geoname("", "")

    def test_add_geoname_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_geoname_multiple(":prop", ["123456", "7890"])
        assert len(res.values) == 2
        assert all([isinstance(x, GeonameValue) for x in res.values])

    def test_add_geoname_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_geoname_optional("", pd.NA)
        assert not res.values
        res = res.add_geoname_optional(":prop", "123456")
        assert len(res.values) == 1
        assert isinstance(res.values[0], GeonameValue)

    def test_add_integer(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_integer(":prop", "1")
        assert len(res.values) == 1
        assert isinstance(res.values[0], IntValue)

    def test_add_integer_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid integer, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_integer("", "")

    def test_add_integer_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_integer_multiple(":prop", ["1", "2"])
        assert len(res.values) == 2
        assert all([isinstance(x, IntValue) for x in res.values])

    def test_add_integer_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_integer_optional("", None)
        assert not res.values
        res = res.add_integer_optional(":prop", "1")
        assert len(res.values) == 1
        assert isinstance(res.values[0], IntValue)

    def test_add_link(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_link(":prop", "other_id")
        assert len(res.values) == 1
        assert isinstance(res.values[0], LinkValue)

    def test_add_link_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape(
                "The input should be a valid xsd:ID or DSP resource IRI, your input '' does not match the type."
            ),
        ):
            Resource.create_new("res_id", "restype", "label").add_link("", "")

    def test_add_link_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_link_multiple(
            ":prop", ["other_id", "yet_another_id"]
        )
        assert len(res.values) == 2
        assert all([isinstance(x, LinkValue) for x in res.values])

    def test_add_link_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_link_optional("", pd.NA)
        assert not res.values
        res = res.add_link_optional(":prop", "other_id")
        assert len(res.values) == 1
        assert isinstance(res.values[0], LinkValue)

    def test_add_list(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_list(":prop", "list-1", "node-1")
        assert len(res.values) == 1
        assert isinstance(res.values[0], ListValue)

    def test_add_list_node_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid list node, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_list("", "listname", "")

    def test_add_list_name_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid list name, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_list("", "", "node")

    def test_add_list_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_list_multiple(
            ":prop", "list-1", ["node-1", "node-2"]
        )
        assert len(res.values) == 2
        assert all([isinstance(x, ListValue) for x in res.values])

    def test_add_list_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_list_optional(":prop", "listname", None)
        assert not res.values
        res = res.add_list_optional(":prop", "list-1", "node-1")
        assert len(res.values) == 1
        assert isinstance(res.values[0], ListValue)

    def test_add_simple_text(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_simpletext(":prop", "text")
        assert len(res.values) == 1
        assert isinstance(res.values[0], SimpleText)

    def test_add_simple_text_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid non empty string, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_simpletext("", "")

    def test_add_simple_text_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_simpletext_multiple(":prop", ["text1", "text2"])
        assert len(res.values) == 2
        assert all([isinstance(x, SimpleText) for x in res.values])

    def test_add_simple_text_multiple_input_non_list(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_simpletext_multiple(":prop", "text1")
        assert len(res.values) == 1
        assert all([isinstance(x, SimpleText) for x in res.values])
        assert res.values[0].value == "text1"

    def test_add_simple_text_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_simpletext_optional(":prop", None)
        assert not res.values
        res = res.add_simpletext_optional(":prop", "text")
        assert len(res.values) == 1
        assert isinstance(res.values[0], SimpleText)

    def test_add_richtext(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_richtext(":prop", "A\nB")
        assert len(res.values) == 1
        assert isinstance(res.values[0], Richtext)
        assert res.values[0].value == "A<br/>B"

    def test_add_richtext_warns_empty_string(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid non empty string, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_richtext("prop", "")

    def test_add_richtext_warns_pd_na(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape(
                "The input should be a valid non empty string, your input '<NA>' does not match the type."
            ),
        ):
            Resource.create_new("res_id", "restype", "label").add_richtext(":prop", pd.NA)  # type: ignore[arg-type]

    def test_add_richtext_no_replace(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_richtext(
            "", "A\nB", newline_replacement=NewlineReplacement.NONE
        )
        assert len(res.values) == 1
        assert isinstance(res.values[0], Richtext)
        assert res.values[0].value == "A\nB"

    def test_add_richtext_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_richtext_multiple(":prop", ["text1", "text2"])
        assert len(res.values) == 2
        assert all([isinstance(x, Richtext) for x in res.values])

    def test_add_richtext_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_richtext_optional(":prop", None)
        assert not res.values
        res = res.add_richtext_optional(":prop", "text")
        assert len(res.values) == 1
        assert isinstance(res.values[0], Richtext)

    def test_add_time(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_time(":prop", "2024-10-31T11:00:00Z")
        assert len(res.values) == 1
        assert isinstance(res.values[0], TimeValue)

    def test_add_time_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid timestamp, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_time("", "")

    def test_add_time_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_time_multiple(
            ":prop", ["2024-10-31T11:00:00Z", "2023-01-01T00:00:00Z"]
        )
        assert len(res.values) == 2
        assert all([isinstance(x, TimeValue) for x in res.values])

    def test_add_time_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_time_optional(":prop", None)
        assert not res.values
        res = res.add_time_optional(":prop", "2023-01-01T00:00:00Z")
        assert len(res.values) == 1
        assert isinstance(res.values[0], TimeValue)

    def test_add_uri(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_uri(":prop", "https://www.google.com/")
        assert len(res.values) == 1
        assert isinstance(res.values[0], UriValue)

    def test_add_uri_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid uri, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_uri("", "")

    def test_add_uri_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_uri_multiple(
            "", ["https://www.google.com/", "https://dasch.swiss/"]
        )
        assert len(res.values) == 2
        assert all([isinstance(x, UriValue) for x in res.values])

    def test_add_uri_optional(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_uri_optional(":prop", pd.NA)
        assert not res.values
        res = res.add_uri_optional(":prop", "https://dasch.swiss/")
        assert len(res.values) == 1
        assert isinstance(res.values[0], UriValue)


class TestAddFiles:
    def test_add_file(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_file(
            "foo/bar.baz", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth"]
        )
        assert isinstance(res.file_value, FileValue)

    def test_add_file_with_metadata(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_file(
            "foo/bar.baz", LicenseRecommended.CC.BY, "copy", ["auth"]
        )
        assert isinstance(res.file_value, FileValue)
        assert res.file_value.metadata.license == LicenseRecommended.CC.BY
        assert res.file_value.metadata.copyright_holder == "copy"
        assert res.file_value.metadata.authorship == tuple(["auth"])

    def test_add_file_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("Field 'bitstream' | Your input '' is empty. Please enter a valid file name."),
        ):
            Resource.create_new("res_id", "restype", "label").add_file(
                "", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth"]
            )

    def test_add_file_raising(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_file(
            "existing filename", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth"]
        )
        msg = regex.escape(
            "Resource ID 'res_id' | Field 'file / iiif-uri' | "
            "This resource already contains a file with the name: 'existing filename'. "
            "The new file with the name 'new filename' cannot be added."
        )
        with pytest.raises(XmllibInputError, match=msg):
            res.add_file("new filename", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth"])

    def test_add_iiif_uri(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_iiif_uri(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2",
            LicenseRecommended.DSP.UNKNOWN,
            "copy",
            ["auth"],
        )
        assert isinstance(res.file_value, IIIFUri)

    def test_add_iiif_uri_with_metadata(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_iiif_uri(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2",
            LicenseRecommended.CC.BY,
            "copy",
            ["auth"],
        )
        assert isinstance(res.file_value, IIIFUri)
        assert res.file_value.metadata.license == LicenseRecommended.CC.BY
        assert res.file_value.metadata.copyright_holder == "copy"
        assert res.file_value.metadata.authorship == tuple(["auth"])

    def test_add_iiif_uri_warns(self) -> None:
        with pytest.warns(
            XmllibInputWarning,
            match=regex.escape("The input should be a valid IIIF uri, your input '' does not match the type."),
        ):
            Resource.create_new("res_id", "restype", "label").add_iiif_uri(
                "", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth"]
            )

    def test_add_iiif_uri_raising(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_file(
            "existing IIIF", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth"]
        )
        msg = regex.escape(
            "Resource ID 'res_id' | Field 'file / iiif-uri' | "
            "This resource already contains a file with the name: 'existing IIIF'. "
            "The new file with the name 'new IIIF' cannot be added."
        )
        with pytest.raises(XmllibInputError, match=msg):
            res.add_iiif_uri("new IIIF", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth"])


@pytest.mark.parametrize(
    ("input_val", "expected_val"),
    [(1, [1]), (True, [True]), ("string", ["string"]), ([1, 2], [1, 2]), ((1, 2), [1, 2]), ({1, 2}, [1, 2])],
)
def test_check_and_fix_collection_input_success(input_val: Any, expected_val: list[Any]) -> None:
    assert check_and_fix_collection_input(input_val, "prop", "id") == sorted(expected_val)


def test_check_and_fix_collection_input_warns() -> None:
    msg = regex.escape(
        "Resource ID 'id' | Property 'prop' | The input is empty. "
        "Please note that no values will be added to the resource."
    )
    with pytest.warns(XmllibInputInfo, match=msg):
        check_and_fix_collection_input([], "prop", "id")


def test_check_and_fix_collection_input_raises() -> None:
    msg = regex.escape(
        "Resource ID 'id' | Property 'prop' | "
        "The input is a dictionary. Only collections (list, set, tuple) are permissible."
    )
    with pytest.raises(XmllibInputError, match=msg):
        check_and_fix_collection_input({1: 1}, "prop", "id")


if __name__ == "__main__":
    pytest.main([__file__])
