# pylint: disable=f-string-without-interpolation,missing-class-docstring,missing-function-docstring

import unittest
import pytest
import pandas as pd

from dsp_tools.models.exceptions import BaseError
import dsp_tools.utils.excel_to_json.utils as utl

from pandas.testing import assert_frame_equal, assert_series_equal


class TestUtils(unittest.TestCase):
    def test_clean_data_frame(self):
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
        returned_df = utl.clean_data_frame(unclean_df=original_df)
        assert_frame_equal(expected_df, returned_df)

    def test_check_required_columns_raises_error(self):
        original_df = pd.DataFrame(columns=["col1", "col2", "col3", "extra_col"])
        required = {"col1", "col2", "col3"}
        utl.check_required_columns_raises_error(check_df=original_df, required_columns=required)
        required = {"col1", "col2", "col3", "col4"}
        with self.assertRaises(BaseError) as context:
            utl.check_required_columns_raises_error(check_df=original_df, required_columns=required)
            self.assertEqual(
                context,
                "The following columns are missing in the excel: "
                "{required_columns.difference(set(check_df.columns))}",
            )

    def test_check_duplicate_raise_error(self):
        original_df = pd.DataFrame(
            {
                "col_1": ["1.54", "0-1", "1-n", "0-1", "1.54"],
                "col_2": ["1.54", "0-1", "1-n", "text", "neu"],
            }
        )
        utl.check_duplicate_raise_error(check_df=original_df, duplicate_column="col_2")
        with self.assertRaises(BaseError) as context:
            utl.check_duplicate_raise_error(check_df=original_df, duplicate_column="col_1")
            self.assertEqual(
                context,
                "The column '{duplicate_column}' may not contain any duplicate values. "
                "The following values appeared multiple times '{duplicate_values}'.",
            )

    def test_check_required_values(self):
        original_df = pd.DataFrame(
            {
                "col_1": ["1.54", "0-1", "1-n", pd.NA],
                "col_2": ["1", "1", pd.NA, "text"],
                "col_3": ["1", "1", "1", "text"],
            }
        )
        expected_dict = {"col_1": [False, False, False, True]}
        returned_dict = utl.check_required_values(check_df=original_df, required_values_columns=["col_1", "col_3"])
        self.assertListEqual(list(expected_dict.keys()), list(returned_dict.keys()))
        for key, expected_list in expected_dict.items():
            self.assertListEqual(list(returned_dict[key]), expected_list)

    def test_turn_bool_array_into_index_numbers(self):
        original_series = pd.Series([False, True, False, True])
        expected_list = [1, 3]
        returned_list = utl.turn_bool_array_into_index_numbers(in_series=original_series, true_remains=True)
        self.assertListEqual(expected_list, returned_list)
        expected_list = [0, 2]
        returned_list = utl.turn_bool_array_into_index_numbers(in_series=original_series, true_remains=False)
        self.assertListEqual(expected_list, returned_list)

    def test_get_wrong_row_numbers(self):
        original_dict = {
            "col_1": pd.Series([False, True, False, True]),
            "col_2": pd.Series([False, False, True, False]),
        }
        expected_dict = {"col_1": [3, 5], "col_2": [4]}
        returned_dict = utl.get_wrong_row_numbers(wrong_row_dict=original_dict, true_remains=True)
        self.assertDictEqual(expected_dict, returned_dict)

    def test_update_dict_ifnot_value_none(self):
        original_dict = {0: 0}
        original_update_dict = {1: 1, 2: 2, 3: None, 4: pd.NA, 5: "5"}
        expected_dict = {0: 0, 1: 1, 2: 2, 5: "5"}
        returned_dict = utl.update_dict_ifnot_value_none(
            additional_dict=original_update_dict, to_update_dict=original_dict
        )
        self.assertDictEqual(expected_dict, returned_dict)

    def test_find_one_full_cell_in_cols(self):
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
        returned_array = utl.find_one_full_cell_in_cols(check_df=original_df, required_columns=required_cols)
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
        returned_array = utl.find_one_full_cell_in_cols(check_df=original_df, required_columns=required_cols)
        self.assertIsNone(returned_array)

    def test_col_must_or_not_empty_based_on_other_col(self):
        original_df = pd.DataFrame({"substring": ["1", "2", "3", "4", "5", "6"], "check": [1, pd.NA, 3, 4, pd.NA, 6]})
        returned_value = utl.col_must_or_not_empty_based_on_other_col(
            check_df=original_df,
            substring_list=["1", "3", "6"],
            substring_colname="substring",
            check_empty_colname="check",
            must_have_value=True,
        )
        self.assertIsNone(returned_value)
        expected_series = pd.Series([True, False, False, False, False, False])
        returned_series = utl.col_must_or_not_empty_based_on_other_col(
            check_df=original_df,
            substring_list=["1", "2"],
            substring_colname="substring",
            check_empty_colname="check",
            must_have_value=False,
        )
        assert_series_equal(expected_series, returned_series)

    def test__get_labels(self):
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

    def test_get_comments(self):
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
        self.assertDictEqual(expected_dict, returned_dict)
        returned_dict = utl.get_comments(original_df.loc[1, :])
        self.assertIsNone(returned_dict)


if __name__ == "__main__":
    pytest.main([__file__])
