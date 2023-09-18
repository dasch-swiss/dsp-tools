from __future__ import annotations

from typing import Any
from unittest import mock

import numpy as np
import pandas as pd
import regex

from dsp_tools.models.exceptions import UserError

languages = ["en", "de", "fr", "it", "rm"]


def read_and_clean_excel_file(excelfile: str, sheetname: str | int = 0) -> pd.DataFrame:
    """
    This function reads an Excel file, if there is a ValueError then it patches the openpyxl part that creates the
    error and opens it with that patch.
    It cleans and then returns the pd.DataFrame.

    Args:
        excelfile: The name of the Excel file
        sheetname: The name or index (zero-based) of the Excel sheet, by default it reads the first

    Returns:
        A pd.DataFrame
    """
    try:
        read_df: pd.DataFrame = pd.read_excel(excelfile, sheet_name=sheetname)
    except ValueError:
        # Pandas relies on openpyxl to parse XLSX files.
        # A strange behavior of openpyxl prevents pandas from opening files with some formatting properties
        # (unclear which formatting properties exactly).
        # Apparently, the excel2json test files have one of the unsupported formatting properties.
        # Credits: https://stackoverflow.com/a/70537454/14414188
        with mock.patch("openpyxl.styles.fonts.Font.family.max", new=100):
            read_df = pd.read_excel(excelfile, sheet_name=sheetname)
    read_df = clean_data_frame(df=read_df)
    return read_df


