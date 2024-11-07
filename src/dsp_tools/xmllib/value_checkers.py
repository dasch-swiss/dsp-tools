import json
from typing import Any

import pandas as pd
import regex


def is_nonempty_value(value: Any) -> bool:
    """
    Check if a value is not empty.

    Args:
        value: value to check

    Returns:
        True if it is not empty
    """
    if isinstance(value, str) and len(value) == 0:
        return False
    return not pd.isna(value)


def is_bool_like(value: Any) -> bool:
    """
    Checks if a value is a bool or can be converted into a bool.
    It is case-insensitive, meaning that the words can also be capitalised.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    value = str(value).lower().strip()
    if value in ("false", "0", "0.0", "no", "non", "nein"):
        return True
    elif value in ("true", "1", "1.0", "yes", "oui", "ja"):
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
    Checks if a value is a date value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """

    calendar_optional = r"((GREGORIAN|JULIAN|ISLAMIC):)?"
    first_era_optional = r"((CE|BCE|BC|AD):)?"
    second_area_optional = r"(:(CE|BCE|BC|AD))?"
    date = r"\d{1,4}(?:-\d{1,2}){0,2}"
    date_mandatory = rf"({date})"
    date_optional = rf"(:{date})?"
    full_date_pattern = (
        rf"^{calendar_optional}{first_era_optional}{date_mandatory}{second_area_optional}{date_optional}$"
    )
    return bool(regex.search(full_date_pattern, str(value)))


def is_geoname(value: Any) -> bool:
    """
    Checks if a value is a geoname value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    return is_integer(value)


def is_decimal(value: Any) -> bool:
    """
    Checks if a value is a float, an integer, or a string which can be converted into a float.

    Args:
        value: value to check

    Returns:
        True if conforms to the above-mentioned criteria.
    """
    if pd.isna(value):
        return False

    match value:
        case bool():
            return False
        case int() | float():
            return True
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_integer(value: Any) -> bool:
    """
    Checks if a value is an integer or a string which can be converted into an integer.

    Args:
        value: value to check

    Returns:
        True if conforms to the above-mentioned criteria.
    """
    match value:
        case bool():
            return False
        case int():
            return True
        case str():
            return bool(regex.search(r"^\d+$", value))
        case _:
            return False


def is_string_like(value: Any) -> bool:
    """
    Checks if a value is a string.

    Args:
        value: value to check

    Returns:
        True if it is a string
    """
    if pd.isna(value):
        return False
    value = str(value).strip()
    if len(value) == 0:
        return False
    return bool(regex.search(r"\S", value, flags=regex.UNICODE))


def is_timestamp(value: Any) -> bool:
    """
    Checks if a value is a valid timestamp.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    validation_regex = r"^\d{4}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(\.\d{1,12})?(Z|[+-][0-1]\d:[0-5]\d)$"
    return bool(regex.search(validation_regex, str(value)))


def find_geometry_problem(value: Any) -> str:
    """
    Validates if a value is a valid geometry object.

    Args:
        value: geometry object

    Returns:
        String with the validation message if it fails, else an empty string.
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


def is_dsp_iri(value: Any) -> bool:
    """
    Check if a value is a valid internal DSP IRI.

    Args:
        value: IRI

    Returns:
        True if it is valid, else false
    """
    return bool(regex.search(r"^http://rdfh\.ch/\d{4}/", str(value)))


def is_dsp_ark(value: Any) -> bool:
    """
    Checks if a value is a valid ARK.

    Args:
        value: ARK

    Returns:
        True if it is valid, else false
    """
    return bool(regex.search(r"^ark:/", str(value)))
