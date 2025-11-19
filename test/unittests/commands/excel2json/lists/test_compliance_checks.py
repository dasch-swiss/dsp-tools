import warnings

import pandas as pd
import pytest
import regex

from dsp_tools.commands.excel2json.lists.compliance_checks import _check_duplicates_all_excels
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_duplicate_custom_id_all_excels
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_duplicate_nodes_one_df
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_erroneous_entries_all_excels
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_erroneous_entries_one_column_level
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_erroneous_entries_one_grouped_df
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_erroneous_entries_one_list
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_erroneous_node_info_one_df
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_missing_translations_all_excels
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_missing_translations_one_column_group
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_missing_translations_one_sheet
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_for_unique_list_names
from dsp_tools.commands.excel2json.lists.compliance_checks import (
    _check_if_all_translations_in_all_column_levels_present_one_sheet,
)
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_missing_translations_one_row
from dsp_tools.commands.excel2json.lists.compliance_checks import _check_warn_unusual_columns_one_sheet
from dsp_tools.commands.excel2json.lists.compliance_checks import _make_shape_compliance_all_excels
from dsp_tools.commands.excel2json.lists.compliance_checks import _make_shape_compliance_one_sheet
from dsp_tools.commands.excel2json.lists.compliance_checks import make_all_excel_compliance_checks
from dsp_tools.commands.excel2json.lists.models.deserialise import Columns
from dsp_tools.commands.excel2json.lists.models.deserialise import ExcelSheet
from dsp_tools.commands.excel2json.lists.models.input_error import DuplicatesCustomIDInProblem
from dsp_tools.commands.excel2json.lists.models.input_error import DuplicatesInSheetProblem
from dsp_tools.commands.excel2json.lists.models.input_error import ListSheetComplianceProblem
from dsp_tools.commands.excel2json.lists.models.input_error import ListSheetContentProblem
from dsp_tools.commands.excel2json.lists.models.input_error import MinimumRowsProblem
from dsp_tools.commands.excel2json.lists.models.input_error import MissingExpectedColumn
from dsp_tools.commands.excel2json.lists.models.input_error import MissingNodeColumn
from dsp_tools.commands.excel2json.lists.models.input_error import MissingNodeTranslationProblem
from dsp_tools.commands.excel2json.lists.models.input_error import MissingTranslationsSheetProblem
from dsp_tools.commands.excel2json.lists.models.input_error import NodesPerRowProblem
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import InputError


class TestMakeAllExcelComplianceChecks:
    def test_good(self, f1_s1_good_en: ExcelSheet, f2_s2_good_en_de: ExcelSheet) -> None:
        make_all_excel_compliance_checks([f1_s1_good_en, f2_s2_good_en_de])

    def test_duplicates(self, cols_en_1: Columns) -> None:
        df_1 = pd.DataFrame({"id (optional)": [1, 2], "en_list": ["list2", "list2"], "en_1": [pd.NA, 1]})
        df_2 = pd.DataFrame({"id (optional)": [1, 4], "en_list": ["list2", "list2"], "en_1": [pd.NA, 1]})
        all_sheets = [
            ExcelSheet(excel_name="file1", sheet_name="sheet2", df=df_1, col_info=cols_en_1),
            ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df_2, col_info=cols_en_1),
        ]
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "No duplicates are allowed in the 'ID (optional)' column. At the following locations, IDs are duplicated:"
            "\n----------------------------\n"
            "ID: '1'\n"
            "    - Excel 'file1' | Sheet 'sheet2' | Row 2\n"
            "    - Excel 'file2' | Sheet 'sheet2' | Row 2"
        )
        with pytest.raises(InputError, match=expected):
            make_all_excel_compliance_checks(all_sheets)

    def test_duplicate_list_names(self, cols_en_1_no_comments: Columns) -> None:
        df_1 = pd.DataFrame({"id (optional)": [1, 2], "en_list": ["list2", "list2"], "en_1": [pd.NA, 1]})
        df_2 = pd.DataFrame({"id (optional)": [3, 4], "en_list": ["list2", "list2"], "en_1": [pd.NA, 1]})
        all_sheets = [
            ExcelSheet(excel_name="file1", sheet_name="sheet2", df=df_1, col_info=cols_en_1_no_comments),
            ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df_2, col_info=cols_en_1_no_comments),
        ]
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "The name of the list must be unique across all the excel sheets.\n"
            "The following sheets have lists with the same name:\n"
            "    - Excel file: 'file1', Sheet: 'sheet2', List: 'list2'\n"
            "    - Excel file: 'file2', Sheet: 'sheet2', List: 'list2'"
        )
        with pytest.raises(InputError, match=expected):
            make_all_excel_compliance_checks(all_sheets)

    def test_content_compliance(self, f1_s1_good_en: ExcelSheet, f2_s2_missing_translations: ExcelSheet) -> None:
        all_sheets = [f1_s1_good_en, f2_s2_missing_translations]
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "The Excel file 'file2' contains the following problems:\n\n"
            "The excel sheet 'sheet2' has the following problem(s):\n"
            "In one list, all the nodes must be translated into all the languages used. "
            "For the following nodes, the translations are missing:\n"
            "    - Row Number: 2 | Column(s): de_list\n"
            "    - Row Number: 3 | Column(s): en_1\n"
            "    - Row Number: 5 | Column(s): de_comments\n"
            "    - Row Number: 6 | Column(s): en_1, en_2, en_list"
        )
        with pytest.raises(InputError, match=expected):
            make_all_excel_compliance_checks(all_sheets)


