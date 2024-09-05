from __future__ import annotations

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
    if len(value) == 0:
        return False
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
        if regex.search(r"^\d+$", value):
            return True
    elif isinstance(value, int):
        return True
    return False


def is_float(value: Any) -> bool:
    """
    Checks if a value is a float.
    A valid integer is if it is a string, which can be converted into an integer,
    or a value of the type int.

    Args:
        value: value to check

    Returns:
        True if conforms to the above-mentioned criteria.
    """
    if isinstance(value, str):
        if regex.search(r"^\d+(\.\d+)?$", value):
            return True
    elif isinstance(value, int) or isinstance(value, float):
        return True
    return False
