import warnings
from typing import cast

import pandas as pd
import pytest
import regex
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json import resources as e2j
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import MandatorySheetsMissingProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import RequiredColumnMissingProblem
from dsp_tools.commands.excel2json.models.input_error import ResourceSheetNotListedProblem
from dsp_tools.commands.excel2json.models.ontology import ResourceCardinality
from dsp_tools.commands.excel2json.resources import _check_complete_gui_order
from dsp_tools.commands.excel2json.resources import _create_all_cardinalities
from dsp_tools.commands.excel2json.resources import _extract_default_permissions_overrule
from dsp_tools.commands.excel2json.resources import _make_one_cardinality


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
        with pytest.warns(Warning, match=expected_msg):
            res = _create_all_cardinalities("class_name", df)
        assert isinstance(res, list)
        res = sorted(res, key=lambda x: x.propname)
        one = res[0]
        assert isinstance(one, ResourceCardinality)
        assert one.propname == ":1"
        assert one.cardinality == "1-n"
        assert one.gui_order == 1
        two = res[1]
        assert isinstance(two, ResourceCardinality)
        assert two.propname == ":2"
        assert two.cardinality == "1"
        assert two.gui_order == 2
        three = res[2]
        assert isinstance(three, ResourceCardinality)
        assert three.propname == ":3"
        assert three.cardinality == "0-n"
        assert three.gui_order == 3

    def test_error(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "cardinality": ["1-n", "1", "0-n"], "gui_order": [1, 2, "a"]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' contain invalid characters "
            "that could not be converted to an integer.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        with pytest.warns(Warning, match=expected_msg):
            res = _create_all_cardinalities("class_name", df)
        assert isinstance(res, list)
        res = sorted(res, key=lambda x: x.propname)
        one = res[0]
        assert isinstance(one, ResourceCardinality)
        assert one.propname == ":1"
        assert one.cardinality == "1-n"
        assert one.gui_order == 1
        two = res[1]
        assert isinstance(two, ResourceCardinality)
        assert two.propname == ":2"
        assert two.cardinality == "1"
        assert two.gui_order == 2
        three = res[2]
        assert isinstance(three, ResourceCardinality)
        assert three.propname == ":3"
        assert three.cardinality == "0-n"
        assert three.gui_order == 3

    def test_good(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "cardinality": ["1-n", "1", "0-n"], "gui_order": ["1", "2", "3"]})
        with warnings.catch_warnings(record=True) as catched_warnings:
            res = _create_all_cardinalities("class_name", df)
            assert isinstance(res, list)
            res = sorted(res, key=lambda x: x.propname)
            one = res[0]
            assert isinstance(one, ResourceCardinality)
            assert one.propname == ":1"
            assert one.cardinality == "1-n"
            assert one.gui_order == 1
            two = res[1]
            assert isinstance(two, ResourceCardinality)
            assert two.propname == ":2"
            assert two.cardinality == "1"
            assert two.gui_order == 2
            three = res[2]
            assert isinstance(three, ResourceCardinality)
            assert three.propname == ":3"
            assert three.cardinality == "0-n"
            assert three.gui_order == 3
            assert len(catched_warnings) == 0


def test_make_one_property() -> None:
    s = pd.Series(
        {
            "property": "1",
            "gui_order": 1,
            "cardinality": "1-n",
        }
    )
    res = _make_one_cardinality(s)
    assert isinstance(res, ResourceCardinality)
    assert res.propname == ":1"
    assert res.cardinality == "1-n"
    assert res.gui_order == 1


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


def test_failing_validate_excel_file() -> None:
    test_dict = {"Frenchclasses": pd.DataFrame({})}
    res = e2j._validate_excel_file(test_dict)
    assert isinstance(res, ExcelFileProblem)
    assert len(res.problems) == 1
    missing = res.problems[0]
    assert isinstance(missing, MandatorySheetsMissingProblem)
    assert missing.existing_sheets == ["Frenchclasses"]
    assert missing.mandatory_sheet == ["classes"]


def test_extract_default_permissions_overrule() -> None:
    df_dict = {
        "name": ["resource1", "resource2", "resource3", "resource4", "resource5", "resource6"],
        "default_permissions_overrule": ["private", "limited_view", "Private", "LIMITED_VIEW", pd.NA, "other_value"],
    }
    test_df = pd.DataFrame(df_dict)
    result = _extract_default_permissions_overrule(test_df)
    assert result.private == ["resource1", "resource3"]
    assert result.limited_view == ["resource2", "resource4"]


class TestValidateClassesExcelSheet:
    def test_missing_sheet(self) -> None:
        test_df = pd.DataFrame({"name": ["name"], "super": ["super"]})
        res = e2j._validate_classes_excel_sheet(test_df, {"other", "name"})
        assert isinstance(res, ExcelSheetProblem)
        assert len(res.problems) == 1
        missing_sheet = res.problems[0]
        assert isinstance(missing_sheet, ResourceSheetNotListedProblem)
        assert missing_sheet.missing_names == {"other"}

    def test_good_no_sheets(self) -> None:
        test_df = pd.DataFrame({"name": ["name"], "super": ["super"]})
        res = e2j._validate_classes_excel_sheet(test_df, set())
        assert not res

    def test_good_with_sheet(self) -> None:
        test_df = pd.DataFrame({"name": ["name"], "super": ["super"]})
        res = e2j._validate_classes_excel_sheet(test_df, {"name"})
        assert not res


if __name__ == "__main__":
    pytest.main([__file__])