class TestFormalExcelCompliance:
    def test_good(self, f1_s1_good_en: ExcelSheet, f2_s2_good_en_de: ExcelSheet) -> None:
        all_sheets = [f1_s1_good_en, f2_s2_good_en_de]
        _make_shape_compliance_all_excels(all_sheets)

    def test_problem(
        self, f1_s1_no_list_columns: ExcelSheet, f2_s2_missing_lang_column: ExcelSheet, f2_s3_one_row: ExcelSheet
    ) -> None:
        all_sheets = [f1_s1_no_list_columns, f2_s2_missing_lang_column, f2_s3_one_row]
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "The Excel file 'file1' contains the following problems:\n\n"
            "The excel sheet 'sheet1' has the following problem(s):\n"
            "    - At least one column for the node names in the format '[lang]_[column_number]' is required. "
            "The allowed language tags are: en, de, fr, it, rm."
            "\n\n---------------------------------------\n\n"
            "The Excel file 'file2' contains the following problems:\n\n"
            "The excel sheet 'sheet2' has the following problem(s):\n"
            "    - All nodes and lists must be translated into the same languages. "
            "Based on the languages used, the following column(s) are missing: de_3"
            "\n----------------------------\n"
            "The excel sheet 'sheet3' has the following problem(s):\n"
            "    - The Excel sheet must contain at least two rows, "
            "one for the list name and one row for a minimum of one node."
        )

        with pytest.raises(InputError, match=expected):
            _make_shape_compliance_all_excels(all_sheets)


class TestCheckExcelsForDuplicates:
    def test_good(self, f1_s1_good_en: ExcelSheet, f2_s2_good_en_de: ExcelSheet) -> None:
        all_sheets = [f1_s1_good_en, f2_s2_good_en_de]
        _check_duplicates_all_excels(all_sheets)

    def test_problem(self, f1_s1_identical_row: ExcelSheet) -> None:
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "The Excel file 'file1' contains the following problems:\n\n"
            "The excel sheet 'sheet1' contains rows that are completely identical "
            "(excluding the column 'ID (optional)'). The following rows are duplicates:\n"
            "    - 3\n"
            "    - 4"
        )
        with pytest.raises(InputError, match=expected):
            _check_duplicates_all_excels([f1_s1_identical_row])

    def test_problem_duplicate_id(self, sheets_duplicate_id: list[ExcelSheet]) -> None:
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "No duplicates are allowed in the 'ID (optional)' column. At the following locations, IDs are duplicated:\n"
            "----------------------------\n"
            "ID: '1'\n"
            "    - Excel 'file1' | Sheet 'sheet1' | Row 3\n"
            "    - Excel 'file2' | Sheet 'sheet2' | Row 2\n"
            "----------------------------\n"
            "ID: '4'\n"
            "    - Excel 'file1' | Sheet 'sheet1' | Row 5\n"
            "    - Excel 'file2' | Sheet 'sheet2' | Row 4"
        )
        with pytest.raises(InputError, match=expected):
            _check_duplicates_all_excels(sheets_duplicate_id)


