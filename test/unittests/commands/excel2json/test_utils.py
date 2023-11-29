# pylint: disable=missing-class-docstring,missing-function-docstring

import unittest
from typing import cast

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal
from pytest_unordered import unordered

import dsp_tools.commands.excel2json.utils as utl


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

    def test_check_contains_required_columns_else_raise_error(self) -> None:
        original_df = pd.DataFrame(columns=["col1", "col2", "col3", "extra_col"])
        required = {"col1", "col2", "col3"}
        assert not utl.check_contains_required_columns_else_raise_error(df=original_df, required_columns=required)

        required = {"col1", "col2", "col3", "col4"}
        res = utl.check_contains_required_columns_else_raise_error(df=original_df, required_columns=required)
        assert res.column == ["col4"]
        assert res.user_msg == "The following required columns are missing in the excel:"

    def test_check_column_for_duplicate_else_raise_error(self) -> None:
        original_df = pd.DataFrame(
            {
                "col_1": ["1.54", "0-1", "1-n", "0-1", "1.54"],
                "col_2": ["1.54", "0-1", "1-n", "text", "neu"],
            }
        )
        assert not utl.check_column_for_duplicate(df=original_df, to_check_column="col_2")

        res = utl.check_column_for_duplicate(df=original_df, to_check_column="col_1")
        assert res.user_msg == "Duplicate values are not allowed in the following:"
        assert res.column == "col_1"
        assert unordered(res.values) == ["1.54", "0-1"]
        assert not res.rows

    def test_check_required_values(self) -> None:
        original_df = pd.DataFrame(
            {
                "col_1": ["1.54", "0-1", "1-n", pd.NA],
                "col_2": ["1", "1", pd.NA, "text"],
                "col_3": ["1", "1", "1", "text"],
            }
        )
        expected_dict = {"col_1": [False, False, False, True]}
        returned_dict = utl.check_required_values(df=original_df, required_values_columns=["col_1", "col_3"])
        self.assertListEqual(list(expected_dict.keys()), list(returned_dict.keys()))
        for key, expected_list in expected_dict.items():
            self.assertListEqual(list(returned_dict[key]), expected_list)

    def test_turn_bool_array_into_index_numbers(self) -> None:
        original_series = pd.Series([False, True, False, True])
        expected_list = [1, 3]
        returned_list = utl.turn_bool_array_into_index_numbers(series=original_series, true_remains=True)
        self.assertListEqual(expected_list, returned_list)
        expected_list = [0, 2]
        returned_list = utl.turn_bool_array_into_index_numbers(series=original_series, true_remains=False)
        self.assertListEqual(expected_list, returned_list)

    def test_get_wrong_row_numbers(self) -> None:
        original_dict = {
            "col_1": pd.Series([False, True, False, True]),
            "col_2": pd.Series([False, False, True, False]),
        }
        expected_dict = {"col_1": [3, 5], "col_2": [4]}
        returned_dict = utl.get_wrong_row_numbers(wrong_row_dict=original_dict, true_remains=True)
        self.assertDictEqual(expected_dict, returned_dict)

    def test_update_dict_if_not_value_none(self) -> None:
        original_dict = {0: 0}
        original_update_dict = {1: 1, 2: 2, 3: None, 4: pd.NA, 5: "5"}
        expected_dict = {0: 0, 1: 1, 2: 2, 5: "5"}
        returned_dict = utl.update_dict_if_not_value_none(
            additional_dict=original_update_dict, to_update_dict=original_dict
        )
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
        assert_series_equal(expected_array, returned_array)
        original_df = pd.DataFrame(
            {
                "label_en": [1, 2, 3, 4],
                "label_de": [1, pd.NA, 3, 4],
                "label_fr": [1, pd.NA, 3, pd.NA],
                "label_it": [1, pd.NA, 3, 4],
                "label_rm": [pd.NA, pd.NA, 3, 4],
            }
        )
        returned_array = utl.find_one_full_cell_in_cols(df=original_df, required_columns=required_cols)
        self.assertIsNone(returned_array)

    def test_col_must_or_not_empty_based_on_other_col(self) -> None:
        original_df = pd.DataFrame({"substring": ["1", "2", "3", "4", "5", "6"], "check": [1, pd.NA, 3, 4, pd.NA, 6]})
        returned_value = utl.col_must_or_not_empty_based_on_other_col(
            df=original_df,
            substring_list=["1", "3", "6"],
            substring_colname="substring",
            check_empty_colname="check",
            must_have_value=True,
        )
        self.assertIsNone(returned_value)
        expected_series = pd.Series([True, False, False, False, False, False])
        returned_series = utl.col_must_or_not_empty_based_on_other_col(
            df=original_df,
            substring_list=["1", "2"],
            substring_colname="substring",
            check_empty_colname="check",
            must_have_value=False,
        )
        assert_series_equal(expected_series, returned_series)

    def test__get_labels(self) -> None:
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
        returned_dict = utl.get_labels(original_df.loc[0, :])
        self.assertDictEqual(expected_dict, returned_dict)
        expected_dict = {"en": "text_en"}
        returned_dict = utl.get_labels(original_df.loc[1, :])
        self.assertDictEqual(expected_dict, returned_dict)

    def test_get_comments(self) -> None:
        original_df = pd.DataFrame(
            {
                "comment_en": ["text_en", pd.NA],
                "comment_de": ["text_de", pd.NA],
                "comment_fr": ["text_fr", pd.NA],
                "comment_it": ["text_it", pd.NA],
                "comment_rm": ["text_rm", pd.NA],
            }
        )
        expected_dict = {"de": "text_de", "en": "text_en", "fr": "text_fr", "it": "text_it", "rm": "text_rm"}
        returned_dict = utl.get_comments(original_df.loc[0, :])
        self.assertDictEqual(expected_dict, cast(dict[str, str], returned_dict))
        returned_none = utl.get_comments(original_df.loc[1, :])
        self.assertIsNone(cast(None, returned_none))

    def test_add_optional_columns(self) -> None:
        original_df = pd.DataFrame(
            {
                "comment_en": ["text_en", pd.NA],
                "comment_it": ["text_it", pd.NA],
                "comment_rm": [pd.NA, pd.NA],
            }
        )
        optional_cols = {"comment_en", "comment_de", "comment_fr", "comment_it", "comment_rm"}
        expected_df = pd.DataFrame(
            {
                "comment_de": [pd.NA, pd.NA],
                "comment_en": ["text_en", pd.NA],
                "comment_fr": [pd.NA, pd.NA],
                "comment_it": ["text_it", pd.NA],
                "comment_rm": [pd.NA, pd.NA],
            }
        )
        returned_df = utl.add_optional_columns(df=original_df, optional_col_set=optional_cols)
        # as the columns are extracted via a set, they are not sorted and may appear in any order,
        # this would cause the validation to fail
        returned_df = returned_df.sort_index(axis=1)
        assert_frame_equal(expected_df, returned_df)
        # if all columns exist, the df should be returned unchanged
        unchanged_df = utl.add_optional_columns(df=expected_df, optional_col_set=optional_cols)
        assert_frame_equal(expected_df, unchanged_df)


if __name__ == "__main__":
    pytest.main([__file__])
