import warnings
from typing import cast

import pandas as pd
import pytest
import regex

from dsp_tools.commands.excel2json.lists_compliance_checks import _check_all_excel_for_erroneous_entries
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_all_excels_if_any_nodes_miss_translations
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_all_expected_translations_present
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_for_erroneous_entries
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_min_num_col_present
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_minimum_rows
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_one_column_groups_for_erroneous_entries
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_one_group_for_erroneous_entries
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_one_hierarchy
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_one_node_for_translations
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_sheet_for_erroneous_entries
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_sheet_if_any_nodes_miss_translations
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_warn_unusual_columns
from dsp_tools.commands.excel2json.lists_compliance_checks import _df_shape_compliance
from dsp_tools.commands.excel2json.lists_compliance_checks import _make_columns
from dsp_tools.commands.excel2json.models.input_error import ListSheetComplianceProblem
from dsp_tools.commands.excel2json.models.input_error import ListSheetContentProblem
from dsp_tools.commands.excel2json.models.input_error import MissingNodeTranslationProblem
from dsp_tools.commands.excel2json.models.input_error import MissingTranslationsSheetProblem
from dsp_tools.commands.excel2json.models.input_error import NodesPerRowProblem
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError


class TestShapeCompliance:
    def test_good(self) -> None:
        test_df = pd.DataFrame({"ID (optional)": [1, 2, 3], "en_list": ["a", "b", "c"], "en_2": ["d", "e", "f"]})
        assert not _df_shape_compliance(test_df, "")

    def test_good_no_id(self) -> None:
        test_df = pd.DataFrame({"en_list": ["a", "b", "c"], "en_2": ["d", "e", "f"]})
        assert not _df_shape_compliance(test_df, "")

    def test_problems_one(self) -> None:
        test_df = pd.DataFrame({"ID (optional)": [1], "en_list": ["a"], "additional_1": ["b"]})
        expected = {
            "minimum rows": "The Excel sheet must contain at least two rows, "
            "one for the list name and one row for a minimum of one node.",
            "missing columns for nodes": "There is no column with the expected format for the list nodes: "
            "'[lang]_[column_number]'",
        }
        warning_msg = regex.escape(
            "The following columns do not conform to the expected format "
            "and will not be included in the output: additional_1"
        )
        with pytest.warns(DspToolsUserWarning, match=warning_msg):
            res = _df_shape_compliance(test_df, "sheet")
            res = cast(ListSheetComplianceProblem, res)
            assert res.problems == expected

    def test_problems_two(self) -> None:
        test_df = pd.DataFrame({"ID (optional)": [1, 2], "en_list": ["a", "b"], "en_1": ["b", "c"], "de_1": ["b", "c"]})
        expected = {
            "missing translations": "All nodes must be translated into the same languages. "
            "One or more translations for the following column(s) are missing: "
            "de_list"
        }
        res = _df_shape_compliance(test_df, "sheet")
        res = cast(ListSheetComplianceProblem, res)
        assert res.problems == expected