class TestCheckForDuplicateListNames:
    def test_good(self, cols_en_list_only: Columns) -> None:
        df_1 = pd.DataFrame({"en_list": ["list1", "list1"]})
        df_2 = pd.DataFrame({"en_list": ["list2", "list2"]})
        all_sheets = [
            ExcelSheet(excel_name="file1", sheet_name="sheet1", df=df_1, col_info=cols_en_list_only),
            ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df_2, col_info=cols_en_list_only),
        ]
        _check_for_unique_list_names(all_sheets)

    def test_problem(self, cols_en_list_only: Columns) -> None:
        df_1 = pd.DataFrame({"en_list": ["list1", "list2"]})
        df_2 = pd.DataFrame({"en_list": ["list2", "list2"]})
        df_3 = pd.DataFrame({"en_list": ["list2", "list2"]})
        all_sheets = [
            ExcelSheet(excel_name="file1", sheet_name="sheet1", df=df_1, col_info=cols_en_list_only),
            ExcelSheet(excel_name="file1", sheet_name="sheet2", df=df_2, col_info=cols_en_list_only),
            ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df_3, col_info=cols_en_list_only),
        ]
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "The Excel file 'file1' contains the following problems:\n\n"
            "Per Excel sheet only one list is allowed.\n"
            "The sheet 'sheet1' has more than one list, namely the following: list1, list2"
            "\n\n---------------------------------------\n\n"
            "The name of the list must be unique across all the excel sheets.\n"
            "The following sheets have lists with the same name:\n"
            "    - Excel file: 'file1', Sheet: 'sheet1', List: 'list2'\n"
            "    - Excel file: 'file1', Sheet: 'sheet2', List: 'list2'\n"
            "    - Excel file: 'file2', Sheet: 'sheet2', List: 'list2'"
        )
        with pytest.raises(InputError, match=expected):
            _check_for_unique_list_names(all_sheets)


class TestCheckForDuplicates:
    def test_good(self, cols_en_1: Columns) -> None:
        test_df = pd.DataFrame({"en_list": ["a", "b", "c"], "en_1": ["d", "e", "f"]})
        test_sheet = ExcelSheet(excel_name="", sheet_name="sheet", df=test_df, col_info=cols_en_1)
        assert not _check_for_duplicate_nodes_one_df(test_sheet)

    def test_problem(self, cols_en_1_2: Columns) -> None:
        test_df = pd.DataFrame({"en_list": ["a", "a", "a"], "en_1": ["b", "b", "b"], "en_2": ["d", "c", "d"]})
        test_sheet = ExcelSheet(excel_name="excel", sheet_name="sheet", df=test_df, col_info=cols_en_1_2)
        res = _check_for_duplicate_nodes_one_df(test_sheet)
        assert isinstance(res, DuplicatesInSheetProblem)
        assert res.excel_name == "excel"
        assert res.sheet_name == "sheet"
        assert res.rows == [0, 2]

    def test_check_for_duplicate_custom_id_all_excels_good(
        self, f1_s1_good_en: ExcelSheet, f2_s2_good_en_de: ExcelSheet
    ) -> None:
        sheets = [f1_s1_good_en, f2_s2_good_en_de]
        assert not _check_for_duplicate_custom_id_all_excels(sheets)

    def test_check_for_duplicate_custom_id_all_excels_problem(self, sheets_duplicate_id: list[ExcelSheet]) -> None:
        result = _check_for_duplicate_custom_id_all_excels(sheets_duplicate_id)
        assert isinstance(result, DuplicatesCustomIDInProblem)
        assert len(result.duplicate_ids) == 2
        one = result.duplicate_ids[0]
        assert one.custom_id == 1
        assert len(one.excel_locations) == 2
        locations = sorted(one.excel_locations, key=lambda x: x.excel_filename)  # type: ignore[return-value,arg-type]
        assert locations[0].excel_filename == "file1"
        assert locations[0].sheet == "sheet1"
        assert locations[0].row == 3
        assert locations[1].excel_filename == "file2"
        assert locations[1].sheet == "sheet2"
        assert locations[1].row == 2
        two = result.duplicate_ids[1]
        assert two.custom_id == 4
        assert len(two.excel_locations) == 2
        locations = sorted(two.excel_locations, key=lambda x: x.excel_filename)  # type: ignore[return-value,arg-type]
        assert locations[0].excel_filename == "file1"
        assert locations[0].sheet == "sheet1"
        assert locations[0].row == 5
        assert locations[1].excel_filename == "file2"
        assert locations[1].sheet == "sheet2"
        assert locations[1].row == 4


