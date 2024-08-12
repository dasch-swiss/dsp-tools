from typing import Any

import pandas as pd
import regex


def is_string(value: Any) -> bool:
    """
    Checks if a value is a string.

    Args:
        value: value to check

    Returns:
        True if it is a string
    """
    if pd.isna(value):
        return False
    if regex.search(r"^(none|<NA>|-|n/a)$", value, flags=regex.IGNORECASE):
        return False
    return bool(regex.search(r"[\p{L}\d_!?]", value, flags=regex.UNICODE))
