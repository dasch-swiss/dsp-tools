import pandas as pd
import regex

from dsp_tools.models.exceptions import InputError


def _get_preferred_language_for_id(columns: pd.Series[str]) -> str:
    match = [res.group(1) for x in columns if (res := regex.search(r"^(en|de|fr|it|rm)_\d+$", x))]
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