class TestShapeCompliance:
    def test_good(self, cols_en_1: Columns) -> None:
        test_df = pd.DataFrame({"id (optional)": [1, 2, 3], "en_list": ["a", "b", "c"], "en_1": ["d", "e", "f"]})
        test_sheet = ExcelSheet(excel_name="", sheet_name="sheet", df=test_df, col_info=cols_en_1)
        assert not _make_shape_compliance_one_sheet(test_sheet)

    def test_good_no_id(self, cols_en_1: Columns) -> None:
        test_df = pd.DataFrame({"en_list": ["a", "b", "c"], "en_1": ["d", "e", "f"]})
        test_sheet = ExcelSheet(excel_name="", sheet_name="sheet", df=test_df, col_info=cols_en_1)
        assert not _make_shape_compliance_one_sheet(test_sheet)

    def test_missing_node_column(self, cols_en_list_only: Columns) -> None:
        test_df = pd.DataFrame({"id (optional)": [1, 1], "en_list": ["a", "b"], "additional_1": ["b", "c"]})
        test_sheet = ExcelSheet(excel_name="excel", sheet_name="sheet", df=test_df, col_info=cols_en_list_only)
        warning_msg = regex.escape(
            "The following columns do not conform to the expected format "
            "and will not be included in the output: additional_1"
        )
        with pytest.warns(DspToolsUserWarning, match=warning_msg):
            res = _make_shape_compliance_one_sheet(test_sheet)
        assert isinstance(res, ListSheetComplianceProblem)
        assert res.excel_name == "excel"
        assert res.sheet_name == "sheet"
        assert len(res.problems) == 1
        assert isinstance(res.problems[0], MissingNodeColumn)

    def test_missing_list_column(self, cols_en_1: Columns) -> None:
        test_df = pd.DataFrame({"id (optional)": [1, 2], "en_1": ["b", "c"]})
        test_sheet = ExcelSheet(excel_name="excel", sheet_name="sheet", df=test_df, col_info=cols_en_1)
        res = _make_shape_compliance_one_sheet(test_sheet)
        assert isinstance(res, ListSheetComplianceProblem)
        assert res.excel_name == "excel"
        assert res.sheet_name == "sheet"
        assert len(res.problems) == 1
        missing = res.problems[0]
        assert isinstance(missing, MissingExpectedColumn)
        assert missing.missing_cols == {"en_list"}

    def test_missing_translation_column(self, cols_en_de_1: Columns) -> None:
        test_df = pd.DataFrame(
            {"id (optional)": [1, 2], "en_list": ["a", "b"], "de_list": ["b", "c"], "de_1": ["b", "c"]}
        )
        test_sheet = ExcelSheet(excel_name="excel", sheet_name="sheet", df=test_df, col_info=cols_en_de_1)
        res = _make_shape_compliance_one_sheet(test_sheet)
        assert isinstance(res, ListSheetComplianceProblem)
        assert res.excel_name == "excel"
        assert res.sheet_name == "sheet"
        assert len(res.problems) == 1
        missing = res.problems[0]
        assert isinstance(missing, MissingExpectedColumn)
        assert missing.missing_cols == {"en_1"}

    def test_missing_rows(self, cols_en_1: Columns) -> None:
        test_df = pd.DataFrame({"id (optional)": [1], "en_list": ["a"], "en_1": ["d"]})
        test_sheet = ExcelSheet(excel_name="", sheet_name="sheet", df=test_df, col_info=cols_en_1)
        res = _make_shape_compliance_one_sheet(test_sheet)
        assert isinstance(res, ListSheetComplianceProblem)
        assert len(res.problems) == 1
        assert isinstance(res.problems[0], MinimumRowsProblem)


