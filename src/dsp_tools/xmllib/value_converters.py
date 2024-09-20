from typing import Any


def convert_to_bool_string(value: Any) -> str:
    """
    Turns a value into a bool string, suitable for an XML.

    Args:
        value: value to transform

    Returns:
        'true' or 'false' if it is a known value,
        else it returns the original value as a string.
    """
    str_val = str(value).lower().strip()
    if str_val in ("false", "0", "0.0", "no"):
        return "false"
    elif str_val in ("true", "1", "1.0", "yes"):
        return "true"
    return str(value)