class TestCheckMinNumColNamesPresent:
    def test_good(self) -> None:
        col_names = pd.Index(["ID (optional)", "en_list", "en_2"])
        assert not _check_min_num_col_present(col_names)

    def test_good_no_id(self) -> None:
        col_names = pd.Index(["en_list", "en_2"])
        assert not _check_min_num_col_present(col_names)

    def test_missing_columns_list(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_2"])
        expected = {
            "missing columns for list name": "There is no column with the expected format for the list names: "
            "'[lang]_list'"
        }
        assert _check_min_num_col_present(test_cols) == expected

    def test_missing_columns_node(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list"])
        expected = {
            "missing columns for nodes": "There is no column with the expected format for the list nodes: "
            "'[lang]_[column_number]'"
        }
        assert _check_min_num_col_present(test_cols) == expected


class TestCheckMinimumRows:
    def test_good(self) -> None:
        test_df = pd.DataFrame({"one": [1, 2, 3], "two": [4, 5, 6]})
        assert not _check_minimum_rows(test_df)

    def test_missing_rows(self) -> None:
        test_df = pd.DataFrame({"one": [1]})
        expected = {
            "minimum rows": "The Excel sheet must contain at least two rows, "
            "one for the list name and one row for a minimum of one node."
        }
        assert _check_minimum_rows(test_df) == expected


class TestCheckWarnUnusualColumns:
    def test_good(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list", "en_2", "de_2"])
        with warnings.catch_warnings(record=True) as caught_warnings:
            _check_warn_unusual_columns(test_cols)
        assert len(caught_warnings) == 0

    def test_additional_columns(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list", "en_2", "de_2", "additional_1", "additional_2"])
        expected = regex.escape(
            "The following columns do not conform to the expected format "
            "and will not be included in the output: additional_1, additional_2"
        )
        with pytest.warns(DspToolsUserWarning, match=expected):
            _check_warn_unusual_columns(test_cols)


class TestCheckAllTranslationsPresent:
    def test_good(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list", "de_list", "de_1", "en_1", "de_2", "en_2"])
        assert not _check_all_expected_translations_present(test_cols)

    def test_missing_translations_node_columns(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list", "de_list", "de_1", "en_1", "de_2"])
        expected = {
            "missing translations": "All nodes must be translated into the same languages. "
            "One or more translations for the following column(s) are missing: "
            "en_2"
        }
        assert _check_all_expected_translations_present(test_cols) == expected

    def test_missing_translations_list_columns(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list", "de_1", "en_1", "de_2", "en_2"])
        expected = {
            "missing translations": "All nodes must be translated into the same languages. "
            "One or more translations for the following column(s) are missing: "
            "de_list"
        }
        assert _check_all_expected_translations_present(test_cols) == expected


class TestCheckAllExcelsMissingTranslations:
    def test_good(self) -> None:
        df_1 = pd.DataFrame(
            {"en_list": ["list1", "list1", "list1", "list1"], "en_1": [pd.NA, "node1", "node2", "node3"]}
        )
        df_2 = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1", "list1"],
                "de_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node2", "node3"],
                "de_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node2", "node3"],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, "node2.1", pd.NA],
                "de_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, "node2.1", pd.NA],
                "en_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA, pd.NA],
                "de_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        df_dict = {"file1": {"sheet1": df_1}, "file2": {"sheet2": df_2}}
        _check_all_excels_if_any_nodes_miss_translations(df_dict)

    def test_problem(self) -> None:
        df_1 = pd.DataFrame({"en_list": ["list1", "list1", "list1", "list1"], "en_1": [pd.NA, "node1", pd.NA, "node3"]})
        df_2 = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1"],
                "de_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, pd.NA, "node1", "node1", "node1", "node2", "node3"],
                "de_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", pd.NA],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, pd.NA],
                "de_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, pd.NA],
                "en_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA],
                "de_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA],
            }
        )
        df_dict = {"file1": {"sheet1": df_1}, "file2": {"sheet2": df_2}}
        expected = regex.escape(
            "\nThe excel file(s) used to create the list sections have the following problem(s):\n\n"
            "---------------------------------------\n\n"
            "The excel 'file2' has the following problem(s):\n"
            "----------------------------\n"
            "In one list, all the nodes must be translated into all the languages used. "
            "The following nodes are missing translations:\n"
            "    - Row Number: '3' Column(s): en_1\n"
            "    - Row Number: '8' Column(s): de_1"
        )
        with pytest.raises(InputError, match=expected):
            _check_all_excels_if_any_nodes_miss_translations(df_dict)