class TestCheckWarnUnusualColumns:
    def test_good(self) -> None:
        test_cols = pd.Index(["id (optional)", "en_list", "en_2", "de_2"])
        with warnings.catch_warnings(record=True) as caught_warnings:
            _check_warn_unusual_columns_one_sheet(test_cols)
        assert len(caught_warnings) == 0

    def test_additional_columns(self) -> None:
        test_cols = pd.Index(["id (optional)", "en_list", "en_2", "de_2", "additional_1", "additional_2"])
        expected = regex.escape(
            "The following columns do not conform to the expected format "
            "and will not be included in the output: additional_1, additional_2"
        )
        with pytest.warns(DspToolsUserWarning, match=expected):
            _check_warn_unusual_columns_one_sheet(test_cols)


class TestCheckAllTranslationsPresent:
    def test_good(self) -> None:
        test_cols = pd.Index(["id (optional)", "en_list", "de_list", "de_1", "en_1", "de_2", "en_2"])
        assert not _check_if_all_translations_in_all_column_levels_present_one_sheet(test_cols)

    def test_missing_translations_node_columns(self) -> None:
        test_cols = pd.Index(["id (optional)", "en_list", "de_list", "de_1", "en_1", "de_2"])
        res = _check_if_all_translations_in_all_column_levels_present_one_sheet(test_cols)
        assert isinstance(res, MissingExpectedColumn)
        assert res.missing_cols == {"en_2"}

    def test_missing_translations_list_columns(self) -> None:
        test_cols = pd.Index(["id (optional)", "en_list", "de_1", "en_1", "de_2", "en_2"])
        res = _check_if_all_translations_in_all_column_levels_present_one_sheet(test_cols)
        assert isinstance(res, MissingExpectedColumn)
        assert res.missing_cols == {"de_list"}


class TestCheckAllExcelsMissingTranslations:
    def test_good(self, f1_s1_good_en: ExcelSheet, f2_s2_good_en_de: ExcelSheet) -> None:
        all_sheets = [f1_s1_good_en, f2_s2_good_en_de]
        _check_for_missing_translations_all_excels(all_sheets)

    def test_problem(self, f1_s1_good_en: ExcelSheet, f2_s2_missing_translations: ExcelSheet) -> None:
        all_sheets = [f1_s1_good_en, f2_s2_missing_translations]
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "The Excel file 'file2' contains the following problems:\n\n"
            "The excel sheet 'sheet2' has the following problem(s):\n"
            "In one list, all the nodes must be translated into all the languages used. "
            "For the following nodes, the translations are missing:\n"
            "    - Row Number: 2 | Column(s): de_list\n"
            "    - Row Number: 3 | Column(s): en_1\n"
            "    - Row Number: 5 | Column(s): de_comments\n"
            "    - Row Number: 6 | Column(s): en_1, en_2, en_list"
        )
        with pytest.raises(InputError, match=expected):
            _check_for_missing_translations_all_excels(all_sheets)


class TestAllNodesTranslatedIntoAllLanguages:
    def test_good(self, f1_s1_good_id_filled_empty_comments: ExcelSheet) -> None:
        assert not _check_for_missing_translations_one_sheet(f1_s1_good_id_filled_empty_comments)

    def test_missing_translation(self, f1_s1_missing_translation_id_filled: ExcelSheet) -> None:
        expected = [
            MissingNodeTranslationProblem(["de_2"], 2),
            MissingNodeTranslationProblem(["en_list"], 5),
            MissingNodeTranslationProblem(["en_1"], 8),
        ]
        result = _check_for_missing_translations_one_sheet(f1_s1_missing_translation_id_filled)
        assert isinstance(result, MissingTranslationsSheetProblem)
        assert result.excel_name == "excel1"
        assert result.sheet == "sheet1"
        res_node_problems = sorted(result.node_problems, key=lambda x: x.index_num)
        for res, expct in zip(res_node_problems, expected):
            assert res.empty_columns == expct.empty_columns
            assert res.index_num == expct.index_num


