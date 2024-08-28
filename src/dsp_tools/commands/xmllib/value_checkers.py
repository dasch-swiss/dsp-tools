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
    value = str(value)
    if regex.search(r"^(none|<NA>|-|n/a)$", value, flags=regex.IGNORECASE):
        return False
    return bool(regex.search(r"[\p{L}\d_!?]", value, flags=regex.UNICODE))


def is_integer(value: Any) -> bool:
    """
    Checks if a value is an integer.
    A valid integer is if it is a string, which can be converted into an integer,
    or a value of the type int.

    Args:
        value: value to check

    Returns:
        True if conforms to the above-mentioned criteria.
    """
    if isinstance(value, str):
        if not regex.search(r"^\d+$", value):
            return False
    elif not isinstance(value, int):
        return False
    return True
