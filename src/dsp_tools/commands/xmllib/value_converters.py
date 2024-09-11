from typing import Any


def convert_to_bool(value: Any) -> str:
    """
    Turns a value into a bool

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    str_val = str(value).lower().strip()
    if str_val in ("false", "0", "0.0", "no"):
        return "false"
    elif str_val in ("true", "1", "1.0", "yes"):
        return "true"
    return str(value)
