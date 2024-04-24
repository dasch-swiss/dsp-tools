import pandas as pd
import pytest
import regex
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json.new_lists import _fill_id_column
from dsp_tools.commands.excel2json.new_lists import _fill_parent_id
from dsp_tools.commands.excel2json.new_lists import _get_all_languages_for_columns
from dsp_tools.commands.excel2json.new_lists import _get_columns_preferred_lang
from dsp_tools.commands.excel2json.new_lists import _get_id
from dsp_tools.commands.excel2json.new_lists import _get_labels
from dsp_tools.commands.excel2json.new_lists import _get_preferred_language
from dsp_tools.commands.excel2json.new_lists import _get_remaining_column_nums
from dsp_tools.commands.excel2json.new_lists import _make_one_node
from dsp_tools.models.exceptions import InputError


class TestFillIdColumn:
    def test_to_fill(self) -> None:
        test_df = pd.DataFrame(
            {
                "ID (optional)": [pd.NA, "1", pd.NA, "3", pd.NA, pd.NA, pd.NA, pd.NA],
                "en_list": ["list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en"],
                "en_1": [pd.NA, "nd_en_1", "nd_en_2", "nd_en_3", "nd_en_3", "nd_en_3", "nd_en_3", "nd_en_3"],
                "en_2": [pd.NA, pd.NA, pd.NA, pd.NA, "nd_en_3.1", "nd_en_3.2", "nd_en_3.2", "nd_en_3.2"],
                "en_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "nd_en_3.2.1", "nd_en_3.2.2"],
            }
        )
        expected = [
            "list_en",
            pd.NA,
            "nd_en_2",
            pd.NA,
            "nd_en_3.1",
            "nd_en_3.2",
            "nd_en_3.2.1",
            "nd_en_3.2.2",
        ]
        res = _fill_id_column(test_df, "en")
        assert res["auto_id"].to_list() == expected

    def test_nothing_to_fill(self) -> None:
        test_df = pd.DataFrame(
            {
                "ID (optional)": ["list_en", "1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
            }
        )
        expected = pd.DataFrame(
            {
                "ID (optional)": ["list_en", "1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
                "auto_id": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        res = _fill_id_column(test_df, "en")
        assert_frame_equal(res, expected)


def test_fill_parent_id() -> None:
    test_df = pd.DataFrame(
        {
            "ID (optional)": [
                "list_en",
                "1",
                "2",
                "3",
                "3.1",
                "3.2",
                "3.2.1",
                "3.2.2",
            ],
            "en_list": ["list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en"],
            "en_1": [pd.NA, "nd_en_1", "nd_en_2", "nd_en_3", "nd_en_3", "nd_en_3", "nd_en_3", "nd_en_3"],
            "en_2": [pd.NA, pd.NA, pd.NA, pd.NA, "nd_en_3.1", "nd_en_3.2", "nd_en_3.2", "nd_en_3.2"],
            "en_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "nd_en_3.2.1", "nd_en_3.2.2"],
        }
    )
    expected = ["list_en", "list_en", "list_en", "list_en", "3", "3", "3.2", "3.2"]
    res = _fill_parent_id(test_df, "en")
    assert res["parent_id"].to_list() == expected


def test_get_columns_preferred_lang_returns_expected_columns() -> None:
    columns = pd.Index(["en_2", "de_1", "en_1", "it_1"])
    assert _get_columns_preferred_lang(columns, "en") == ["en_1", "en_2"]


def test_get_columns_preferred_lang_returns_empty_list_for_no_match() -> None:
    columns = pd.Index(["de_1", "de_2", "it_1"])
    assert not _get_columns_preferred_lang(columns, "en")


class TestMakeOneNode:
    def test_creates_node_with_correct_id_and_labels(self):
        row = pd.DataFrame({"ID (optional)": ["1.1"], "en_1": ["Hello"], "de_1": ["Hallo"]}, index=[1])
        node = _make_one_node(row.loc[1], "1")
        assert node.id_ == "1.1"
        assert node.labels == {"en": "Hello", "de": "Hallo"}
        assert node.row_number == 1

    def test_generates_id_when_not_provided(self):
        row = pd.DataFrame({"ID (optional)": [pd.NA], "en_1": ["Hello"], "de_1": ["Hallo"]}, index=[2])
        node = _make_one_node(row.loc[2], "1")
        assert node.id_ == "Hello"
        assert node.labels == {"en": "Hello", "de": "Hallo"}
        assert node.row_number == 2


class TestGetId:
    def test_returns_id_when_provided(self) -> None:
        df = pd.DataFrame({"ID (optional)": ["1.1"], "en_1": ["Hello"], "de_1": ["Hallo"]}, index=[5])
        row = df.loc[5]
        assert _get_id(row, "1") == "1.1"

    def test_generates_id_when_not_provided(self) -> None:
        df = pd.DataFrame({"ID (optional)": [pd.NA], "en_1": ["Hello"], "de_1": ["Hallo"]}, index=[7])
        row = df.loc[7]
        assert _get_id(row, "1") == "Hello"

    def test_generates_id_list(self) -> None:
        df = pd.DataFrame({"ID (optional)": [pd.NA], "en_list": ["Hello"], "de_1": ["Hallo"]}, index=[9])
        row = df.loc[9]
        assert _get_id(row, "list") == "Hello"

    def test_raises_error_when_no_language_column(self) -> None:
        df = pd.DataFrame({"ID (optional)": [pd.NA], "es_1": ["Hola"]}, index=[11])
        row = df.loc[11]
        with pytest.raises(InputError):
            _get_id(row, "1")


class TestGetLabels:
    def test_correct_labels_for_all_languages(self) -> None:
        row = pd.Series(
            {
                "en_1": "Hello",
                "de_1": "Hallo",
                "fr_1": "Bonjour",
                "it_1": "Ciao",
                "rm_1": "Bun di",
                "en_2": pd.NA,
                "de_2": pd.NA,
            }
        )
        col_ending = "1"
        expected = {"en": "Hello", "de": "Hallo", "fr": "Bonjour", "it": "Ciao", "rm": "Bun di"}
        assert _get_labels(row, col_ending) == expected

    def test_returns_correct_labels_for_some_languages(self) -> None:
        row = pd.Series(
            {
                "en_1": "Hello",
                "de_1": pd.NA,
                "fr_1": "Bonjour",
                "it_1": pd.NA,
                "rm_1": "Bun di",
                "en_2": "English_2",
            }
        )
        col_ending = "1"
        assert _get_labels(row, col_ending) == {"en": "Hello", "fr": "Bonjour", "rm": "Bun di"}

    def test_returns_empty_dict_for_no_languages(self) -> None:
        row = pd.Series(
            {
                "en_1": pd.NA,
                "de_1": pd.NA,
                "fr_1": pd.NA,
                "it_1": pd.NA,
                "rm_1": pd.NA,
                "en_2": pd.NA,
                "de_2": pd.NA,
                "fr_2": pd.NA,
                "it_2": pd.NA,
                "rm_2": pd.NA,
            }
        )
        col_ending = "1"
        assert not _get_labels(row, col_ending)


class TestGetRemainingColumns:
    def test_with_matching_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3", "it_4", "rm_5", "de_11"])
        assert _get_remaining_column_nums(columns, 2) == [2, 3, 4, 5, 11]

    def test_with_no_matching_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3", "it_4", "rm_5"])
        assert _get_remaining_column_nums(columns, 6) == []

    def test_with_non_language_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3", "it_4", "rm_5", "other_6"])
        assert _get_remaining_column_nums(columns, 2) == [2, 3, 4, 5]

    def test_with_non_numeric_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3", "it_4", "rm_5", "en_other"])
        assert _get_remaining_column_nums(columns, 2) == [2, 3, 4, 5]


class TestGetAllLanguagesForColumns:
    def test_get_all_languages_for_columns_returns_correct_languages(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1", "en_2"])
        ending = "1"
        assert _get_all_languages_for_columns(columns, ending) == ["en", "de", "fr", "it", "rm"]

    def test_get_all_languages_for_columns_returns_empty_list_for_no_match(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1", "en_2", "de_2", "fr_2", "it_2", "rm_2"])
        ending = "3"
        assert not _get_all_languages_for_columns(columns, ending)


class TestGetPreferredLanguageForId:
    def test_get_preferred_language_for_id_en(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1"])
        assert _get_preferred_language(columns, "1") == "en"

    def test_get_preferred_language_for_id_de(self) -> None:
        columns = pd.Index(["de_1", "fr_1", "it_1", "rm_1"])
        assert _get_preferred_language(columns, "1") == "de"

    def test_get_preferred_language_for_id_fr(self) -> None:
        columns = pd.Index(["fr_1", "it_1", "rm_1"])
        assert _get_preferred_language(columns, "1") == "fr"

    def test_get_preferred_language_for_id_it(self) -> None:
        columns = pd.Index(["it_1", "rm_1"])
        assert _get_preferred_language(columns, "1") == "it"

    def test_get_preferred_language_for_id_rm(self) -> None:
        columns = pd.Index(["rm_1"])
        assert _get_preferred_language(columns, "1") == "rm"

    def test_get_preferred_language_for_id_raises(self) -> None:
        columns = pd.Index(["es_1"])
        msg = regex.escape(
            "The columns may only contain the languages: 'en', 'de', 'fr', 'it', 'rm'.\n" "The columns are: es_1"
        )
        with pytest.raises(InputError, match=msg):
            _get_preferred_language(columns, "1")


if __name__ == "__main__":
    pytest.main([__file__])
