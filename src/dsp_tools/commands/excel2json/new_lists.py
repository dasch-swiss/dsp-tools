from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import ListNodeProblem
from dsp_tools.commands.excel2json.models.input_error import ListSheetProblem
from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.commands.excel2json.models.list_node import ListRoot
from dsp_tools.models.exceptions import InputError


def _construct_ids(excel_dfs: dict[str, dict[str, pd.DataFrame]]) -> dict[str, dict[str, pd.DataFrame]]:
    all_file_dict = {}
    for filename, sheets in excel_dfs.items():
        single_file_dict = {}
        for sheet_name, df in sheets.items():
            single_file_dict[sheet_name] = _complete_id_one_df(df, _get_preferred_language(df.columns))
        all_file_dict[filename] = single_file_dict
    all_file_dict = _resolve_duplicate_ids_all_excels(all_file_dict)
    return _fill_parent_id_col_all_excels(all_file_dict)


def _fill_parent_id_col_all_excels(excel_dfs: dict[str, dict[str, pd.DataFrame]]) -> dict[str, dict[str, pd.DataFrame]]:
    all_file_dict = {}
    for filename, sheets in excel_dfs.items():
        single_file_dict = {}
        for sheet_name, df in sheets.items():
            single_file_dict[sheet_name] = _fill_parent_id_col_one_df(df, _get_preferred_language(df.columns))
        all_file_dict[filename] = single_file_dict
    return all_file_dict


def _fill_parent_id_col_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    """Create an extra column with the ID of the parent node."""
    # To start, all rows get the ID of the list. These will be overwritten if the row has another parent.
    df["parent_id"] = df.at[0, "id"]
    columns = _get_columns_of_preferred_lang(df.columns, preferred_language, r"\d+")
    for col in columns:
        grouped = df.groupby(col)
        for name, group in grouped:
            if group.shape[0] > 1:
                # The first row already has the correct ID assigned
                rest_index = list(group.index)[1:]
                df.loc[rest_index, "parent_id"] = group.at[group.index[0], "id"]
    return df


def _resolve_duplicate_ids_all_excels(
    excel_dfs: dict[str, dict[str, pd.DataFrame]],
) -> dict[str, dict[str, pd.DataFrame]]:
    ids = []
    for sheets in excel_dfs.values():
        for df in sheets.values():
            ids.extend(df["id"].tolist())
    counter = Counter(ids)
    if duplicate_ids := [item for item, count in counter.items() if count > 1]:
        return _remove_duplicate_ids_in_all_excel(duplicate_ids, excel_dfs)
    return excel_dfs


def _remove_duplicate_ids_in_all_excel(
    duplicate_ids: list[str], excel_dfs: dict[str, dict[str, pd.DataFrame]]
) -> dict[str, dict[str, pd.DataFrame]]:
    for sheets in excel_dfs.values():
        for df in sheets.values():
            preferred_lang = _get_preferred_language(df.columns)
            for i, row in df.iterrows():
                if row["id"] in duplicate_ids:
                    df.at[i, "id"] = _construct_non_duplicate_id_string(df.iloc[int(str(i))], preferred_lang)
    return excel_dfs


def _complete_id_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    if "ID (optional)" not in df.columns:
        df["ID (optional)"] = pd.NA
    df = _create_auto_id_one_df(df, preferred_language)
    df["id"] = df["ID (optional)"].fillna(df["auto_id"])
    df = _resolve_duplicate_ids_keep_custom_change_auto_id_one_df(df, preferred_language)
    return df


def _resolve_duplicate_ids_keep_custom_change_auto_id_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    if (duplicate_filter := df["id"].duplicated(keep=False)).any():
        for i in duplicate_filter.index[duplicate_filter]:
            if pd.isna(df.at[i, "ID (optional)"]):
                df.loc[i, "id"] = _construct_non_duplicate_id_string(df.iloc[i], preferred_language)
    return df


def _create_auto_id_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    """For every node without manual ID, take the label of the preferred language as ID."""
    df["auto_id"] = pd.NA
    if not df["ID (optional)"].isna().any():
        return df
    if pd.isna(df.at[0, "ID (optional)"]):
        df.loc[0, "auto_id"] = df.at[0, f"{preferred_language}_list"]
    column_names = sorted(_get_columns_of_preferred_lang(df.columns, preferred_language, r"\d+"), reverse=True)
    for i, row in df.iterrows():
        if pd.isna(row["ID (optional)"]):
            for col in column_names:
                if pd.notna(row[col]):
                    df.at[i, "auto_id"] = row[col]
                    break
    df = _resolve_duplicate_ids_for_auto_id_one_df(df, preferred_language)
    return df


