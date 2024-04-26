import warnings

import pandas as pd
import pytest

from dsp_tools.commands.excel2json.lists_compliance_checks import _check_min_num_col_present
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_minimum_rows
from dsp_tools.commands.excel2json.lists_compliance_checks import _check_warn_unusual_columns
from dsp_tools.commands.excel2json.lists_compliance_checks import _df_shape_compliance
from dsp_tools.models.custom_warnings import DspToolsUserWarning


class TestShapeCompliance:
    def test_good(self):
        test_df = pd.DataFrame({"ID (optional)": [1, 2, 3], "en_list": ["a", "b", "c"], "en_2": ["d", "e", "f"]})
        assert not _df_shape_compliance(test_df)

    def test_problems(self):
        test_df = pd.DataFrame({"ID (optional)": [1], "en_list": ["a"], "additional_1": ["b"]})
        expected = {
            "minimum rows": "The excel must contain at least two rows, "
            "one for the list name one row for a minimum of one node.",
            "missing columns": "The following columns are required: "
            "'ID (optional)', at least one in the format of "
            "'[lang]_list', and '[lang]_[column_number]'",
            "additional columns": "The following columns do not conform to the expected format "
            "and will not be included in the output: 'additional_1'",
        }
        assert _df_shape_compliance(test_df) == expected


class TestCheckMinNumColPresent:
    def test_good(self) -> None:
        cols = pd.Index(["ID (optional)", "en_list", "en_2"])
        assert not _check_min_num_col_present(cols)

    def test_missing_columns_id(self) -> None:
        test_cols = pd.Index(["en_list", "en_2"])
        expected = {
            "missing columns": "The following columns are required: "
            "'ID (optional)', at least one in the format of "
            "'[lang]_list', and '[lang]_[column_number]'"
        }
        assert _check_min_num_col_present(test_cols) == expected

    def test_missing_columns_list(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_2"])
        expected = {
            "missing columns": "The following columns are required: "
            "'ID (optional)', at least one in the format of "
            "'[lang]_list', and '[lang]_[column_number]'"
        }
        assert _check_min_num_col_present(test_cols) == expected

    def test_missing_columns_node(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list"])
        expected = {
            "missing columns": "The following columns are required: "
            "'ID (optional)', at least one in the format of "
            "'[lang]_list', and '[lang]_[column_number]'"
        }
        assert _check_warn_unusual_columns(test_cols) == expected


class TestCheckMinimumRows:
    def test_good(self) -> None:
        test_df = pd.DataFrame({"one": [1, 2, 3], "two": [4, 5, 6]})
        assert not _check_minimum_rows(test_df)

    def test_missing_rows(self) -> None:
        test_df = pd.DataFrame({"one": [1]})
        expected = {
            "minimum rows": "The excel must contain at least two rows, "
            "one for the list name one row for a minimum of one node."
        }
        assert _check_minimum_rows(test_df) == expected


class TestCheckWarnUnusualColumns:
    def test_good(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list", "en_2", "de_2"])
        with warnings.catch_warnings(record=True) as catched_warnings:
            _check_warn_unusual_columns(test_cols)
            assert len(catched_warnings) == 0

    def test_additional_columns(self) -> None:
        test_cols = pd.Index(["ID (optional)", "en_list", "en_2", "de_2", "additiona_1", "additional_2"])
        expected = {
            "additional columns": "The following columns do not conform to the expected format "
            "and will not be included in the output: 'additional_1', 'additional_2'"
        }
        with pytest.warns(DspToolsUserWarning) as record:
            _check_warn_unusual_columns(test_cols)
        assert record[0].message.args[0] == expected
