from __future__ import annotations

import warnings

import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import ListSheetComplianceProblem
from dsp_tools.commands.excel2json.new_lists import _get_lang_string_from_column_names
from dsp_tools.models.custom_warnings import DspToolsUserWarning


def _df_shape_compliance(df: pd.DataFrame, sheet_name: str) -> ListSheetComplianceProblem | None:
    problems = {}
    problems.update(_check_minimum_rows(df))
    problems.update(_check_min_num_col_present(df.columns))
    _check_warn_unusual_columns(df.columns)
    if problems:
        return ListSheetComplianceProblem(sheet_name, problems)
    return None


def _check_minimum_rows(df: pd.DataFrame) -> dict[str, str]:
    if len(df) < 2:
        return {
            "minimum rows": "The excel must contain at least two rows, "
            "one for the list name and one row for a minimum of one node."
        }
    return {}


def _check_min_num_col_present(cols: pd.Index[str]) -> dict[str, str]:
    problem = {}
    nodes = [_get_lang_string_from_column_names(c, r"\d+") for c in cols]
    if not any(nodes):
        problem["missing columns for nodes"] = (
            "There is not column with the expected format for the list nodes: '[lang]_[column_number]'"
        )
    list_name = [_get_lang_string_from_column_names(c, r"list") for c in cols]
    if not any(list_name):
        problem["missing columns for list name"] = (
            "There is not column with the expected format for the list names: '[lang]_list'"
        )
    return problem


def _check_warn_unusual_columns(cols: pd.Index[str]) -> None:
    not_matched = [x for x in cols if not regex.search(r"^(en|de|fr|it|rm)_(\d+|list)|(ID \(optional\))$", x)]
    if not_matched:
        msg = (
            f"The following columns do not conform to the expected format "
            f"and will not be included in the output: {', '.join(not_matched)}"
        )
        warnings.warn(DspToolsUserWarning(msg))