def _resolve_duplicate_ids_for_auto_id_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    if (duplicate_filter := df["auto_id"].dropna().duplicated(keep=False)).any():
        for i in duplicate_filter.index[duplicate_filter]:
            df.at[i, "auto_id"] = _construct_non_duplicate_id_string(df.iloc[i], preferred_language)
    return df


def _construct_non_duplicate_id_string(row: pd.Series[Any], preferred_language: str) -> str:
    column_names = _get_columns_of_preferred_lang(row.index, preferred_language, r"\d+")
    column_names.insert(0, f"{preferred_language}_list")
    id_cols = [row[col] for col in column_names if pd.notna(row[col])]
    return ":".join(id_cols)


def _make_one_list(df: pd.DataFrame, sheet_name: str) -> ListRoot | ListSheetProblem:
    node_dict, node_problems = _make_list_nodes_from_df(df)
    nodes_for_root = _add_nodes_to_parent(node_dict, df.at[0, "id"]) if node_dict else []
    col_titles_of_root_cols = [x for x in df.columns if regex.search(r"^(en|de|fr|it|rm)_list$", x)]
    root = ListRoot.create(
        id_=df.at[0, "id"],
        labels=_get_labels(df.iloc[0], col_titles_of_root_cols),
        sheet_name=sheet_name,
        nodes=nodes_for_root,
        comments={},
    )
    match (root, node_problems):
        case (ListRoot(), list(ListNodeProblem())):
            return ListSheetProblem(sheet_name, root_problems={}, node_problems=node_problems)
        case (ListSheetProblem(), _):
            root.node_problems = node_problems
    return root


def _add_nodes_to_parent(node_dict: dict[str, ListNode], list_id: str) -> list[ListNode]:
    root_list = []
    for _, node in node_dict.items():
        if node.parent_id == list_id:
            root_list.append(node)
        else:
            node_dict[node.parent_id].sub_nodes.append(node)
    return root_list


def _make_list_nodes_from_df(df: pd.DataFrame) -> tuple[dict[str, ListNode], list[ListNodeProblem]]:
    columns_for_nodes = _get_reverse_sorted_columns_list(df)
    problems = []
    node_dict = {}
    for i, row in df[1:].iterrows():
        node = _make_one_node(row, columns_for_nodes, str(i))
        match node:
            case ListNode():
                node_dict[node.id_] = node
            case ListNodeProblem():
                problems.append(node)
    return node_dict, problems


def _make_one_node(row: pd.Series[Any], list_of_columns: list[list[str]], index: str) -> ListNode | ListNodeProblem:
    for col_group in list_of_columns:
        if labels := _get_labels(row, col_group):
            return ListNode.create(id_=row["id"], labels=labels, parent_id=row["parent_id"], sub_nodes=[])
    return ListNodeProblem(node_id=row["id"], problems={"Unknown": f"Unknown problem occurred in row number: {index}"})


def _get_reverse_sorted_columns_list(df: pd.DataFrame) -> list[list[str]]:
    numbers = sorted(_get_hierarchy_nums(df.columns), reverse=True)
    languages = _get_all_languages_for_columns(df.columns, r"\d+")
    return [[f"{lang}_{num}" for lang in languages] for num in numbers]


def _get_labels(row: pd.Series[Any], columns: list[str]) -> dict[str, str]:
    """
    Provided a df row and a list of column titles,
    create a mapping from language codes to the label of that language.
    (The label comes from the Excel cell at the intersection of the row with the column.)

    Parameters:
        row: A pandas Series representing a row of a DataFrame.
        columns: A list of column names.

    Returns:
        A dictionary with language codes as keys and the corresponding labels as values.
    """
    return {
        lang: row[col]
        for col in columns
        if not (pd.isna(row[col])) and (lang := _get_lang_string_from_column_name(col))
    }


def _get_lang_string_from_column_name(col_str: str, ending: str = r"(\d+|list)") -> str | None:
    if res := regex.search(rf"^(en|de|fr|it|rm)_{ending}$", col_str):
        return res.group(1)
    return None


def _get_columns_of_preferred_lang(
    columns: pd.Index[str], preferred_language: str, ending: str = r"(\d+|list)"
) -> list[str]:
    return sorted(col for col in columns if regex.search(rf"^{preferred_language}_{ending}$", col))


def _get_hierarchy_nums(columns: pd.Index[str]) -> list[int]:
    return sorted(
        list(set(int(res.group(2)) for x in columns if (res := regex.search(r"^(en|de|fr|it|rm)_(\d+)$", x))))
    )


def _get_all_languages_for_columns(columns: pd.Index[str], ending: str = r"(\d+|list)") -> set[str]:
    return set(res for x in columns if (res := _get_lang_string_from_column_name(x, ending)))


def _get_preferred_language(columns: pd.Index[str], ending: str = r"(\d+|list)") -> str:
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
