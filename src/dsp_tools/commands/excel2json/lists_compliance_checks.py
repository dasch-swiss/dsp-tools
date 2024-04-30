from __future__ import annotations

import warnings
from typing import Any

import pandas as pd
import regex
from loguru import logger

from dsp_tools.commands.excel2json.models.input_error import ListExcelProblem
from dsp_tools.commands.excel2json.models.input_error import ListSheetComplianceProblem
from dsp_tools.commands.excel2json.models.input_error import ListSheetContentProblem
from dsp_tools.commands.excel2json.models.input_error import MissingNodeTranslationProblem
from dsp_tools.commands.excel2json.models.input_error import MissingTranslationsSheetProblem
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.new_lists import _get_all_languages_for_columns
from dsp_tools.commands.excel2json.new_lists import _get_hierarchy_nums
from dsp_tools.commands.excel2json.new_lists import _get_lang_string_from_column_name
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError


def make_all_formal_excel_compliance_checks(
    excel_dfs: dict[str, dict[str, pd.DataFrame]],
) -> list[ListExcelProblem]:
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


def _make_formal_excel_compliance_check(excel_dfs: dict[str, pd.DataFrame], excel_name: str) -> ListExcelProblem | None:
    problems = [p for sheet_name, df in excel_dfs.items() if (p := _df_shape_compliance(df, sheet_name)) is not None]
    if problems:
        return ListExcelProblem(excel_name, problems)
    return None


def _df_shape_compliance(df: pd.DataFrame, sheet_name: str) -> Problem | None:
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


def make_all_list_content_compliance_checks(
    excel_dfs: dict[str, dict[str, pd.DataFrame]],
) -> list[ListExcelProblem]:
    """
    This function checks if the content of the excel files is compliant with the expected format.

    Args:
        excel_dfs: dictionary with the excel file name as key
                    and a dictionary with the sheet name as key and the dataframe.

    Returns:
        A list with the problems, or an empty list if there are no problems

    Raises:
        InputError: If any node is missing translations
    """
    _check_if_any_nodes_miss_translations(excel_dfs)
    return [
        res
        for filename in excel_dfs
        if (res := _make_content_excel_compliance_check(excel_dfs[filename], filename)) is not None
    ]


def _make_content_excel_compliance_check(
    excel_dfs: dict[str, pd.DataFrame], excel_name: str
) -> ListExcelProblem | None:
    problems: list[Problem] = [
        p for sheet_name, df in excel_dfs.items() if (p := _df_content_compliance(df, sheet_name)) is not None
    ]
    if problems:
        return ListExcelProblem(excel_name, problems)
    return None


def _df_content_compliance(df: pd.DataFrame, sheet_name: str) -> ListSheetContentProblem | None:
    problems: list[Problem] = [df]
    if problems:
        return ListSheetContentProblem(sheet_name, problems)
    return None


def _check_if_any_nodes_miss_translations(excel_dfs: dict[str, dict[str, pd.DataFrame]]) -> None:
    problems = []
    for filename, excel_sheets in excel_dfs.items():
        missing_translations = [
            p
            for sheet_name, df in excel_dfs.items()
            if (p := _check_all_nodes_translated_into_all_languages(df[filename], sheet_name)) is not None
        ]
        if missing_translations:
            problems.append(ListExcelProblem(filename, missing_translations))
    if problems:
        msg = [x.execute_error_protocol() for x in problems]
        msg = "\n\n---------------------------------------\n\n".join(msg)
        logger.error(msg)
        raise InputError(msg)


def _check_all_nodes_translated_into_all_languages(
    df: pd.DataFrame, sheet_name: str
) -> MissingTranslationsSheetProblem | None:
    col_endings = [str(num) for num in _get_hierarchy_nums(df.columns)]
    col_endings.append("list")
    languages = _get_all_languages_for_columns(df.columns)
    all_cols = _make_columns(col_endings, languages)
    problems = []
    for column_group in all_cols:
        problems.extend(_check_one_hierarchy(column_group, df))
    if problems:
        return MissingTranslationsSheetProblem(sheet_name, problems)
    return None


def _check_one_hierarchy(columns: list[str], df: pd.DataFrame) -> list[MissingNodeTranslationProblem]:
    problems = []
    for _, row in df.iterrows():
        if problem := _check_one_node_for_translations(row, columns):
            problems.append(problem)
    return problems


def _make_columns(nums: list[str], languages: set[str]) -> list[list[str]]:
    return [[f"{lang}_{num}" for lang in languages] for num in nums]


def _check_one_node_for_translations(row: pd.Series[Any], columns: list[str]) -> MissingNodeTranslationProblem | None:
    missing = row[columns].isna()
    if missing.any() and not missing.all():
        missing_cols = [str(index) for index, is_missing in missing.items() if is_missing]
        return MissingNodeTranslationProblem(missing_cols, row["row_number"])
    return None
