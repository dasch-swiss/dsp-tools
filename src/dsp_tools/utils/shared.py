from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any
from typing import Optional
from typing import TypeGuard
from typing import Union

import pandas as pd
import regex

from dsp_tools.commands.excel2xml.propertyelement import PropertyElement
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def prepare_dataframe(
    df: pd.DataFrame,
    required_columns: list[str],
    location_of_sheet: str,
) -> pd.DataFrame:
    """
    Takes a pandas DataFrame,
    strips the column headers from whitespaces and transforms them to lowercase,
    strips every cell from whitespaces and inserts "" if there is no string in it,
    and deletes the rows that don't have a value in one of the required cells.

    Args:
        df: pandas DataFrame
        required_columns: headers of the columns where a value is required
        location_of_sheet: for better error messages, provide this information of the caller

    Raises:
        BaseError: if one of the required columns doesn't exist, or if the resulting DataFrame would be empty

    Returns:
        prepared DataFrame
    """
    # strip column headers and transform to lowercase, so that the script doesn't break when the headers vary a bit
    new_df = df.rename(columns=lambda x: x.strip().lower())
    required_columns = [x.strip().lower() for x in required_columns]
    # strip every cell, and insert "" if there is no valid word in it
    new_df = new_df.map(
        lambda x: str(x).strip() if pd.notna(x) and regex.search(r"[\w\p{L}]", str(x), flags=regex.U) else ""
    )
    # delete rows that don't have the required columns
    for req in required_columns:
        if req not in new_df:
            raise BaseError(f"{location_of_sheet} requires a column named '{req}'")
        new_df = new_df[pd.notna(new_df[req])]
        new_df = new_df[[bool(regex.search(r"[\w\p{L}]", x, flags=regex.U)) for x in new_df[req]]]
    if len(new_df) < 1:
        raise BaseError(f"{location_of_sheet} requires at least one row")
    return new_df


def simplify_name(value: str) -> str:
    """
    Simplifies a given value in order to use it as node name

    Args:
        value: The value to be simplified

    Returns:
        str: The simplified value
    """
    simplified_value = value.lower()

    # normalize characters (p.ex. ä becomes a)
    simplified_value = unicodedata.normalize("NFKD", simplified_value)

    # replace forward slash and whitespace with a dash
    simplified_value = regex.sub("[/\\s]+", "-", simplified_value)

    # delete all characters which are not letters, numbers or dashes
    simplified_value = regex.sub("[^A-Za-z0-9\\-]+", "", simplified_value)

    return simplified_value


def check_notna(value: Optional[Any]) -> TypeGuard[Any]:
    """
    Check a value if it is usable in the context of data archiving. A value is considered usable if it is
     - a number (integer or float, but not np.nan)
     - a boolean
     - a string with at least one Unicode letter (matching the regex ``\\p{L}``) or number, or at least one _, !, or ?
       (The strings "None", "<NA>", "N/A", and "-" are considered invalid.)
     - a PropertyElement whose "value" fulfills the above criteria

    Args:
        value: any object encountered when analysing data

    Returns:
        True if the value is usable, False if it is N/A or otherwise unusable

    Examples:
        >>> check_notna(0)      == True
        >>> check_notna(False)  == True
        >>> check_notna("œ")    == True
        >>> check_notna("0")    == True
        >>> check_notna("_")    == True
        >>> check_notna("!")    == True
        >>> check_notna("?")    == True
        >>> check_notna(None)   == False
        >>> check_notna("None") == False
        >>> check_notna(<NA>)   == False
        >>> check_notna("<NA>") == False
        >>> check_notna("-")    == False
        >>> check_notna(" ")    == False
    """

    if isinstance(value, PropertyElement):
        value = value.value

    if isinstance(value, (bool, int)) or (
        isinstance(value, float) and pd.notna(value)
    ):  # necessary because isinstance(np.nan, float)
        return True
    elif isinstance(value, str):
        return bool(regex.search(r"[\p{L}\d_!?]", value, flags=regex.UNICODE)) and not bool(
            regex.search(r"^(none|<NA>|-|n/a)$", value, flags=regex.IGNORECASE)
        )
    else:
        return False


def parse_json_input(project_file_as_path_or_parsed: Union[str, Path, dict[str, Any]]) -> dict[str, Any]:
    """
    Check the input for a method that expects a JSON project definition, either as file path or as parsed JSON object:
    If it is parsed already, return it unchanged.
    If the input is a file path, parse it.

    Args:
        project_file_as_path_or_parsed: path to the JSON project definition, or parsed JSON object

    Raises:
        BaseError: if the input is invalid

    Returns:
        the parsed JSON object
    """
    project_definition: dict[str, Any] = {}
    if isinstance(project_file_as_path_or_parsed, dict):
        project_definition = project_file_as_path_or_parsed
    elif isinstance(project_file_as_path_or_parsed, (str, Path)) and Path(project_file_as_path_or_parsed).exists():
        with open(project_file_as_path_or_parsed, encoding="utf-8") as f:
            try:
                project_definition = json.load(f)
            except json.JSONDecodeError as e:
                msg = f"The input file '{project_file_as_path_or_parsed}' cannot be parsed to a JSON object."
                raise BaseError(msg) from e
    else:
        raise BaseError("Invalid input: The input must be a path to a JSON file or a parsed JSON object.")
    return project_definition
