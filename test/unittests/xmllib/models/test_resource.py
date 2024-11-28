import pandas as pd
import pytest
import regex

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.file_values import FileValue
from dsp_tools.xmllib.models.file_values import IIIFUri
from dsp_tools.xmllib.models.resource import Resource
from dsp_tools.xmllib.models.values import BooleanValue
from dsp_tools.xmllib.models.values import ColorValue
from dsp_tools.xmllib.models.values import DateValue
from dsp_tools.xmllib.models.values import DecimalValue
from dsp_tools.xmllib.models.values import GeonameValue
from dsp_tools.xmllib.models.values import IntValue
from dsp_tools.xmllib.models.values import LinkValue
from dsp_tools.xmllib.models.values import ListValue
from dsp_tools.xmllib.models.values import Richtext
from dsp_tools.xmllib.models.values import SimpleText
from dsp_tools.xmllib.models.values import TimeValue
from dsp_tools.xmllib.models.values import UriValue


class TestAddValues:
    def test_add_bool(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_bool(":prop", "True")
        assert len(res.values) == 1
        assert isinstance(res.values[0], BooleanValue)

    def test_add_bool_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning, match=regex.escape("a 'bool' does not conform to the expected format")):
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
        with pytest.warns(DspToolsUserWarning, match=regex.escape("a 'color' does not conform to the expected format")):
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
        with pytest.warns(DspToolsUserWarning, match=regex.escape("a 'date' does not conform to the expected format")):
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
            DspToolsUserWarning, match=regex.escape("a 'decimal' does not conform to the expected format")
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
            DspToolsUserWarning, match=regex.escape("a 'geoname' does not conform to the expected format")
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
            DspToolsUserWarning, match=regex.escape("a 'integer' does not conform to the expected format")
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
            DspToolsUserWarning, match=regex.escape("a 'string' does not conform to the expected format")
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

    def test_add_list_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning, match=regex.escape("a 'list' does not conform to the expected format")):
            Resource.create_new("res_id", "restype", "label").add_list("", "", "")

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
            DspToolsUserWarning, match=regex.escape("a 'string' does not conform to the expected format")
        ):
            Resource.create_new("res_id", "restype", "label").add_simpletext("", "")

    def test_add_simple_text_multiple(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_simpletext_multiple(":prop", ["text1", "text2"])
        assert len(res.values) == 2
        assert all([isinstance(x, SimpleText) for x in res.values])

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

    def test_add_richtext_warns(self) -> None:
        with pytest.warns(
            DspToolsUserWarning, match=regex.escape("a 'string' does not conform to the expected format")
        ):
            Resource.create_new("res_id", "restype", "label").add_richtext("", "")

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
            DspToolsUserWarning, match=regex.escape("a 'timestamp' does not conform to the expected format")
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
        with pytest.warns(DspToolsUserWarning, match=regex.escape("a 'uri' does not conform to the expected format")):
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
        res = Resource.create_new("res_id", "restype", "label").add_file("foo/bar.baz")
        assert isinstance(res.file_value, FileValue)

    def test_add_file_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning, match=regex.escape("The value '' is not a valid file name")):
            Resource.create_new("res_id", "restype", "label").add_file("")

    def test_add_file_raising(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_file("existing filename")
        msg = regex.escape(
            "The resource with the ID 'res_id' already contains a file with the name: 'existing filename'.\n"
            "The new file with the name 'new filename' cannot be added."
        )
        with pytest.raises(InputError, match=msg):
            res.add_file("new filename")

    def test_add_iiif_uri(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_iiif_uri(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2"
        )
        assert isinstance(res.file_value, IIIFUri)

    def test_add_iiif_uri_warns(self) -> None:
        with pytest.warns(DspToolsUserWarning, match=regex.escape("The value '' is not a valid IIIF uri")):
            Resource.create_new("res_id", "restype", "label").add_iiif_uri("")

    def test_add_iiif_uri_raising(self) -> None:
        res = Resource.create_new("res_id", "restype", "label").add_file("existing IIIF")
        msg = regex.escape(
            "The resource with the ID 'res_id' already contains a file with the name: 'existing IIIF'.\n"
            "The new file with the name 'new IIIF' cannot be added."
        )
        with pytest.raises(InputError, match=msg):
            res.add_iiif_uri("new IIIF")


if __name__ == "__main__":
    pytest.main([__file__])
