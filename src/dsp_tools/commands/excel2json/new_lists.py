from __future__ import annotations

import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.commands.excel2json.models.list_node import ListRoot
from dsp_tools.models.exceptions import InputError


def _make_one_list(df: pd.DataFrame, sheet_name: str, excel_name: str) -> ListRoot:
    get_lang_col = _get_preferred_language_for_id(df.columns, "list")
    groups = df.groupby(f"{get_lang_col}_list")
    if len(groups) != 1:
        raise InputError(
            f"The Excel: '{excel_name}' and sheet: '{sheet_name}' must only have one unique value in the list column."
        )
    df = groups.get_group(groups.first().name)
    node_cols = [res.group(1) for x in df.columns if (res := regex.search(r"^[en|de|fr|it|rm]_(\d)+$", x))]
    nodes = []
    for col in sorted(node_cols):
        nodes.extend(_create_nodes(df, col))
    root = ListRoot(
        id_=_get_id(df.iloc[0], "list"),
        labels=_get_labels(df.iloc[0], "list"),
        nodes=nodes,
    )
    return root


def _create_nodes(df: pd.DataFrame, col_number: str) -> list[ListNode]:
    nodes = []
    preferred_lang = _get_preferred_language_for_id(df.columns, "list")
    groups = df.groupby(f"{preferred_lang}_{col_number}")
    for name, group in groups:
        nodes.append(_make_one_node(group, col_number))
    # go through the nodes and add the children
    return nodes


def _make_one_node(row: pd.Series, col_number: str) -> ListNode:
    node_id = _get_id(row, col_number)
    labels = _get_labels(row, col_number)
    return ListNode(node_id, labels, int(row.index))


def _get_id(row: pd.Series, col_number: str) -> str:
    return (
        row.get("ID (optional)")
        if pd.notna(row["ID (optional)"])
        else row.get(f"{_get_preferred_language_for_id(row.index, str(col_number))}_{col_number}")
    )


def _get_labels(row: pd.Series, col_ending: str) -> dict[str, str]:
    languages = _get_all_languages_for_columns(row.index, col_ending)
    return {lang: row.get(f"{lang}_{col_ending}") for lang in languages if pd.notna(row[f"{lang}_{col_ending}"])}


def _get_all_languages_for_columns(columns: pd.Index[str], ending: str) -> list[str]:
    return [res.group(1) for x in columns if (res := regex.search(rf"^(en|de|fr|it|rm)_{ending}$", x))]


def _get_preferred_language_for_id(columns: pd.Index[str], ending: str) -> str:
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
