from __future__ import annotations

import warnings

import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import ListExcelComplianceProblem
from dsp_tools.commands.excel2json.models.input_error import ListSheetComplianceProblem
from dsp_tools.commands.excel2json.new_lists import _get_hierarchy_nums
from dsp_tools.commands.excel2json.new_lists import _get_lang_string_from_column_name
from dsp_tools.models.custom_warnings import DspToolsUserWarning


def make_all_formal_excel_compliance_checks(
    excel_dfs: dict[str, dict[str, pd.DataFrame]],
) -> list[ListExcelComplianceProblem]:
    """
    This function checks if the excel files are compliant with the expected format.

    Args:
        excel_dfs: dictionary with the excel file name as key
                    and a dictionary with the sheet name as key and the dataframe.

    Returns:
        A list with the problems, or an empty list if there are no problems
    """
    return [
        res
        for filename in excel_dfs
        if (res := _make_formal_excel_compliance_check(excel_dfs[filename], filename)) is not None
    ]


def _make_formal_excel_compliance_check(
    excel_dfs: dict[str, pd.DataFrame], excel_name: str
) -> ListExcelComplianceProblem | None:
    problems = [p for sheet_name, df in excel_dfs.items() if (p := _df_shape_compliance(df, sheet_name)) is not None]
    if problems:
        return ListExcelComplianceProblem(excel_name, problems)
    return None


def _df_shape_compliance(df: pd.DataFrame, sheet_name: str) -> ListSheetComplianceProblem | None:
    problems = {}
    problems.update(_check_minimum_rows(df))
    problems.update(_check_min_num_col_present(df.columns))
    problems.update(_check_all_expected_translations_present(df.columns))
    _check_warn_unusual_columns(df.columns)
    if problems:
        return ListSheetComplianceProblem(sheet_name, problems)
    return None


def _check_minimum_rows(df: pd.DataFrame) -> dict[str, str]:
    if len(df) < 2:
        return {
            "minimum rows": "The Excel sheet must contain at least two rows, "
            "one for the list name and one row for a minimum of one node."
        }
    return {}


def _check_min_num_col_present(cols: pd.Index[str]) -> dict[str, str]:
    problem = {}
    node_langs = [_get_lang_string_from_column_name(c, r"\d+") for c in cols]
    if not any(node_langs):
        problem["missing columns for nodes"] = (
            "There is no column with the expected format for the list nodes: '[lang]_[column_number]'"
        )
    list_langs = [_get_lang_string_from_column_name(c, r"list") for c in cols]
    if not any(list_langs):
        problem["missing columns for list name"] = (
            "There is no column with the expected format for the list names: '[lang]_list'"
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


def _check_all_expected_translations_present(cols: pd.Index[str]) -> dict[str, str]:
    languages = {r for c in cols if (r := _get_lang_string_from_column_name(c)) is not None}
    all_nums = [str(n) for n in _get_hierarchy_nums(cols)]
    all_nums.append("list")

    def make_col_names(lang: str) -> set[str]:
        return {f"{lang}_{num}" for num in all_nums}

    expected_cols = set()
    for lang in languages:
        expected_cols.update(make_col_names(lang))
    if missing_cols := expected_cols - set(cols):
        return {
            "missing translations": f"All nodes must be translated into the same languages. "
            f"One or more translations for the following column(s) are missing: "
            f"{', '.join(missing_cols)}"
        }
    return {}
