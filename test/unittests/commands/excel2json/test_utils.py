from __future__ import annotations

import unittest
from typing import Any
from typing import cast

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal
from pytest_unordered import unordered

import dsp_tools.commands.excel2json.utils as utl
from dsp_tools.commands.excel2json.models.input_error import DuplicatesInColumnProblem

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestUtils(unittest.TestCase):
    def test_clean_data_frame(self) -> None:
        original_df = pd.DataFrame(
            {
                "  TitLE of Column 1 ": [1.54, " 0-1 ", "1-n ", "   "],
                " Title of Column 2 ": ["1", 1, "   t  ext  ", "text"],
                "Title of Column 3": ["", pd.NA, None, "text"],
            }
        )
        expected_df = pd.DataFrame(
            {
                "title of column 1": ["1.54", "0-1", "1-n", pd.NA],
                "title of column 2": ["1", "1", "t  ext", "text"],
                "title of column 3": [pd.NA, pd.NA, pd.NA, "text"],
            }
        )
        returned_df = utl.clean_data_frame(df=original_df)
        assert_frame_equal(expected_df, returned_df)

    def test_check_contains_required_columns(self) -> None:
        original_df = pd.DataFrame(columns=["col1", "col2", "col3", "extra_col"])
        required = {"col1", "col2", "col3"}
        assert not utl.check_contains_required_columns(df=original_df, required_columns=required)

        required = {"col1", "col2", "col3", "col4"}
        res = utl.check_contains_required_columns(df=original_df, required_columns=required)
        assert res.columns == ["col4"]  # type: ignore[union-attr]

    def test_check_column_for_duplicate(self) -> None:
        original_df = pd.DataFrame(
            {
                "col_1": ["1.54", "0-1", "1-n", "0-1", "1.54"],
                "col_2": ["1.54", "0-1", "1-n", "text", "neu"],
            }
        )
        assert not utl.check_column_for_duplicate(df=original_df, to_check_column="col_2")

        result = utl.check_column_for_duplicate(df=original_df, to_check_column="col_1")
        res = cast(DuplicatesInColumnProblem, result)
        assert res.column == "col_1"
        assert unordered(res.duplicate_values) == ["1.54", "0-1"]

    def test_check_required_values(self) -> None:
        original_df = pd.DataFrame(
            {
                "col_1": ["1.54", "0-1", "1-n", pd.NA],
                "col_2": ["1", "1", pd.NA, "text"],
                "col_3": ["1", "1", "1", "text"],
            }
        )
        returned_dict = utl.check_required_values(df=original_df, required_values_columns=["col_1", "col_3"])
        assert list(returned_dict.keys()) == ["col_1"]
        expected_series = pd.Series([False, False, False, True], name="col_1")
        assert_series_equal(returned_dict["col_1"], expected_series)

    def test_turn_bool_array_into_index_numbers(self) -> None:
        original_series = pd.Series([False, True, False, True])

        returned_list = utl.turn_bool_array_into_index_numbers(series=original_series, true_remains=True)
        assert unordered(returned_list) == [1, 3]

        returned_list = utl.turn_bool_array_into_index_numbers(series=original_series, true_remains=False)
        assert unordered(returned_list) == [0, 2]

    def test_get_wrong_row_numbers(self) -> None:
        original_dict = {
            "col_1": pd.Series([False, True, False, True]),
            "col_2": pd.Series([False, False, True, False]),
        }
        expected_dict = {"col_1": [3, 5], "col_2": [4]}
        returned_dict = utl.get_wrong_row_numbers(wrong_row_dict=original_dict, true_remains=True)
        self.assertDictEqual(expected_dict, returned_dict)

    def test_find_one_full_cell_in_cols(self) -> None:
        required_cols = ["label_en", "label_de", "label_fr", "label_it", "label_rm"]
        original_df = pd.DataFrame(
            {
                "label_en": [1, pd.NA, pd.NA, 4],
                "label_de": [1, pd.NA, 3, 4],
                "label_fr": [1, pd.NA, 3, pd.NA],
                "label_it": [1, pd.NA, 3, 4],
                "label_rm": [pd.NA, pd.NA, 3, 4],
            }
        )
        expected_array = pd.Series([False, True, False, False])
        returned_array = utl.find_one_full_cell_in_cols(df=original_df, required_columns=required_cols)
        assert returned_array is not None
        assert_series_equal(returned_array, expected_array)

    def test_find_one_full_cell_none(self) -> None:
        required_cols = ["label_en", "label_de", "label_fr", "label_it", "label_rm"]
        original_df = pd.DataFrame(
            {
                "label_en": [1, 2, 3, 4],
                "label_de": [1, pd.NA, 3, 4],
                "label_fr": [1, pd.NA, 3, pd.NA],
                "label_it": [1, pd.NA, 3, 4],
                "label_rm": [pd.NA, pd.NA, 3, 4],
            }
        )
        assert not utl.find_one_full_cell_in_cols(df=original_df, required_columns=required_cols)

    def test_col_must_or_not_empty_based_on_other_col(self) -> None:
        original_df = pd.DataFrame({"substring": ["1", "2", "3", "4", "5", "6"], "check": [1, pd.NA, 3, 4, pd.NA, 6]})
        assert not utl.col_must_or_not_empty_based_on_other_col(
            df=original_df,
            substring_list=["1", "3", "6"],
            substring_colname="substring",
            check_empty_colname="check",
            must_have_value=True,
        )

        expected_series = pd.Series([True, False, False, False, False, False])
        returned_series = utl.col_must_or_not_empty_based_on_other_col(
            df=original_df,
            substring_list=["1", "2"],
            substring_colname="substring",
            check_empty_colname="check",
            must_have_value=False,
        )
        assert returned_series is not None
        assert_series_equal(returned_series, expected_series)

    def test_get_labels(self) -> None:
        original_df = pd.DataFrame(
            {
                "label_en": ["text_en", "text_en"],
                "label_de": ["text_de", pd.NA],
                "label_fr": ["text_fr", pd.NA],
                "label_it": ["text_it", pd.NA],
                "label_rm": ["text_rm", pd.NA],
            }
        )
        expected_dict = {"de": "text_de", "en": "text_en", "fr": "text_fr", "it": "text_it", "rm": "text_rm"}
        returned_dict = utl.get_labels(cast("pd.Series[Any]", original_df.loc[0, :]))
        self.assertDictEqual(expected_dict, returned_dict)

        expected_dict = {"en": "text_en"}
        returned_dict = utl.get_labels(cast("pd.Series[Any]", original_df.loc[1, :]))
        self.assertDictEqual(expected_dict, returned_dict)

    def test_get_comments(self) -> None:
        original_df = pd.DataFrame(
            {
                "comment_en": ["text_en", pd.NA],
                "comment_de": ["text_de", pd.NA],
                "comment_fr": ["text_fr", pd.NA],
                "comment_it": [pd.NA, pd.NA],
                "comment_rm": ["text_rm", pd.NA],
            }
        )
        expected_dict = {"de": "text_de", "en": "text_en", "fr": "text_fr", "rm": "text_rm"}
        returned_dict = utl.get_comments(cast("pd.Series[Any]", original_df.loc[0, :]))
        assert returned_dict
        assert expected_dict == returned_dict

        assert not utl.get_comments(cast("pd.Series[Any]", original_df.loc[1, :]))


if __name__ == "__main__":
    pytest.main([__file__])
