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
    column_numbers = _get_column_nums(df.columns)
    col_endings = [str(num) for num in column_numbers]
    col_endings.append("list")
    languages = _get_all_languages_for_columns(df.columns)
    all_cols = _make_columns(col_endings, languages)
    problems = []
    for column_group in all_cols:
        column_group.append("index")
        problems.extend(_check_one_hierarchy(column_group, df))
    if problems:
        return MissingTranslationsSheetProblem(sheet_name, problems)
    return None


def _check_one_hierarchy(columns: list[str], df: pd.DataFrame) -> list[MissingNodeTranslationProblem]:
    problems = []
    for _, row in df.iterrows():
        node = row[columns]
        problem = _check_one_node_for_translations(node)
        if problem:
            problems.append(problem)
    return problems


def _make_columns(nums: list[str], languages: set[str]) -> list[list[str]]:
    return [[f"{lang}_{num}" for lang in languages] for num in nums]


def _check_one_node_for_translations(node: pd.Series[Any]) -> MissingNodeTranslationProblem | None:
    if (missing := node.isna()).any():
        missing_cols = node[missing].index.tolist()
        return MissingNodeTranslationProblem(missing_cols, node["index"])
    return None