class TestCheckMissingTranslationsOneRow:
    def test_good(self, f2_s2_good_en_de: ExcelSheet, cols_en_de_1_3: Columns) -> None:
        for i, row in f2_s2_good_en_de.df.iterrows():
            assert not _check_missing_translations_one_row(int(str(i)), row, cols_en_de_1_3)

    def test_good_empty_comments(
        self, f1_s1_good_id_filled_empty_comments: ExcelSheet, cols_en_de_1_3: Columns
    ) -> None:
        for i, row in f1_s1_good_id_filled_empty_comments.df.iterrows():
            assert not _check_missing_translations_one_row(int(str(i)), row, cols_en_de_1_3)

    def test_one_missing(self, f2_s2_missing_translations: ExcelSheet, cols_en_de_1_3: Columns) -> None:
        result = _check_missing_translations_one_row(1, f2_s2_missing_translations.df.loc[1], cols_en_de_1_3)  # type: ignore[arg-type]
        assert isinstance(result, MissingNodeTranslationProblem)
        assert set(result.empty_columns) == {"en_1"}
        assert result.index_num == 1

    def test_three_missing(self, f2_s2_missing_translations: ExcelSheet, cols_en_de_1_3: Columns) -> None:
        result = _check_missing_translations_one_row(4, f2_s2_missing_translations.df.loc[4], cols_en_de_1_3)  # type: ignore[arg-type]
        assert isinstance(result, MissingNodeTranslationProblem)
        assert set(result.empty_columns) == {"en_list", "en_1", "en_2"}
        assert result.index_num == 4

    def test_one_group_good(self, f2_s2_good_en_de: ExcelSheet) -> None:
        for i, row in f2_s2_good_en_de.df.iterrows():
            assert not _check_for_missing_translations_one_column_group(row, ["en_list", "de_list"])

    def test_one_group_missing(self) -> None:
        series = pd.Series(data=[pd.NA, "content"], index=["en_1", "de_1"])
        result = _check_for_missing_translations_one_column_group(series, ["en_1", "de_1"])
        assert result == ["en_1"]


class TestCheckAllExcelForRowProblems:
    def test_all_good(self, f1_s1_good_en: ExcelSheet, f2_s2_good_en_de: ExcelSheet) -> None:
        all_sheets = [f1_s1_good_en, f2_s2_good_en_de]
        _check_for_erroneous_entries_all_excels(all_sheets)

    def test_all_problem(self, cols_en_1: Columns, cols_en_1_2: Columns) -> None:
        df_1 = pd.DataFrame({"en_list": ["list1", "list1", "list1", "list1"], "en_1": [pd.NA, "node1", pd.NA, "node3"]})
        df_2 = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node1", "node2", "node3"],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.2", "node2.1", pd.NA],
            }
        )
        all_sheets = [
            ExcelSheet(excel_name="file1", sheet_name="sheet1", df=df_1, col_info=cols_en_1),
            ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df_2, col_info=cols_en_1_2),
        ]
        expected = regex.escape(
            "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
            "The Excel file 'file1' contains the following problems:\n\n"
            "The Excel sheet 'sheet1' has the following problem(s):\n"
            "    - Row Number: 4, Column(s) that must be filled: en_1\n\n"
            "---------------------------------------\n\n"
            "The Excel file 'file2' contains the following problems:\n\n"
            "The Excel sheet 'sheet2' has the following problem(s):\n"
            "    - Row Number: 6, Column(s) that must be empty: en_2"
        )
        with pytest.raises(InputError, match=expected):
            _check_for_erroneous_entries_all_excels(all_sheets)


class TestOneSheetErrors:
    def test_all_good_flat(self, cols_en_1: Columns) -> None:
        df = pd.DataFrame({"en_list": ["list1", "list1", "list1", "list1"], "en_1": [pd.NA, "node1", "node2", "node3"]})
        test_sheet = ExcelSheet(excel_name="", sheet_name="sheet", df=df, col_info=cols_en_1)
        assert not _check_for_erroneous_entries_one_list(test_sheet)

    def test_problem(self, cols_en_1_2: Columns) -> None:
        df = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node1", "node2", "node3"],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.2", "node2.1", pd.NA],
            }
        )
        test_sheet = ExcelSheet(excel_name="excel_name", sheet_name="sheet", df=df, col_info=cols_en_1_2)
        res = _check_for_erroneous_entries_one_list(test_sheet)
        assert isinstance(res, ListSheetContentProblem)
        assert res.excel_name == "excel_name"
        assert res.sheet_name == "sheet"
        assert len(res.problems) == 1


