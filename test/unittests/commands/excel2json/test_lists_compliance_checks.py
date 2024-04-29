import warnings
from typing import cast

import pandas as pd
import pytest
import regex

from dsp_tools.commands.excel2json.lists_compliance_checks import _check_all_expected_translations_present
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_min_num_col_present
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_minimum_rows
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_warn_unusual_columns
from dsp_tools.commands.excel2json.lists_compliance_checks import _df_shape_compliance
from dsp_tools.commands.excel2json.models.input_error import ListSheetComplianceProblem
from dsp_tools.models.custom_warnings import DspToolsUserWarning


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
