from __future__ import annotations

from typing import Any

import pandas as pd
import regex

from dsp_tools.commands.excel2json.new_lists.models.deserialise import ColumnNodes
from dsp_tools.commands.excel2json.new_lists.models.deserialise import Columns
from dsp_tools.models.exceptions import InputError


def get_lang_string_from_column_name(col_str: str, ending: str = r"(\d+|list|comments)") -> str | None:
    """Gets the language tag of one string."""
    if res := regex.search(rf"^(en|de|fr|it|rm)_{ending}$", col_str):
        return res.group(1)
    return None


def get_columns_of_preferred_lang(
    columns: pd.Index[str], preferred_language: str, ending: str = r"(\d+|list|comments)"
) -> list[str]:
    """Get all the columns that contain the preferred language tag."""
    return sorted(col for col in columns if regex.search(rf"^{preferred_language}_{ending}$", col))


def get_column_info(df_cols: pd.Index[Any]) -> Columns:
    """
    Constructs and returns all the columns that should be present in the df based on the languages used.

    Args:
        df_cols: columns of the df

    Returns:
        Object with column info
    """
    hierarchy_nums = get_hierarchy_nums(df_cols)
    all_langs = get_all_languages_for_columns(df_cols)
    preferred_lang = get_preferred_language_from_columns(df_cols)
    node_cols = []
    for n in hierarchy_nums:
        node_cols.append(ColumnNodes(level_num=int(n), columns=[f"{lang}_{n}" for lang in all_langs]))
    comment_cols = []
    if get_all_languages_for_columns(df_cols, r"comments"):
        comment_cols = [f"{lang}_comments" for lang in all_langs]
    list_columns = [f"{lang}_list" for lang in all_langs]
    return Columns(
        preferred_lang=preferred_lang, list_cols=list_columns, comment_cols=comment_cols, node_cols=node_cols
    )


def get_hierarchy_nums(columns: pd.Index[str]) -> list[int]:
    """Get all the numbers that are used in the column names that contain a language tag."""
    return sorted(
        list(set(int(res.group(2)) for x in columns if (res := regex.search(r"^(en|de|fr|it|rm)_(\d+)$", x))))
    )


def get_all_languages_for_columns(columns: pd.Index[str], ending: str = r"(\d+|list|comments)") -> set[str]:
    """Get all the language tags for all the columns."""
    return set(res for x in columns if (res := get_lang_string_from_column_name(x, ending)))


def get_preferred_language_from_columns(columns: pd.Index[str], ending: str = r"(\d+|list|comments)") -> str:
    """Get the language tag of the preferred language."""
    match = {res.group(1) for x in columns if (res := regex.search(rf"^(en|de|fr|it|rm)_{ending}+$", x))}
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
