import pandas as pd
import pytest
import regex

from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.file_values import FileValue
from dsp_tools.xmllib.models.file_values import IIIFUri
from dsp_tools.xmllib.models.resource import Resource
from dsp_tools.xmllib.models.user_enums import NewlineReplacement
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
        res = Resource("", "", "").add_bool("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], BooleanValue)

    def test_add_bools(self) -> None:
        res = Resource("", "", "").add_bools(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, BooleanValue) for x in res.values])

    def test_add_bool_optional(self) -> None:
        res = Resource("", "", "").add_bool_optional(None, "")
        assert not res.values
        res = res.add_bool_optional("val", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], BooleanValue)

    def test_add_color(self) -> None:
        res = Resource("", "", "").add_color("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], ColorValue)

    def test_add_colors(self) -> None:
        res = Resource("", "", "").add_colors(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, ColorValue) for x in res.values])

    def test_add_color_optional(self) -> None:
        res = Resource("", "", "").add_color_optional(pd.NA, "")
        assert not res.values
        res = res.add_color_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], ColorValue)

    def test_add_date(self) -> None:
        res = Resource("", "", "").add_date("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], DateValue)

    def test_add_dates(self) -> None:
        res = Resource("", "", "").add_dates(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, DateValue) for x in res.values])

    def test_add_date_optional(self) -> None:
        res = Resource("", "", "").add_date_optional(None, "")
        assert not res.values
        res = res.add_date_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], DateValue)

    def test_add_decimal(self) -> None:
        res = Resource("", "", "").add_decimal("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], DecimalValue)

    def test_add_decimals(self) -> None:
        res = Resource("", "", "").add_decimals(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, DecimalValue) for x in res.values])

    def test_add_decimal_optional(self) -> None:
        res = Resource("", "", "").add_decimal_optional(None, "")
        assert not res.values
        res = res.add_decimal_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], DecimalValue)

    def test_add_geoname(self) -> None:
        res = Resource("", "", "").add_geoname("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], GeonameValue)

    def test_add_geonames(self) -> None:
        res = Resource("", "", "").add_geonames(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, GeonameValue) for x in res.values])

    def test_add_geoname_optional(self) -> None:
        res = Resource("", "", "").add_geoname_optional(pd.NA, "")
        assert not res.values
        res = res.add_geoname_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], GeonameValue)

    def test_add_integer(self) -> None:
        res = Resource("", "", "").add_integer("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], IntValue)

    def test_add_integers(self) -> None:
        res = Resource("", "", "").add_integers(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, IntValue) for x in res.values])

    def test_add_integer_optional(self) -> None:
        res = Resource("", "", "").add_integer_optional(None, "")
        assert not res.values
        res = res.add_integer_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], IntValue)

    def test_add_link(self) -> None:
        res = Resource("", "", "").add_link("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], LinkValue)

    def test_add_links(self) -> None:
        res = Resource("", "", "").add_links(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, LinkValue) for x in res.values])

    def test_add_link_optional(self) -> None:
        res = Resource("", "", "").add_link_optional(pd.NA, "")
        assert not res.values
        res = res.add_link_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], LinkValue)

    def test_add_list(self) -> None:
        res = Resource("", "", "").add_list("", "", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], ListValue)

    def test_add_lists(self) -> None:
        res = Resource("", "", "").add_lists(["", ""], "", "")
        assert len(res.values) == 2
        assert all([isinstance(x, ListValue) for x in res.values])

    def test_add_list_optional(self) -> None:
        res = Resource("", "", "").add_list_optional(None, None, "")
        assert not res.values
        res = res.add_list_optional("", "", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], ListValue)

    def test_add_simple_text(self) -> None:
        res = Resource("", "", "").add_simpletext("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], SimpleText)

    def test_add_simple_texts(self) -> None:
        res = Resource("", "", "").add_simpletexts(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, SimpleText) for x in res.values])

    def test_add_simple_text_optional(self) -> None:
        res = Resource("", "", "").add_simpletext_optional(None, "")
        assert not res.values
        res = res.add_simpletext_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], SimpleText)

    def test_add_richtext(self) -> None:
        res = Resource("", "", "").add_richtext("A\nB", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], Richtext)
        assert res.values[0].value == "A<br/>B"

    def test_add_richtext_no_replace(self) -> None:
        res = Resource("", "", "").add_richtext("A\nB", "", newline_replacement=NewlineReplacement.NONE)
        assert len(res.values) == 1
        assert isinstance(res.values[0], Richtext)
        assert res.values[0].value == "A\nB"

    def test_add_richtexts(self) -> None:
        res = Resource("", "", "").add_richtexts(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, Richtext) for x in res.values])

    def test_add_richtext_optional(self) -> None:
        res = Resource("", "", "").add_richtext_optional(None, "")
        assert not res.values
        res = res.add_richtext_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], Richtext)

    def test_add_time(self) -> None:
        res = Resource("", "", "").add_time("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], TimeValue)

    def test_add_times(self) -> None:
        res = Resource("", "", "").add_times(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, TimeValue) for x in res.values])

    def test_add_time_optional(self) -> None:
        res = Resource("", "", "").add_time_optional(None, "")
        assert not res.values
        res = res.add_time_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], TimeValue)

    def test_add_uri(self) -> None:
        res = Resource("", "", "").add_uri("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], UriValue)

    def test_add_uris(self) -> None:
        res = Resource("", "", "").add_uris(["", ""], "")
        assert len(res.values) == 2
        assert all([isinstance(x, UriValue) for x in res.values])

    def test_add_uri_optional(self) -> None:
        res = Resource("", "", "").add_uri_optional(pd.NA, "")
        assert not res.values
        res = res.add_uri_optional("", "")
        assert len(res.values) == 1
        assert isinstance(res.values[0], UriValue)


class TestAddFiles:
    def test_add_file(self) -> None:
        res = Resource("", "", "").add_file("")
        assert isinstance(res.file_value, FileValue)

    def test_add_file_raising(self) -> None:
        res = Resource("id", "", "").add_file("existing filename")
        msg = regex.escape(
            "The resource with the ID 'id' already contains a file with the name: 'existing filename'.\n"
            "The new file with the name 'new filename' cannot be added."
        )
        with pytest.raises(InputError, match=msg):
            res.add_file("new filename")

    def test_add_iiif_uri(self) -> None:
        res = Resource("", "", "").add_iiif_uri("")
        assert isinstance(res.file_value, IIIFUri)

    def test_add_iiif_uri_raising(self) -> None:
        res = Resource("id", "", "").add_file("existing IIIF")
        msg = regex.escape(
            "The resource with the ID 'id' already contains a file with the name: 'existing IIIF'.\n"
            "The new file with the name 'new IIIF' cannot be added."
        )
        with pytest.raises(InputError, match=msg):
            res.add_iiif_uri("new IIIF")


if __name__ == "__main__":
    pytest.main([__file__])