class TestAllNodesTranslatedIntoAllLanguages:
    def test_good(self) -> None:
        test_df = pd.DataFrame(
            {
                "id": ["list_id", "1", "1.1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
                "parent_id": ["list_id", "list_id", "1", "list_id", "list_id", "3", "3", "3.2", "3.2"],
                "en_list": [
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                ],
                "de_list": [
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                ],
                "en_1": [
                    pd.NA,
                    "Node_en_1",
                    "Node_en_1",
                    "Node_en_2",
                    "Node_en_3",
                    "Node_en_3",
                    "Node_en_3",
                    "Node_en_3",
                    "Node_en_3",
                ],
                "de_1": [
                    pd.NA,
                    "Node_de_1",
                    "Node_de_1",
                    "Node_de_2",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                ],
                "en_2": [
                    pd.NA,
                    pd.NA,
                    "Node_en_1.1",
                    pd.NA,
                    pd.NA,
                    "Node_en_3.1",
                    "Node_en_3.2",
                    "Node_en_3.2",
                    "Node_en_3.2",
                ],
                "de_2": [
                    pd.NA,
                    pd.NA,
                    "Node_de_1.1",
                    pd.NA,
                    pd.NA,
                    "Node_de_3.1",
                    "Node_de_3.2",
                    "Node_de_3.2",
                    "Node_de_3.2",
                ],
                "en_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "Node_en_3.2.1", "Node_en_3.2.2"],
                "de_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "Node_de_3.2.1", "Node_de_3.2.2"],
            }
        )
        _check_sheet_if_any_nodes_miss_translations(test_df, "sheet")

    def test_missing_translation(self) -> None:
        test_df = pd.DataFrame(
            {
                "id": ["list_id", "1", "1.1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
                "parent_id": ["list_id", "list_id", "1", "list_id", "list_id", "3", "3", "3.2", "3.2"],
                "en_list": [
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    pd.NA,
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                ],
                "de_list": [
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                ],
                "en_1": [
                    pd.NA,
                    "Node_en_1",
                    "Node_en_1",
                    "Node_en_2",
                    "Node_en_3",
                    "Node_en_3",
                    "Node_en_3",
                    "Node_en_3",
                    pd.NA,
                ],
                "de_1": [
                    pd.NA,
                    "Node_de_1",
                    "Node_de_1",
                    "Node_de_2",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                ],
                "en_2": [
                    pd.NA,
                    pd.NA,
                    "Node_en_1.1",
                    pd.NA,
                    pd.NA,
                    "Node_en_3.1",
                    "Node_en_3.2",
                    "Node_en_3.2",
                    "Node_en_3.2",
                ],
                "de_2": [
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    "Node_de_3.1",
                    "Node_de_3.2",
                    "Node_de_3.2",
                    "Node_de_3.2",
                ],
            }
        )
        expected = [
            MissingNodeTranslationProblem(["de_2"], 2),
            MissingNodeTranslationProblem(["en_list"], 5),
            MissingNodeTranslationProblem(["en_1"], 8),
        ]
        result = _check_sheet_if_any_nodes_miss_translations(test_df, "sheet")
        result = cast(MissingTranslationsSheetProblem, result)
        res_node_problems = sorted(result.node_problems, key=lambda x: x.index_num)
        for res, expct in zip(res_node_problems, expected):
            assert res.empty_columns == expct.empty_columns
            assert res.index_num == expct.index_num


class TestCheckOneHierarchy:
    def test_good(self) -> None:
        test_df = pd.DataFrame(
            {
                "en_1": ["exist1_en", "exist2_en", "exist3_en"],
                "de_1": ["exist1_de", "exist2_de", "exist3_de"],
                "fr_1": ["exist1_fr", "exist2_fr", "exist3_fr"],
            }
        )
        assert not _check_one_hierarchy(["en_1", "de_1", "fr_1"], test_df)

    def test_missing_translation(self) -> None:
        test_df = pd.DataFrame(
            {
                "en_1": ["exist1_en", pd.NA, "exist3_en"],
                "de_1": ["exist1_de", pd.NA, "exist3_de"],
                "fr_1": ["exist1_fr", "exist2_fr", "exist3_fr"],
            }
        )
        res = _check_one_hierarchy(["en_1", "de_1", "fr_1"], test_df)
        assert len(res) == 1
        prbl = res[0]
        assert prbl.empty_columns == ["en_1", "de_1"]
        assert prbl.index_num == 1


class TestCheckOneNodeForTranslation:
    def test_good(self) -> None:
        test_series = pd.Series(["exist_en", "exist_de"], index=["en_1", "de_1"])
        assert not _check_one_node_for_translations(test_series, ["en_1", "de_1"], 1)

    def test_good_empty(self) -> None:
        test_series = pd.Series([pd.NA, pd.NA], index=["en_1", "de_1"])
        assert not _check_one_node_for_translations(test_series, ["en_1", "de_1"], 1)

    def test_missing_translation(self) -> None:
        test_series = pd.Series(["exist_en", pd.NA], index=["en_1", "de_1"])
        result = _check_one_node_for_translations(test_series, ["en_1", "de_1"], 1)
        result = cast(MissingNodeTranslationProblem, result)
        assert result.empty_columns == ["de_1"]
        assert result.index_num == 1


def test_make_columns() -> None:
    res = _make_columns(["1", "2"], {"en", "de", "fr"})
    assert len(res) == 2
    assert set(res[0]) == {"en_1", "de_1", "fr_1"}
    assert set(res[1]) == {"en_2", "de_2", "fr_2"}


class TestCheckAllExcelForRowProblems:
    def test_all_good(self) -> None:
        df_1 = pd.DataFrame(
            {"en_list": ["list1", "list1", "list1", "list1"], "en_1": [pd.NA, "node1", "node2", "node3"]}
        )
        df_2 = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node2", "node3"],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, "node2.1", pd.NA],
                "en_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        df_dict = {"file1": {"sheet1": df_1}, "file2": {"sheet2": df_2}}
        _check_all_excel_for_erroneous_entries(df_dict)

    def test_all_problem(self) -> None:
        df_1 = pd.DataFrame({"en_list": ["list1", "list1", "list1", "list1"], "en_1": [pd.NA, "node1", pd.NA, "node3"]})
        df_2 = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node1", "node2", "node3"],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.2", "node2.1", pd.NA],
            }
        )
        df_dict = {"file1": {"sheet1": df_1}, "file2": {"sheet2": df_2}}
        expected = regex.escape(
            "\nThe excel file(s) used to create the list sections have the following problem(s):\n\n"
            "---------------------------------------\n\n"
            "The excel 'file1' has the following problem(s):\n"
            "----------------------------\n"
            "The Excel sheet 'sheet1' has the following problem(s):\n"
            "    - Row Number: '4' Column must be filled: en_1\n\n"
            "---------------------------------------\n\n"
            "The excel 'file2' has the following problem(s):\n"
            "----------------------------\n"
            "The Excel sheet 'sheet2' has the following problem(s):\n"
            "    - Row Number: '6' Columns must be empty: en_2"
        )
        with pytest.raises(InputError, match=expected):
            _check_all_excel_for_erroneous_entries(df_dict)