def clean_data_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function takes a pd.DataFrame and removes:
        - Leading and trailing spaces from the column names
        - Leading and trailing spaces from each cell and any characters in the cells that are not part of any known
        language, for example, linebreaks and replaces it with a pd.NA.
        - Removes all rows that are empty in all columns

    Args:
        df: The pd.DataFrame that is to be cleaned

    Returns:
        pd.DataFrame which has the above-mentioned removed
    """
    # Remove leading and trailing blanks in column names and make them lower case
    df = df.rename(columns=lambda x: x.strip().lower())
    # Remove the values of all cells that do not at least contain one character of any known language and removes
    # leading and trailing spaces.
    df = df.map(
        lambda x: str(x).strip() if pd.notna(x) and regex.search(r"[\w\p{L}]", str(x), flags=regex.U) else pd.NA
    )
    # drop all the rows that are entirely empty
    df = df.dropna(axis=0, how="all")
    return df


def check_contains_required_columns_else_raise_error(df: pd.DataFrame, required_columns: set[str]) -> None:
    """
    This function takes a pd.DataFrame and a set of required column names.
    It checks if all the columns from the set are in the pd.DataFrame.
    Additional columns to the ones in the set are allowed.
    It raises an error if any columns are missing.

    Args:
        df: pd.DataFrame that is checked
        required_columns: set of column names

    Raises:
        UserError: if there are required columns missing
    """
    if not required_columns.issubset(set(df.columns)):
        raise UserError(
            f"The following columns are missing in the excel:\n" f"{required_columns.difference(set(df.columns))}"
        )


def check_column_for_duplicate_else_raise_error(df: pd.DataFrame, to_check_column: str) -> None:
    """
    This function checks if a specified column contains duplicate values.
    Empty cells (pd.NA) also count as duplicates.
    If there are any duplicate values, it creates a string with the duplicates which are displayed in the error message.

    Args:
        df: pd.DataFrame that is checked for duplicates
        to_check_column: Name of the column that must not contain duplicates

    Raises:
        UserError: if there are duplicates in the column
    """
    if df[to_check_column].duplicated().any():
        # If it does, it creates a string with all the duplicate values and raises an error.
        duplicate_values = ",".join(df[to_check_column][df[to_check_column].duplicated()].tolist())
        raise UserError(
            f"The column '{to_check_column}' may not contain any duplicate values. "
            f"The following values appeared multiple times '{duplicate_values}'."
        )


def check_required_values(df: pd.DataFrame, required_values_columns: list[str]) -> dict[str, pd.Series]:
    """
    If there are any empty cells in the column, it adds the column name and a boolean pd.Series to the dictionary.
    If there are no empty cells, then it is not included in the dictionary.
    If no column has any empty cells, then it returns an empty dictionary.

    Args:
        df: pd.DataFrame that is checked
        required_values_columns: a list of column names that may not contain empty cells

    Returns:
        a dictionary with the column names as key and pd.Series as values if there are any empty cells
    """
    # It checks if any of the values in a specified column are empty. If they are, they are added to the dictionary
    # with the column name as key and a boolean series as value that contain true for every pd.NA
    res_dict = {col: df[col].isnull() for col in required_values_columns if df[col].isnull().any()}
    # If all the columns are filled, then it returns an empty dictionary.
    return res_dict


def turn_bool_array_into_index_numbers(series: pd.Series[bool], true_remains: bool = True) -> list[int]:
    """
    This function takes a pd.Series containing boolean values.
    By default, this method extracts the index numbers of the True values.
    If the index numbers of the False values are required, the parameter "true_remains" should be turned to False.

    Args:
        series: pd.Series, which only contains True and False values
        true_remains: True if the index numbers of True are required, likewise with False

    Returns:
        A list of index numbers
    """
    # If the False are required, we need to invert the array.
    if not true_remains:
        series = ~series
    return list(series[series].index)


def get_wrong_row_numbers(wrong_row_dict: dict[str, pd.Series], true_remains: bool = True) -> dict[str, list[int]]:
    """
    From the boolean pd.Series the index numbers of the True values are extracted.
    The resulting list is the new value of the dictionary.
    This new dictionary is taken and to each index number 2 is added, so that it corresponds to the Excel row number.
    The result is intended to be used to communicate the exact location of a problem in an error message.

    Args:
        wrong_row_dict: The dictionary which contains column names and a boolean pd.Series
        true_remains: If True then the index of True is taken, if False then the index of False values is taken

    Returns:
        Dictionary with the column name as key and the row number as a list.
    """
    wrong_row_dict = {
        k: turn_bool_array_into_index_numbers(series=v, true_remains=true_remains) for k, v in wrong_row_dict.items()
    }
    return {k: [x + 2 for x in v] for k, v in wrong_row_dict.items()}


def update_dict_if_not_value_none(additional_dict: dict[Any, Any], to_update_dict: dict[Any, Any]) -> dict[Any, Any]:
    """
    This function takes two dictionaries.
    The "to_update_dict" should be updated with the information from the "additional_dict"
    only if the value of a particular key is not None or pd.NA.

    Args:
        additional_dict: The dictionary which contains information that may be transferred
        to_update_dict: The dictionary to which the new information should be transferred

    Returns:
        The "to_update_dict" which the additional information
    """
    additional_dict = {k: v for k, v in additional_dict.items() if v is not None and v is not pd.NA}
    to_update_dict.update(additional_dict)
    return to_update_dict


def get_labels(df_row: pd.Series) -> dict[str, str]:
    """
    This function takes a pd.Series which has "label_[language tag]" in the index.
    If the value of the index is not pd.NA, the language tag and the value are added to a dictionary.
    If it is empty, it is omitted from the dictionary.

    Args:
        df_row: a pd.Series (usually a row of a pd.DataFrame) from which the content of the columns containing the
                label is extracted

    Returns:
        A dictionary with the language tag and the content of the cell
    """
    return {lang: df_row[f"label_{lang}"] for lang in languages if df_row[f"label_{lang}"] is not pd.NA}


def get_comments(df_row: pd.Series) -> dict[str, str] | None:
    """
    This function takes a pd.Series which has "comment_[language tag]" in the index.
    If the value of the index is not pd.NA, the language tag and the value are added to a dictionary.
    If it is empty, it is omitted from the dictionary.

    Args:
        df_row: a pd.Series (usually a row of a pd.DataFrame) from which the content of the columns containing the
                comment is extracted

    Returns:
        A dictionary with the language tag and the content of the cell
    """
    comments = {lang: df_row[f"comment_{lang}"] for lang in languages if df_row[f"comment_{lang}"] is not pd.NA}
    if comments == {}:
        return None
    else:
        return comments


def find_one_full_cell_in_cols(df: pd.DataFrame, required_columns: list[str]) -> pd.Series | None:
    """
    This function takes a pd.DataFrame and a list of column names where at least one cell must have a value per row.
    A pd.Series with boolean values is returned, True if any rows do not have a value in at least one column

    Args:
        df: The pd.DataFrame which should be checked
        required_columns: A list of column names where at least one cell per row must have a value

    Returns:
        None if there is no problem or a pd.Series if there is a problem in a row
    """
    # The series has True if the cell is empty
    # In order to combine more than two arrays, we need to reduce the arrays, which takes a tuple
    result_arrays = tuple(df[col].isnull() for col in required_columns)
    # If all are True logical_and returns True otherwise False
    combined_array = np.logical_and.reduce(result_arrays)
    # if any of the values are True, it is turned into a pd.Series
    if any(combined_array):
        return pd.Series(combined_array)
    else:
        return None


def col_must_or_not_empty_based_on_other_col(
    df: pd.DataFrame,
    substring_list: list[str],
    substring_colname: str,
    check_empty_colname: str,
    must_have_value: bool,
) -> pd.Series | None:
    """
    It is presumed that the column "substring_colname" has no empty cells.
    Based on the string content of the individual rows, which is specified in the "substring_list",
    the cell in the column "check_empty_colname" is checked whether it is empty or not.
    The "substring_list" contains the different possibilities regarding the content of the cell.
    If the parameter "must_have_value" is True, then the cell in the "check_empty_colname" column must not be empty.
    If the parameter is set to False, then it must be empty.

    Args:
        df: The pd.DataFrame which is checked
        substring_list: A list of possible information that could be in the column "substring_colname"
        substring_colname: The name of the column that may contain any of the sub-strings
        check_empty_colname: The name of the column which is checked if it is empty or not
        must_have_value: True if the "check_empty_colname" should have a value or the reverse.

    Returns:
        None if all rows are correctly filled or empty.
        A series which contains True values for the rows, where it does
        not comply with the specifications.
    """
    na_series = df[check_empty_colname].isna()
    # If the cells have to be empty, we need to reverse the series
    if not must_have_value:
        na_series = ~na_series
    # This returns True if it finds the substring in the cell, they are joined in a RegEx "|" which denotes "or".
    # If it does not match any of the sub-strings, then the RegEx returns False,
    # which means that the value in the column "check_empty_colname" is not relevant.
    substring_array = df[substring_colname].str.contains("|".join(substring_list), na=False, regex=True)
    # If both are True logical_and returns True otherwise False
    combined_array = np.logical_and(na_series, substring_array)
    if any(combined_array):
        return pd.Series(combined_array)
    else:
        return None


def add_optional_columns(df: pd.DataFrame, optional_col_set: set[str]) -> pd.DataFrame:
    """
    This function takes a df and a set of columns which may not be in the df,
    but whose absence could cause errors in the code following.
    The columns are added, without any values in the rows.

    Args:
        df: Original df
        optional_col_set: set of columns that may not be in the df, if they are not, they will be added.

    Returns:
        The df with the added columns.
        If all are already there, the df is returned unchanged.
    """
    in_df_cols = set(df.columns)
    if not optional_col_set.issubset(in_df_cols):
        additional_col = list(optional_col_set.difference(in_df_cols))
        additional_df = pd.DataFrame(columns=additional_col, index=df.index)
        df = pd.concat(objs=[df, additional_df], axis=1)
    return df
