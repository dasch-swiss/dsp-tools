from __future__ import annotations

from typing import Any

import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import ListNodeProblem
from dsp_tools.commands.excel2json.models.input_error import ListSheetProblem
from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.commands.excel2json.models.list_node import ListRoot
from dsp_tools.models.exceptions import InputError


def _handle_ids(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    df = _fill_id_column(df, preferred_language)
    df = _fill_parent_id(df, preferred_language)

    # Do compliance

    df["id"] = df["ID (optional)"].fillna(df["auto_id"])
    return df


def _fill_id_column(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    df["auto_id"] = pd.NA
    if not df["ID (optional)"].isna().any():
        return df
    if pd.isna(df.at[0, "ID (optional)"]):
        df.at[0, "auto_id"] = df.at[0, f"{preferred_language}_list"]
    columns = sorted(_get_columns_preferred_lang(df.columns, preferred_language), reverse=True)
    for i, row in df.iterrows():
        if pd.isna(row["ID (optional)"]):
            for col in columns:
                if pd.notna(row[col]):
                    df.at[i, "auto_id"] = row[col]
                    break
    return df


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


def _make_one_list(df: pd.DataFrame, sheet_name: str) -> ListRoot | ListSheetProblem:
    node_dict, problems = _make_list_nodes(df)
    cols = [x for x in df.columns if regex.search(r"^(en|de|fr|it|rm)_list$", x)]
    root = ListRoot.create(
        id_=df.at[0, "id"],
        labels=_get_labels(df.iloc[0], cols),
        sheet_name=sheet_name,
    )
    match (root, problems):
        case (ListRoot(), list(ListNodeProblem())):
            return ListSheetProblem(sheet_name, root_problems={}, nodes=problems)
        case (ListSheetProblem(), _):
            root.nodes = problems
            return root
    root.nodes = _add_nodes_to_parent(node_dict, df.at[0, "id"])
    return root


def _add_nodes_to_parent(node_dict: dict[str, ListNode], list_id: str) -> list[ListNode]:
    root_list = []
    for node_id, node in node_dict.items():
        if node.parent_id == list_id:
            root_list.append(node)
        else:
            node_dict[node.parent_id].sub_nodes.append(node)
    return root_list


def _make_list_nodes(df: pd.DataFrame) -> tuple[dict[str, ListNode], list[ListNodeProblem]]:
    list_of_columns = _get_reverse_sorted_columns_list(df)
    problems = []
    node_dict = {}
    for i, row in df[1:].iterrows():
        node = _make_one_node(row, list_of_columns)
        match node:
            case ListNode():
                node_dict[node.id_] = node
            case ListNodeProblem():
                problems.append(node)
    return node_dict, problems


def _make_one_node(row: pd.Series[Any], list_of_columns: list[list[str]]) -> ListNode | ListNodeProblem:
    for col_group in list_of_columns:
        labels = _get_labels(row, col_group)
        if labels:
            return ListNode.create(id_=row["id"], labels=labels, row_number=row["index"], parent_id=row["parent_id"])
    return ListNodeProblem(
        node_id=row["id"], problems={"Unknown": f"Unknown problem occurred in row number: {row["index"]}"}
    )


def _get_reverse_sorted_columns_list(df: pd.DataFrame) -> list[list[str]]:
    numbers = sorted(_get_column_nums(df.columns), reverse=True)
    languages = _get_all_languages_for_columns(df.columns, r"\d+")
    return [[f"{lang}_{num}" for lang in languages] for num in numbers]


def _get_labels(row: pd.Series[Any], columns: list[str]) -> dict[str, str]:
    return {lang: row[col] for col in columns if not (pd.isna(row[col])) and (lang := _get_lang_string(col))}


def _get_lang_string(col_str: str, ending: str = r"\d+") -> str | None:
    if res := regex.search(rf"^(en|de|fr|it|rm)_{ending}$", col_str):
        return res.group(1)
    return None


def _get_columns_preferred_lang(columns: pd.Index[str], preferred_language: str) -> list[str]:
    return sorted(col for col in columns if regex.search(rf"^{preferred_language}_\d+$", col))


def _get_column_nums(columns: pd.Index[str]) -> list[int]:
    return sorted(
        list(set(int(res.group(2)) for x in columns if (res := regex.search(r"^(en|de|fr|it|rm)_(\d+)$", x))))
    )


def _get_all_languages_for_columns(columns: pd.Index[str], ending: str) -> set[str]:
    return set(res for x in columns if (res := _get_lang_string(x, ending)))


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