class TestOneSheetErrors:
    def test_all_good_flat(self) -> None:
        df = pd.DataFrame({"en_list": ["list1", "list1", "list1", "list1"], "en_1": [pd.NA, "node1", "node2", "node3"]})
        assert not _check_sheet_for_erroneous_entries(df, "name")

    def test_problem(self) -> None:
        df = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node1", "node2", "node3"],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.2", "node2.1", pd.NA],
            }
        )
        res = _check_sheet_for_erroneous_entries(df, "name")
        assert isinstance(res, ListSheetContentProblem)
        assert res.sheet_name == "name"
        assert len(res.problems) == 1


class TestCheckForErroneousEntries:
    def test_all_good_subnodes(self) -> None:
        df = pd.DataFrame(
            {
                "en_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1", "list1"],
                "en_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node2", "node3"],
                "en_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, "node2.1", pd.NA],
                "en_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        assert not _check_for_erroneous_entries(df, ["en_list", "en_1", "en_2", "en_3"])

    def test_all_good_flat(self) -> None:
        df = pd.DataFrame({"en_list": ["list1", "list1", "list1", "list1"], "en_1": [pd.NA, "node1", "node2", "node3"]})
        assert not _check_for_erroneous_entries(df, ["en_list", "en_1"])

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
        res = _check_for_erroneous_entries(df, ["en_list", "en_1", "en_2", "en_3"])
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
        assert not _check_one_column_groups_for_erroneous_entries(df, ["two"])

    def test_missing(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "b", "c"], "two": [pd.NA, "bb", pd.NA, pd.NA], "other": ["a", "b", pd.NA, pd.NA]},
            index=[2, 3, 4, 5],
        )
        res = _check_one_column_groups_for_erroneous_entries(df, ["one", "two"])
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
        assert not _check_one_group_for_erroneous_entries(df, ["one", "two"])

    def test_good_one_col(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "c"], "two": [pd.NA, "bb", "cc"], "other": ["a", "b", pd.NA]}, index=[2, 3, 4]
        )
        assert not _check_one_group_for_erroneous_entries(df, ["two"])

    def test_filled_first_row(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "c"], "two": ["filled", "bb", "cc"], "other": ["a", "b", pd.NA]}, index=[2, 3, 4]
        )
        res = _check_one_group_for_erroneous_entries(df, ["one", "two"])
        assert len(res) == 1
        assert isinstance(res[0], NodesPerRowProblem)
        assert res[0].column_names == ["two"]
        assert res[0].index_num == 2
        assert res[0].should_be_empty

    def test_missing_nex_rows(self) -> None:
        df = pd.DataFrame(
            {"one": ["a", "b", "c", "d"], "two": [pd.NA, pd.NA, "cc", pd.NA], "other": ["a", "b", pd.NA, "d"]},
            index=[2, 3, 4, 5],
        )
        res = _check_one_group_for_erroneous_entries(df, ["one", "two"])
        assert len(res) == 2
        assert isinstance(res[0], NodesPerRowProblem)
        assert res[0].column_names == ["two"]
        assert res[0].index_num == 3
        assert not res[0].should_be_empty
        assert isinstance(res[1], NodesPerRowProblem)
        assert res[1].column_names == ["two"]
        assert res[1].index_num == 5
        assert not res[1].should_be_empty
