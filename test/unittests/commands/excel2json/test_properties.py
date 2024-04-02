import unittest
from typing import Any
from typing import cast

import pandas as pd
import pytest
import regex
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json import properties as e2j
from dsp_tools.commands.excel2json.models.input_error import InvalidExcelContentProblem
from dsp_tools.models.exceptions import InputError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestFunctions(unittest.TestCase):
    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_rename_deprecated_lang_cols(self) -> None:
        original_df = pd.DataFrame(
            {"en": [1, 2, 3], "de": [1, 2, 3], "fr": [1, 2, 3], "it": [1, 2, 3], "rm": [1, 2, 3]}
        )
        expected_df = pd.DataFrame(
            {
                "label_en": [1, 2, 3],
                "label_de": [1, 2, 3],
                "label_fr": [1, 2, 3],
                "label_it": [1, 2, 3],
                "label_rm": [1, 2, 3],
            }
        )
        returned_df = e2j._rename_deprecated_lang_cols(df=original_df, excelfile="Test")
        assert_frame_equal(expected_df, returned_df)
        returned_df = e2j._rename_deprecated_lang_cols(df=expected_df, excelfile="Test")
        assert_frame_equal(expected_df, returned_df)

    def test_do_property_excel_compliance_all_good(self) -> None:
        original_df = pd.DataFrame(
            {
                "name": ["name_1", "name_2", "name_3", "name_4", "name_5", "name_6"],
                "label_en": ["label_en_1", "label_en_2", pd.NA, pd.NA, "label_en_5", pd.NA],
                "label_de": ["label_de_1", pd.NA, "label_de_3", pd.NA, pd.NA, pd.NA],
                "label_fr": ["label_fr_1", pd.NA, pd.NA, "label_fr_4", pd.NA, pd.NA],
                "label_it": ["label_it_1", pd.NA, pd.NA, pd.NA, "label_it_5", pd.NA],
                "label_rm": ["label_rm_1", pd.NA, pd.NA, pd.NA, pd.NA, "label_rm_6"],
                "comment_en": ["comment_en_1", "comment_en_2", pd.NA, pd.NA, "comment_en_5", pd.NA],
                "comment_de": ["comment_de_1", pd.NA, "comment_de_3", pd.NA, pd.NA, pd.NA],
                "comment_fr": ["comment_fr_1", pd.NA, pd.NA, "comment_fr_4", pd.NA, pd.NA],
                "comment_it": ["comment_it_1", pd.NA, pd.NA, pd.NA, "comment_it_5", pd.NA],
                "comment_rm": ["comment_rm_1", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
                "super": ["super_1", "super_2", "super_3", "super_4.1, super_4.2, super_4.3", "super_5", "super_6"],
                "subject": ["subject_1", "subject_2", "subject_3", "subject_4", "subject_5", "subject_6"],
                "object": ["object_1", "object_2", "object_3", "object_4", "object_5", "object_6"],
                "gui_element": ["Simple", "Searchbox", "Date", "Searchbox", "List", "Searchbox"],
                "gui_attributes": ["size: 32, maxlength: 128", pd.NA, pd.NA, pd.NA, "hlist: languages", pd.NA],
            }
        )

        e2j._do_property_excel_compliance(df=original_df, excelfile="Test")

    def test_do_property_excel_compliance_problems(self) -> None:
        original_df = pd.DataFrame(
            {
                "name": ["name_1", "name_2", "name_3", "name_4", "name_5", "name_6", "name_7", pd.NA],
                "label_en": ["label_en_1", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
                "label_de": [pd.NA, pd.NA, "label_de_3", pd.NA, pd.NA, pd.NA, pd.NA, "label_de_8"],
                "label_fr": [pd.NA, pd.NA, pd.NA, "label_fr_4", pd.NA, pd.NA, pd.NA, pd.NA],
                "label_it": [pd.NA, pd.NA, pd.NA, pd.NA, "label_it_5", pd.NA, pd.NA, pd.NA],
                "label_rm": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "label_rm_6", pd.NA, pd.NA],
                "comment_en": ["comment_en_1", pd.NA, "comment_en_3", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
                "comment_de": [pd.NA, pd.NA, pd.NA, "comment_de_4", pd.NA, pd.NA, pd.NA, pd.NA],
                "comment_fr": [pd.NA, pd.NA, pd.NA, pd.NA, "comment_fr_5", pd.NA, pd.NA, pd.NA],
                "comment_it": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "comment_it_6", pd.NA, pd.NA],
                "comment_rm": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "comment_rm_7", pd.NA],
                "super": [
                    pd.NA,
                    "super_2",
                    pd.NA,
                    "super_4.1, super_4.2, super_4.3",
                    "super_5",
                    "super_6",
                    "super_7",
                    pd.NA,
                ],
                "subject": [
                    "subject_1",
                    "subject_2",
                    "subject_3",
                    "subject_4",
                    "subject_5",
                    "subject_6",
                    "subject_7",
                    pd.NA,
                ],
                "object": ["object_1", "object_2", "object_3", pd.NA, "object_5", "object_6", "object_7", pd.NA],
                "gui_element": ["Simple", "Searchbox", "Date", "Date", pd.NA, "List", pd.NA, pd.NA],
                "gui_attributes": ["size: 32, maxlength: 128", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        expected_msg = regex.escape(
            (
                "There is a problem with the excel file: 'Test'\n\n"
                "The column 'name' must have values in the row(s):\n"
                "    - 9\n\n"
                "The column 'super' must have values in the row(s):\n"
                "    - 2\n"
                "    - 4\n"
                "    - 9\n\n"
                "The column 'object' must have values in the row(s):\n"
                "    - 5\n"
                "    - 9\n\n"
                "The column 'gui_element' must have values in the row(s):\n"
                "    - 6\n"
                "    - 8\n"
                "    - 9\n\n"
                "The column 'label' must have values in the row(s):\n"
                "    - 3\n"
                "    - 8\n\n"
                "The column 'gui_attributes' must have values in the row(s):\n"
                "    - 7"
            )
        )
        with pytest.raises(InputError, match=expected_msg):
            e2j._do_property_excel_compliance(original_df, "Test")

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_rename_deprecated_hlist(self) -> None:
        original_df = pd.DataFrame({"hlist": [pd.NA, pd.NA, "languages"]})
        expected_df = pd.DataFrame({"gui_attributes": [pd.NA, pd.NA, "hlist:languages"]})
        returned_df = e2j._rename_deprecated_hlist(df=original_df, excelfile="Test")
        assert_frame_equal(expected_df, returned_df)

        original_df = pd.DataFrame(
            {"hlist": [pd.NA, pd.NA, "languages"], "gui_attributes": [pd.NA, "attribute_1", pd.NA]}
        )
        expected_df = pd.DataFrame({"gui_attributes": [pd.NA, "attribute_1", "hlist:languages"]})
        returned_df = e2j._rename_deprecated_hlist(df=original_df, excelfile="Test")
        assert_frame_equal(expected_df, returned_df)

    def test_unpack_gui_attributes(self) -> None:
        test_dict = {
            "maxlength:1, size:32": {"maxlength": "1", "size": "32"},
            "hlist: languages": {"hlist": "languages"},
        }
        for original, expected in test_dict.items():
            self.assertDictEqual(e2j._unpack_gui_attributes(attribute_str=original), expected)

    def test_search_convert_numbers(self) -> None:
        test_dict = {"1": 1, "string": "string", "1.453": 1.453, "sdf.asdf": "sdf.asdf"}
        for original, expected in test_dict.items():
            self.assertEqual(e2j._search_convert_numbers_in_str(value_str=original), expected)

    def test_get_gui_attribute(self) -> None:
        original_df = pd.DataFrame(
            {"gui_attributes": [pd.NA, "max:1.4 / min:1.2", "hlist:", "234345", "hlist: languages,"]}
        )
        self.assertIsNone(e2j._get_gui_attribute(df_row=cast(pd.Series[Any], original_df.loc[0, :]), row_num=2))

        res_1 = e2j._get_gui_attribute(df_row=cast(pd.Series[Any], original_df.loc[1, :]), row_num=3)
        res_problem_1 = cast(InvalidExcelContentProblem, res_1)
        assert res_problem_1.excel_position.row == 3
        assert res_problem_1.actual_content == "max:1.4 / min:1.2"

        res_2 = e2j._get_gui_attribute(df_row=cast(pd.Series[Any], original_df.loc[2, :]), row_num=4)
        res_problem_2 = cast(InvalidExcelContentProblem, res_2)
        assert res_problem_2.excel_position.row == 4
        assert res_problem_2.actual_content == "hlist:"

        res_3 = e2j._get_gui_attribute(df_row=cast(pd.Series[Any], original_df.loc[3, :]), row_num=5)
        res_problem_3 = cast(InvalidExcelContentProblem, res_3)
        assert res_problem_3.excel_position.row == 5
        assert res_problem_3.actual_content == "234345"

        expected_dict = {"hlist": "languages"}
        returned_dict = e2j._get_gui_attribute(df_row=cast(pd.Series[Any], original_df.loc[4, :]), row_num=6)
        self.assertDictEqual(expected_dict, cast(dict[str, str], returned_dict))

    def test_check_compliance_gui_attributes_all_good(self) -> None:
        original_df = pd.DataFrame(
            {
                "gui_element": ["Spinbox", "List", "Searchbox", "Date", "Geonames", "Richtext", "TimeStamp"],
                "gui_attributes": ["Spinbox_attr", "List_attr", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        assert not e2j._check_compliance_gui_attributes(df=original_df)

    def test_check_compliance_gui_attributes(self) -> None:
        original_df = pd.DataFrame(
            {
                "gui_element": ["Spinbox", "List", "Searchbox", "Date", "Geonames", "Richtext", "TimeStamp"],
                "gui_attributes": ["Spinbox_attr", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "TimeStamp_attr"],
            }
        )
        expected_dict = {"gui_attributes": [False, True, False, False, False, False, True]}
        returned_dict = e2j._check_compliance_gui_attributes(df=original_df)
        returned_dict = cast(dict[str, pd.Series[Any]], returned_dict)
        casted_dict: dict[str, Any] = {"gui_attributes": list(returned_dict["gui_attributes"])}
        self.assertDictEqual(expected_dict, casted_dict)

    def test_row2prop(self) -> None:
        original_df = pd.DataFrame(
            {
                "name": ["name_1", "name_2", "name_3"],
                "label_en": ["label_en_1", "label_en_2", pd.NA],
                "label_de": ["label_de_1", pd.NA, "label_de_3"],
                "label_fr": ["label_fr_1", pd.NA, pd.NA],
                "label_it": ["label_it_1", pd.NA, pd.NA],
                "label_rm": ["label_rm_1", pd.NA, pd.NA],
                "comment_en": ["comment_en_1", "comment_en_2", pd.NA],
                "comment_de": ["comment_de_1", pd.NA, "comment_de_3"],
                "comment_fr": ["comment_fr_1", pd.NA, pd.NA],
                "comment_it": ["comment_it_1", pd.NA, pd.NA],
                "comment_rm": ["comment_rm_1", pd.NA, pd.NA],
                "super": ["super_1", "super_2.1, super_2.2", "super_3"],
                "subject": ["subject_1", "subject_2", pd.NA],
                "object": ["object_1", "object_2", "object_3"],
                "gui_element": ["Simple", "Date", "List"],
                "gui_attributes": ["size: 32, maxlength: 128", pd.NA, "hlist: languages"],
            }
        )
        returned_dict = e2j._row2prop(df_row=cast(pd.Series[Any], original_df.loc[0, :]), row_num=0, excelfile="Test")
        expected_dict = {
            "name": "name_1",
            "object": "object_1",
            "subject": "subject_1",
            "gui_element": "Simple",
            "labels": {
                "en": "label_en_1",
                "de": "label_de_1",
                "fr": "label_fr_1",
                "it": "label_it_1",
                "rm": "label_rm_1",
            },
            "super": ["super_1"],
            "comments": {
                "en": "comment_en_1",
                "de": "comment_de_1",
                "fr": "comment_fr_1",
                "it": "comment_it_1",
                "rm": "comment_rm_1",
            },
            "gui_attributes": {"size": 32, "maxlength": 128},
        }
        self.assertDictEqual(expected_dict, returned_dict)

        returned_dict = e2j._row2prop(df_row=cast(pd.Series[Any], original_df.loc[1, :]), row_num=1, excelfile="Test")
        expected_dict = {
            "comments": {"en": "comment_en_2"},
            "gui_element": "Date",
            "labels": {"en": "label_en_2"},
            "name": "name_2",
            "object": "object_2",
            "subject": "subject_2",
            "super": ["super_2.1", "super_2.2"],
        }
        self.assertDictEqual(expected_dict, returned_dict)

        returned_dict = e2j._row2prop(df_row=cast(pd.Series[Any], original_df.loc[2, :]), row_num=2, excelfile="Test")
        expected_dict = {
            "comments": {"de": "comment_de_3"},
            "gui_attributes": {"hlist": "languages"},
            "gui_element": "List",
            "labels": {"de": "label_de_3"},
            "name": "name_3",
            "object": "object_3",
            "super": ["super_3"],
        }
        self.assertDictEqual(expected_dict, returned_dict)


def test_add_optional_columns_with_missing_cols() -> None:
    original_df = pd.DataFrame(
        {
            "comment_en": ["text_en", pd.NA],
            "comment_it": ["text_it", pd.NA],
            "comment_rm": [pd.NA, pd.NA],
        }
    )
    expected_df = pd.DataFrame(
        {
            "comment_de": [pd.NA, pd.NA],
            "comment_en": ["text_en", pd.NA],
            "comment_fr": [pd.NA, pd.NA],
            "comment_it": ["text_it", pd.NA],
            "comment_rm": [pd.NA, pd.NA],
            "label_de": [pd.NA, pd.NA],
            "label_en": [pd.NA, pd.NA],
            "label_fr": [pd.NA, pd.NA],
            "label_it": [pd.NA, pd.NA],
            "label_rm": [pd.NA, pd.NA],
            "subject": [pd.NA, pd.NA],
        }
    )
    returned_df = e2j._add_optional_columns(df=original_df)
    # as the columns are extracted via a set, they are not sorted and may appear in any order,
    # this would cause the validation to fail
    returned_df = returned_df.sort_index(axis=1)
    assert_frame_equal(expected_df, returned_df)


def test_add_optional_columns_no_missing_cols() -> None:
    expected_df = pd.DataFrame(
        {
            "comment_de": [pd.NA, pd.NA],
            "comment_en": ["text_en", pd.NA],
            "comment_fr": [pd.NA, pd.NA],
            "comment_it": ["text_it", pd.NA],
            "comment_rm": [pd.NA, pd.NA],
            "label_de": [pd.NA, pd.NA],
            "label_en": [pd.NA, pd.NA],
            "label_fr": [pd.NA, pd.NA],
            "label_it": [pd.NA, pd.NA],
            "label_rm": [pd.NA, pd.NA],
            "subject": [pd.NA, pd.NA],
        }
    )
    unchanged_df = e2j._add_optional_columns(df=expected_df)
    assert_frame_equal(expected_df, unchanged_df)


if __name__ == "__main__":
    pytest.main([__file__])
