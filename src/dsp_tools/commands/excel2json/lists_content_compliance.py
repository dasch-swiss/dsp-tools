from __future__ import annotations

from typing import Any

import pandas as pd

from dsp_tools.commands.excel2json.models.input_error import MissingNodeTranslationProblem
from dsp_tools.commands.excel2json.models.input_error import MissingTranslationsSheetProblem
from dsp_tools.commands.excel2json.new_lists import _get_all_languages_for_columns
from dsp_tools.commands.excel2json.new_lists import _get_column_nums


def _test_all_nodes_translated_into_all_languages(
    df: pd.DataFrame, sheet_name: str
) -> MissingTranslationsSheetProblem | None:
    col_endings = [str(num) for num in _get_column_nums(df.columns)]
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
