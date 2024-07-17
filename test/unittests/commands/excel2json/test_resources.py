import warnings
from typing import cast

import pandas as pd
import pytest
import regex
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json import resources as e2j
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import RequiredColumnMissingProblem
from dsp_tools.commands.excel2json.resources import _check_complete_gui_order
from dsp_tools.commands.excel2json.resources import _create_all_cardinalities
from dsp_tools.commands.excel2json.resources import _make_one_property
from dsp_tools.models.exceptions import InputError


class TestCheckCompleteGuiOrder:
    def test_column_does_not_exist(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3]})
        expected_df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, 3]})
        res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_na_in_row(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, pd.NA, pd.NA]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' are empty.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected_df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, 3]})
        with pytest.warns(Warning, match=expected_msg):
            res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_error(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, "a"]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' contain invalid characters "
            "that could not be converted to an integer.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected_df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, 3]})
        with pytest.warns(Warning, match=expected_msg):
            res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_good(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "gui_order": ["1", "2", "3"]})
        expected_df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, 3]})
        with warnings.catch_warnings(record=True) as catched_warnings:
            res = _check_complete_gui_order("class_name", df)
            assert len(catched_warnings) == 0
        assert_frame_equal(res, expected_df)


class TestCreateAllCardinalities:
    def test_na_in_row(self) -> None:
        df = pd.DataFrame({"property": ["1", "2", "3"], "cardinality": ["1-n", "1", "0-n"], "gui_order": [1, 2, pd.NA]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' are empty.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected = [
            {"propname": ":1", "gui_order": 1, "cardinality": "1-n"},
            {"propname": ":2", "gui_order": 2, "cardinality": "1"},
            {"propname": ":3", "gui_order": 3, "cardinality": "0-n"},
        ]
        with pytest.warns(Warning, match=expected_msg):
            res = _create_all_cardinalities("class_name", df)
            assert res == expected

    def test_error(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "cardinality": ["1-n", "1", "0-n"], "gui_order": [1, 2, "a"]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' contain invalid characters "
            "that could not be converted to an integer.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected = [
            {"propname": ":1", "gui_order": 1, "cardinality": "1-n"},
            {"propname": ":2", "gui_order": 2, "cardinality": "1"},
            {"propname": ":3", "gui_order": 3, "cardinality": "0-n"},
        ]
        with pytest.warns(Warning, match=expected_msg):
            res = _create_all_cardinalities("class_name", df)
            assert res == expected

    def test_good(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "cardinality": ["1-n", "1", "0-n"], "gui_order": ["1", "2", "3"]})
        expected = [
            {"propname": ":1", "gui_order": 1, "cardinality": "1-n"},
            {"propname": ":2", "gui_order": 2, "cardinality": "1"},
            {"propname": ":3", "gui_order": 3, "cardinality": "0-n"},
        ]
        with warnings.catch_warnings(record=True) as catched_warnings:
            res = _create_all_cardinalities("class_name", df)
            assert res == expected
            assert len(catched_warnings) == 0


def test_make_one_property() -> None:
    s = pd.Series(
        {
            "property": "1",
            "gui_order": 1,
            "cardinality": "1-n",
        }
    )
    expected = {
        "propname": ":1",
        "gui_order": 1,
        "cardinality": "1-n",
    }
    res = _make_one_property(s)
    assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])


def test_validate_individual_class_sheets_problems() -> None:
    sheet_good = pd.DataFrame({"property": ["p1"], "cardinality": ["0-n"]})
    sheet_missing_card = pd.DataFrame({"property": ["p2", "p3"], "cardinality": [pd.NA, "1-n"]})
    sheet_missing_prop = pd.DataFrame({"property": ["p4", pd.NA], "cardinality": ["0-1", "1"]})
    test_dict = {
        "sheet_good": sheet_good,
        "sheet_missing_card": sheet_missing_card,
        "sheet_missing_prop": sheet_missing_prop,
    }
    res = e2j._validate_individual_class_sheets(test_dict)
    assert len(res) == 1
    assert isinstance(res[0], MissingValuesProblem)
    card_problem = res[0].locations[0]
    assert card_problem.sheet == "sheet_missing_card"
    assert card_problem.column == "cardinality"
    assert card_problem.row == 2
    prop_problem = res[0].locations[1]
    assert prop_problem.sheet == "sheet_missing_prop"
    assert prop_problem.column == "property"
    assert prop_problem.row == 3


def test_validate_individual_class_sheets_missing_column() -> None:
    test_dict = {"sheet_missing_col": pd.DataFrame({"property": ["p5"]})}
    res = e2j._validate_individual_class_sheets(test_dict)
    assert len(res) == 1
    assert isinstance(res[0], ExcelSheetProblem)
    assert len(res[0].problems) == 1
    assert res[0].sheet_name == "sheet_missing_col"
    col_problem = cast(RequiredColumnMissingProblem, res[0].problems[0])
    assert col_problem.columns == ["cardinality"]


def test_failing_prepare_classes_df() -> None:
    test_dict = {"Frenchclasses": pd.DataFrame({})}
    expected_msg = regex.escape(
        "The Excel file 'resources.xlsx' contains the following problems:\n\n"
        "A sheet with the name 'classes' is mandatory in this Excel.\n"
        "The following sheets are in the file:\n"
        "    - Frenchclasses"
    )
    with pytest.raises(InputError, match=expected_msg):
        e2j._prepare_classes_df(test_dict)
