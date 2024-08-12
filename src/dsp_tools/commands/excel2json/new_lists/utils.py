from __future__ import annotations

import pandas as pd
import regex

from dsp_tools.models.exceptions import InputError


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
