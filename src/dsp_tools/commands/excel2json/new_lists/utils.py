from __future__ import annotations

from collections import defaultdict

import pandas as pd
import regex

from dsp_tools.models.exceptions import InputError


def get_lang_string_from_column_name(col_str: str, ending: str = r"(\d+|list)") -> str | None:
    """Gets the language tag of one string."""
    if res := regex.search(rf"^(en|de|fr|it|rm)_{ending}$", col_str):
        return res.group(1)
    return None


def get_columns_of_preferred_lang(
    columns: pd.Index[str], preferred_language: str, ending: str = r"(\d+|list)"
) -> list[str]:
    """Get all the columns that contain the preferred language tag."""
    return sorted(col for col in columns if regex.search(rf"^{preferred_language}_{ending}$", col))


def get_hierarchy_nums(columns: pd.Index[str]) -> list[int]:
    """Get all the numbers that are used in the column names that contain a language tag."""
    return sorted(
        list(set(int(res.group(2)) for x in columns if (res := regex.search(r"^(en|de|fr|it|rm)_(\d+)$", x))))
    )


def get_all_languages_for_columns(columns: pd.Index[str], ending: str = r"(\d+|list)") -> set[str]:
    """Get all the language tags for all the columns."""
    return set(res for x in columns if (res := get_lang_string_from_column_name(x, ending)))


def get_preferred_language(columns: pd.Index[str], ending: str = r"(\d+|list)") -> str:
    """Get the language tag of the preferred language."""
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


def get_node_label_col_mapper(columns: pd.Index[str]) -> dict[str, set[str]]:
    """
    Returns a dictionary with the number of the column as key and the list of column names as value.

    Args:
        columns: columns of df

    Returns:
        dictionary with number to column mapping
    """
    found = [res for x in columns if (res := regex.search(r"^(en|de|fr|it|rm)_(\d+)$", x))]
    label_col_dict = defaultdict(set)
    for col in found:
        label_col_dict[int(col.group(2))].add(col.string)
    return label_col_dict


def get_list_cols(columns: pd.Index[str]) -> set[str]:
    """Get all the column names of the list node"""
    return {x for x in columns if regex.search(r"^(en|de|fr|it|rm)_list$", x)}


def get_comment_cols(columns: pd.Index[str]) -> set[str]:
    """Get all the column names of the comment."""
    return {x for x in columns if regex.search(r"^(en|de|fr|it|rm)_comment$", x)}
