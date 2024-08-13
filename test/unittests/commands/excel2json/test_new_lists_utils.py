from __future__ import annotations

import pandas as pd
import pytest
import regex

from dsp_tools.commands.excel2json.new_lists.utils import get_all_languages_for_columns
from dsp_tools.commands.excel2json.new_lists.utils import get_columns_of_preferred_lang
from dsp_tools.commands.excel2json.new_lists.utils import get_comment_cols
from dsp_tools.commands.excel2json.new_lists.utils import get_hierarchy_nums
from dsp_tools.commands.excel2json.new_lists.utils import get_lang_string_from_column_name
from dsp_tools.commands.excel2json.new_lists.utils import get_list_cols
from dsp_tools.commands.excel2json.new_lists.utils import get_node_label_col_mapper
from dsp_tools.commands.excel2json.new_lists.utils import get_preferred_language
from dsp_tools.models.exceptions import InputError


@pytest.fixture()
def columns_correct() -> pd.Index[str]:
    return pd.Index(
        [
            "ID (optional)",
            "en_list",
            "de_list",
            "en_comment",
            "de_comment",
            "en_1",
            "de_1",
            "en_2",
            "de_2",
            "additional",
        ]
    )


def test_get_lang_string_good() -> None:
    assert get_lang_string_from_column_name("en_1") == "en"


def test_get_lang_string_raises() -> None:
    assert not get_lang_string_from_column_name("ru_1")


class TestGetRemainingColumns:
    def test_with_matching_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3"])
        assert get_hierarchy_nums(columns) == [1, 2, 3]

    def test_with_list_language_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3", "de_list"])
        assert get_hierarchy_nums(columns) == [1, 2, 3]

    def test_with_non_numeric_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3", "it_4", "rm_5", "en_other"])
        assert get_hierarchy_nums(columns) == [1, 2, 3, 4, 5]


class TestGetAllLanguagesForColumns:
    def test_get_all_languages_for_columns_returns_correct_languages(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1", "en_2"])
        ending = "1"
        assert get_all_languages_for_columns(columns, ending) == {"en", "de", "fr", "it", "rm"}

    def test_get_all_languages_for_columns_returns_empty_list_for_no_match(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1", "en_2", "de_2", "fr_2", "it_2", "rm_2"])
        ending = "3"
        assert not get_all_languages_for_columns(columns, ending)


class TestGetPreferredLanguageForId:
    def test_get_preferred_language_for_id_en(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1"])
        assert get_preferred_language(columns, "1") == "en"

    def test_get_preferred_language_for_id_de(self) -> None:
        columns = pd.Index(["de_1", "fr_1", "it_1", "rm_1"])
        assert get_preferred_language(columns, "1") == "de"

    def test_get_preferred_language_for_id_fr(self) -> None:
        columns = pd.Index(["fr_1", "it_1", "rm_1"])
        assert get_preferred_language(columns, "1") == "fr"

    def test_get_preferred_language_for_id_it(self) -> None:
        columns = pd.Index(["it_1", "rm_1"])
        assert get_preferred_language(columns, "1") == "it"

    def test_get_preferred_language_for_id_rm(self) -> None:
        columns = pd.Index(["rm_1"])
        assert get_preferred_language(columns, "1") == "rm"

    def test_get_preferred_language_for_id_raises(self) -> None:
        columns = pd.Index(["es_1"])
        msg = regex.escape(
            "The columns may only contain the languages: 'en', 'de', 'fr', 'it', 'rm'.\n" "The columns are: es_1"
        )
        with pytest.raises(InputError, match=msg):
            get_preferred_language(columns, "1")


def test_get_columns_preferred_lang_returns_expected_columns() -> None:
    columns = pd.Index(["en_2", "de_1", "en_1", "it_1"])
    assert get_columns_of_preferred_lang(columns, "en") == ["en_1", "en_2"]


def test_get_columns_preferred_lang_returns_empty_list_for_no_match() -> None:
    columns = pd.Index(["de_1", "de_2", "it_1"])
    assert not get_columns_of_preferred_lang(columns, "en")


def test_get_node_label_col_mapper(columns_correct: pd.Index[str]) -> None:
    result = get_node_label_col_mapper(columns_correct)
    assert result == {
        1: {"en_1", "de_1"},
        2: {"en_2", "de_2"},
    }


def test_get_list_cols(columns_correct: pd.Index[str]) -> None:
    result = get_list_cols(columns_correct)
    assert result == {"en_list", "de_list"}


def test_get_comment_cols(columns_correct: pd.Index[str]) -> None:
    result = get_comment_cols(columns_correct)
    assert result == {"en_comment", "de_comment"}