class TestCheckForErroneousEntries:
    def test_all_good_subnodes(self, f2_s2_good_en_de: ExcelSheet) -> None:
        assert not _check_for_erroneous_node_info_one_df(f2_s2_good_en_de.df, ["en_list", "en_1", "en_2", "en_3"])

    def test_all_good_flat(self, f1_s1_good_en: ExcelSheet) -> None:
        assert not _check_for_erroneous_node_info_one_df(f1_s1_good_en.df, ["en_list", "en_1"])

    def test_all_good_duplicate_names(self) -> None:
        df = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node2", "node2", "node2", "node2"],
                "en_2": [pd.NA, pd.NA, "same", pd.NA, "same", "2.1", "2.1"],
                "en_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "2.1.1"],
            }
        )
        assert not _check_for_erroneous_node_info_one_df(df, ["en_list", "en_1", "en_2", "en_3"])

    def test_missing_row(self) -> None:
        df = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node1", "node2", "node3"],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.2", "node2.1", pd.NA],
                "en_3": [pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA],
            }
        )
        # "node1.1" & "node2" is missing
        res = _check_for_erroneous_node_info_one_df(df, ["en_list", "en_1", "en_2", "en_3"])
        res = sorted(res, key=lambda x: x.index_num)
        assert len(res) == 2
        assert isinstance(res[0], NodesPerRowProblem)
        assert res[0].column_names == ["en_3"]
        assert res[0].index_num == 2
        assert res[0].should_be_empty
        assert isinstance(res[1], NodesPerRowProblem)
        assert res[1].column_names == ["en_2", "en_3"]
        assert res[1].index_num == 4
        assert res[1].should_be_empty


class TestCheckOneColumnGroupsForErroneousEntries:
    def test_good(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "b", "c"], "two": [pd.NA, "bb", "bb", "cc"], "other": ["a", "b", pd.NA, pd.NA]},
            index=[2, 3, 4, 5],
        )
        assert not _check_for_erroneous_entries_one_column_level(df, ["two"], 0)

    def test_missing(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "b", "c"], "two": [pd.NA, "bb", pd.NA, pd.NA], "other": ["a", "b", pd.NA, pd.NA]},
            index=[2, 3, 4, 5],
        )
        res = _check_for_erroneous_entries_one_column_level(df, ["one", "two"], 0)
        assert len(res) == 2
        assert isinstance(res[0], NodesPerRowProblem)
        assert res[0].column_names == ["two"]
        assert res[0].index_num == 3
        assert res[0].should_be_empty
        assert isinstance(res[1], NodesPerRowProblem)
        assert res[1].column_names == ["two"]
        assert res[1].index_num == 4
        assert not res[1].should_be_empty


class TestCheckOneGroupForErroneousEntries:
    def test_good(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "c"], "two": [pd.NA, "bb", "cc"], "other": ["a", "b", pd.NA]}, index=[2, 3, 4]
        )
        assert not _check_for_erroneous_entries_one_grouped_df(df, ["one", "two"])

    def test_good_one_col(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "c"], "two": [pd.NA, "bb", "cc"], "other": ["a", "b", pd.NA]}, index=[2, 3, 4]
        )
        assert not _check_for_erroneous_entries_one_grouped_df(df, ["two"])

    def test_filled_first_row(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "c"], "two": ["filled", "bb", "cc"], "other": ["a", "b", pd.NA]}, index=[2, 3, 4]
        )
        res = _check_for_erroneous_entries_one_grouped_df(df, ["one", "two"])
        assert len(res) == 1
        assert isinstance(res[0], NodesPerRowProblem)
        assert res[0].column_names == ["two"]
        assert res[0].index_num == 2
        assert res[0].should_be_empty

    def test_missing_next_rows(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "c", "d"], "two": [pd.NA, pd.NA, "cc", pd.NA], "other": ["a", "b", pd.NA, "d"]},
            index=[2, 3, 4, 5],
        )
        res = _check_for_erroneous_entries_one_grouped_df(df, ["one", "two"])
        assert len(res) == 2
        assert isinstance(res[0], NodesPerRowProblem)
        assert res[0].column_names == ["two"]
        assert res[0].index_num == 3
        assert not res[0].should_be_empty
        assert isinstance(res[1], NodesPerRowProblem)
        assert res[1].column_names == ["two"]
        assert res[1].index_num == 5
        assert not res[1].should_be_empty


if __name__ == "__main__":
    pytest.main([__file__])
