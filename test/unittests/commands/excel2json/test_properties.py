import unittest
from typing import Any
from typing import cast

import pandas as pd
import pytest
import regex
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json import properties as e2j
from dsp_tools.commands.excel2json.models.input_error import InvalidExcelContentProblem
from dsp_tools.commands.excel2json.models.input_error import PropertyProblem
from dsp_tools.commands.excel2json.models.ontology import GuiAttributes
from dsp_tools.commands.excel2json.models.ontology import OntoProperty
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
        returned_df = e2j._rename_deprecated_lang_cols(df=original_df)
        assert_frame_equal(expected_df, returned_df)
        returned_df = e2j._rename_deprecated_lang_cols(df=expected_df)
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

        e2j._do_property_excel_compliance(df=original_df)

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
                "The Excel file 'properties.xlsx' contains the following problems:\n\n"
                "At the following locations, mandatory values are missing:\n"
                "    - Column 'name' | Row 9\n"
                "    - Column 'super' | Row 2\n"
                "    - Column 'super' | Row 4\n"
                "    - Column 'super' | Row 9\n"
                "    - Column 'object' | Row 5\n"
                "    - Column 'object' | Row 9\n"
                "    - Column 'gui_element' | Row 6\n"
                "    - Column 'gui_element' | Row 8\n"
                "    - Column 'gui_element' | Row 9\n"
                "    - Column 'label' | Row 3\n"
                "    - Column 'label' | Row 8\n"
                "    - Column 'gui_attributes' | Row 7"
            )
        )
        with pytest.raises(InputError, match=expected_msg):
            e2j._do_property_excel_compliance(original_df)

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_rename_deprecated_hlist(self) -> None:
        original_df = pd.DataFrame({"hlist": [pd.NA, pd.NA, "languages"]})
        expected_df = pd.DataFrame({"gui_attributes": [pd.NA, pd.NA, "hlist:languages"]})
        returned_df = e2j._rename_deprecated_hlist(df=original_df)
        assert_frame_equal(expected_df, returned_df)

        original_df = pd.DataFrame(
            {"hlist": [pd.NA, pd.NA, "languages"], "gui_attributes": [pd.NA, "attribute_1", pd.NA]}
        )
        expected_df = pd.DataFrame({"gui_attributes": [pd.NA, "attribute_1", "hlist:languages"]})
        returned_df = e2j._rename_deprecated_hlist(df=original_df)
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
        self.assertIsNone(e2j._get_gui_attribute(df_row=cast("pd.Series[Any]", original_df.loc[0, :]), row_num=2))

        res_1 = e2j._get_gui_attribute(df_row=cast("pd.Series[Any]", original_df.loc[1, :]), row_num=3)
        assert isinstance(res_1, InvalidExcelContentProblem)
        assert res_1.excel_position.row == 3
        assert res_1.actual_content == "max:1.4 / min:1.2"

        res_2 = e2j._get_gui_attribute(df_row=cast("pd.Series[Any]", original_df.loc[2, :]), row_num=4)
        assert isinstance(res_2, InvalidExcelContentProblem)
        assert res_2.excel_position.row == 4
        assert res_2.actual_content == "hlist:"

        res_3 = e2j._get_gui_attribute(df_row=cast("pd.Series[Any]", original_df.loc[3, :]), row_num=5)
        assert isinstance(res_3, InvalidExcelContentProblem)
        assert res_3.excel_position.row == 5
        assert res_3.actual_content == "234345"

        expected_dict = {"hlist": "languages"}
        returned_dict = e2j._get_gui_attribute(df_row=cast("pd.Series[Any]", original_df.loc[4, :]), row_num=6)
        assert isinstance(returned_dict, GuiAttributes)
        self.assertDictEqual(expected_dict, returned_dict.serialise())

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
        assert returned_dict
        casted_dict = {"gui_attributes": list(returned_dict["gui_attributes"])}
        self.assertDictEqual(expected_dict, casted_dict)

    def test_get_final_series_two_series(self) -> None:
        mandatory_check = pd.Series([True, True, False])
        no_attribute_check = pd.Series([True, False, False])
        expected = pd.Series([True, True, False])
        result = e2j._get_final_series(mandatory_check, no_attribute_check)
        self.assertEqual(list(result), list(expected))  # type: ignore[arg-type]

    def test_get_final_series_one_series_one_None(self) -> None:
        mandatory_check = pd.Series([True, True, False])
        no_attribute_check = None
        expected = pd.Series([True, True, False])
        result = e2j._get_final_series(mandatory_check, no_attribute_check)
        self.assertEqual(list(result), list(expected))  # type: ignore[arg-type]

    def test_get_final_series_one_None_one_series(self) -> None:
        mandatory_check = None
        no_attribute_check = pd.Series([True, False, False])
        expected = pd.Series([True, False, False])
        result = e2j._get_final_series(mandatory_check, no_attribute_check)
        self.assertEqual(list(result), list(expected))  # type: ignore[arg-type]

    def test_get_final_series_two_None(self) -> None:
        mandatory_check = None
        no_attribute_check = None
        expected = None
        result = e2j._get_final_series(mandatory_check, no_attribute_check)
        self.assertEqual(result, expected)

    def test_row2prop_problem(self) -> None:
        test_series = pd.Series(
            {
                "name": "name_1",
                "label_en": "label_en",
                "label_de": "label_de",
                "label_fr": "label_fr",
                "label_it": "label_it",
                "label_rm": "label_rm",
                "comment_en": "comment_en",
                "comment_de": "comment_de",
                "comment_fr": "comment_fr",
                "comment_it": "comment_it",
                "comment_rm": "comment_rm",
                "super": "super_1",
                "subject": "subject_1",
                "object": "object_1",
                "gui_element": "Simple",
                "gui_attributes": "max:1.4 / min:1.2",
            }
        )
        res = e2j._row2prop(test_series, row_num=0)
        assert isinstance(res, PropertyProblem)
        assert res.prop_name == "name_1"
        assert len(res.problems) == 1
        invalid = res.problems[0]
        assert isinstance(invalid, InvalidExcelContentProblem)
        assert invalid.actual_content == "max:1.4 / min:1.2"
        assert invalid.expected_content == "attribute: value, attribute: value"

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
        returned_prop = e2j._row2prop(df_row=cast("pd.Series[Any]", original_df.loc[0, :]), row_num=0)
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
        assert isinstance(returned_prop, OntoProperty)
        self.assertDictEqual(expected_dict, returned_prop.serialise())

        returned_prop = e2j._row2prop(df_row=cast("pd.Series[Any]", original_df.loc[1, :]), row_num=1)
        expected_dict = {
            "comments": {"en": "comment_en_2"},
            "gui_element": "Date",
            "labels": {"en": "label_en_2"},
            "name": "name_2",
            "object": "object_2",
            "subject": "subject_2",
            "super": ["super_2.1", "super_2.2"],
        }
        assert isinstance(returned_prop, OntoProperty)
        self.assertDictEqual(expected_dict, returned_prop.serialise())

        returned_prop = e2j._row2prop(df_row=cast("pd.Series[Any]", original_df.loc[2, :]), row_num=2)
        expected_dict = {
            "comments": {"de": "comment_de_3"},
            "gui_attributes": {"hlist": "languages"},
            "gui_element": "List",
            "labels": {"de": "label_de_3"},
            "name": "name_3",
            "object": "object_3",
            "super": ["super_3"],
        }
        assert isinstance(returned_prop, OntoProperty)
        self.assertDictEqual(expected_dict, returned_prop.serialise())


if __name__ == "__main__":
    pytest.main([__file__])
