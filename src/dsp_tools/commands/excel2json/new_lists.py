from __future__ import annotations

import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import ListNodeProblem
from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.models.exceptions import InputError


def _fill_id_column(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    if pd.isna(df.at[0, "ID (optional)"]):
        df.loc[0, "ID (optional)"] = df.at[0, f"{preferred_language}_list"]


def _fill_parent_id(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    df["parent_id"] = df.at[0, "ID (optional)"]
    columns = _get_columns_preferred_lang(df.columns, preferred_language)
    for col in columns:
        grouped = df.groupby(col)
        for name, group in grouped:
            if name == "nan":
                pass
            elif group.shape[0] > 1:
                rest_index = list(group.index)[1:]
                df.loc[rest_index, "parent_id"] = group.at[group.index[0], "ID (optional)"]
    return df


def _make_one_node(row: pd.Series, col_number: str) -> ListNode | ListNodeProblem:
    node_id = _get_id(row, col_number)
    labels = _get_labels(row, col_number)
    return ListNode.create(node_id, labels, int(str(row.name)))


def _get_id(row: pd.Series[str], col_number: str) -> str:
    return (
        row.get("ID (optional)")
        if pd.notna(row.get("ID (optional)"))
        else row.get(f"{_get_preferred_language(row.index, str(col_number))}_{col_number}")
    )


def _get_labels(row: pd.Series[str], col_ending: str) -> dict[str, str]:
    languages = _get_all_languages_for_columns(row.index, col_ending)
    return {lang: row.get(f"{lang}_{col_ending}") for lang in languages if pd.notna(row[f"{lang}_{col_ending}"])}


def _get_columns_preferred_lang(columns: pd.Index[str], preferred_language: str) -> list[str]:
    return sorted(col for col in columns if regex.search(rf"^{preferred_language}_\d+$", col))


def _get_remaining_column_nums(columns: pd.Index[str], current_col_number: int) -> list[int]:
    numbers = [int(res.group(2)) for x in columns if (res := regex.search(r"^(en|de|fr|it|rm)_(\d+)$", x))]
    return sorted(list(set(x for x in numbers if x >= current_col_number)))


def _get_all_languages_for_columns(columns: pd.Index[str], ending: str) -> list[str]:
    return [res.group(1) for x in columns if (res := regex.search(rf"^(en|de|fr|it|rm)_{ending}$", x))]


def _get_preferred_language(columns: pd.Index[str], ending: str) -> str:
    match = [res.group(1) for x in columns if (res := regex.search(rf"^(en|de|fr|it|rm)_{ending}+$", x))]
    if "en" in match:
        return "en"
    elif "de" in match:
        return "de"
    elif "fr" in match:
        return "fr"
    elif "it" in match:
        return "it"
    elif "rm" in match:
        return "rm"
    msg = (
        f"The columns may only contain the languages: 'en', 'de', 'fr', 'it', 'rm'.\n"
        f"The columns are: {" ".join(columns)}"
    )
    raise InputError(msg)
