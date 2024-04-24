import pandas as pd
import pytest
import regex

from dsp_tools.commands.excel2json.new_lists import _get_all_languages_for_columns
from dsp_tools.commands.excel2json.new_lists import _get_id
from dsp_tools.commands.excel2json.new_lists import _get_labels
from dsp_tools.commands.excel2json.new_lists import _get_preferred_language_for_id
from dsp_tools.commands.excel2json.new_lists import _make_one_node
from dsp_tools.models.exceptions import InputError


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
        assert _get_preferred_language_for_id(columns, "1") == "en"

    def test_get_preferred_language_for_id_de(self) -> None:
        columns = pd.Index(["de_1", "fr_1", "it_1", "rm_1"])
        assert _get_preferred_language_for_id(columns, "1") == "de"

    def test_get_preferred_language_for_id_fr(self) -> None:
        columns = pd.Index(["fr_1", "it_1", "rm_1"])
        assert _get_preferred_language_for_id(columns, "1") == "fr"

    def test_get_preferred_language_for_id_it(self) -> None:
        columns = pd.Index(["it_1", "rm_1"])
        assert _get_preferred_language_for_id(columns, "1") == "it"

    def test_get_preferred_language_for_id_rm(self) -> None:
        columns = pd.Index(["rm_1"])
        assert _get_preferred_language_for_id(columns, "1") == "rm"

    def test_get_preferred_language_for_id_raises(self) -> None:
        columns = pd.Index(["es_1"])
        msg = regex.escape(
            "The columns may only contain the languages: 'en', 'de', 'fr', 'it', 'rm'.\n" "The columns are: es_1"
        )
        with pytest.raises(InputError, match=msg):
            _get_preferred_language_for_id(columns, "1")


if __name__ == "__main__":
    pytest.main([__file__])
