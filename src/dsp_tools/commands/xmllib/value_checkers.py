import json
from typing import Any

import pandas as pd
import regex


def is_bool(value: Any) -> bool:
    """
    Checks if a value is a bool or can be converted into a bool.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    value = str(value).lower()
    if value in ("false", "0", "0.0", "no"):
        return True
    elif value in ("true", "1", "1.0", "yes"):
        return True
    return False


def is_color(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """

    return bool(regex.search(r"^#[0-9a-f]{6}$", str(value).strip(), flags=regex.IGNORECASE))


def is_date(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """

    calendar = r"GREGORIAN|JULIAN|ISLAMIC"
    era = r"CE|BCE|BC|AD"
    year = r"\d{1,4}"
    month = r"\d{1,2}"
    day = r"\d{1,2}"
    full_date_pattern = rf"""
    ^
    (?:({calendar}):)?                         # optional calendar
    (?:({era}):)?                              # optional era
    ({year}(?:-{month})?(?:-{day})?)           # date
    (?::({era}))?                              # optional era
    (?::({year}(?:-{month})?(?:-{day})?))?     # optional date
    $
    """
    return bool(regex.search(full_date_pattern, str(value)))


def is_geoname(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    return is_integer(value)


def is_decimal(value: Any) -> bool:
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


def is_list(node: Any, listname: Any) -> bool:
    """
    Checks if a value is valid.

    Args:
        node: value to check
        listname: name of the list

    Returns:
        True if it is not empty
    """
    if any([pd.isna(node), pd.isna(listname)]):
        return False
    if len(str(node)) == 0:
        return False
    if len(str(listname)) == 0:
        return False
    return True


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
    return bool(regex.search(r"[\p{L}\d_!?]", value, flags=regex.UNICODE))


def is_timestamp(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    validation_regex = r"^\d{4}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(.\d{1,12})?(Z|[+-][0-1]\d:[0-5]\d)$"
    return bool(regex.search(validation_regex, str(value)))


def is_geometry(value: Any) -> str:
    """
    Validates if a value is a valid geometry object.

    Args:
        value: geometry object

    Returns:
        string with the validation message if it fails
    """
    msg = ""
    try:
        value_as_dict = json.loads(str(value))
        if value_as_dict["type"] not in ["rectangle", "circle", "polygon"]:
            msg += "\nThe 'type' of the JSON geometry object must be 'rectangle', 'circle', or 'polygon'."

        if not isinstance(value_as_dict["points"], list):
            msg += "\nThe 'points' of the JSON geometry object must be a list of points."
    except (json.JSONDecodeError, TypeError, IndexError, KeyError, AssertionError):
        msg += f"\n'{value}' is not a valid JSON geometry object."
    return msg
