from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest import mock

import numpy as np
import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import DuplicateSheetProblem
from dsp_tools.commands.excel2json.models.input_error import DuplicatesInColumnProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import InvalidSheetNameProblem
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import RequiredColumnMissingProblem
from dsp_tools.commands.excel2json.models.ontology import LanguageDict
from dsp_tools.error.exceptions import InputError

languages = ["en", "de", "fr", "it", "rm"]


def read_and_clean_all_sheets(excelfile: str | Path) -> dict[str, pd.DataFrame]:
    """
    This function reads an Excel file with all its sheets.
    If there is a ValueError, it patches the openpyxl part that causes the error
    and opens it with that patch.
    It cleans the dataframes and then returns them in the form {sheet_name: dataframe}.

    Args:
        excelfile: path to the Excel file

    Returns:
        All sheets of the excel file, in the form of a dictionary {sheet_name: dataframe}

    Raises:
        InputError: If the sheets are not correctly named
    """
    try:
        df_dict = pd.read_excel(excelfile, sheet_name=None)
    except ValueError:
        # Pandas relies on openpyxl to parse XLSX files.
        # A strange behavior of openpyxl prevents pandas from opening files with some formatting properties
        # (unclear which formatting properties exactly).
        # Apparently, the excel2json test files have one of the unsupported formatting properties.
        # Credits: https://stackoverflow.com/a/70537454/14414188
        with mock.patch("openpyxl.styles.fonts.Font.family.max", new=100):
            df_dict = pd.read_excel(excelfile, sheet_name=None)
    _find_duplicate_col_names(str(excelfile), list(df_dict))
    try:
        return {name.strip(""): clean_data_frame(df) for name, df in df_dict.items()}
    except AttributeError:
        msg = InvalidSheetNameProblem(str(excelfile), list(df_dict.keys())).execute_error_protocol()
        raise InputError(msg) from None


def _find_duplicate_col_names(excelfile: str, col_names: list[str]) -> None:
    sheet_names = [str(x).lower().strip() for x in col_names]
    duplicate_names = list({x for x in sheet_names if sheet_names.count(x) > 1})
    if duplicate_names:
        msg = ExcelFileProblem(str(excelfile), [DuplicateSheetProblem(duplicate_names)]).execute_error_protocol()
        raise InputError(msg) from None


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


def check_contains_required_columns(
    df: pd.DataFrame, required_columns: set[str]
) -> None | RequiredColumnMissingProblem:
    """
    This function checks if all the columns from the set are in the pd.DataFrame.
    Additional columns to the ones in the set are allowed.

    Args:
        df: pd.DataFrame that is checked
        required_columns: set of column names

    Returns:
        An object if there is a problem else None.
    """
    if not required_columns.issubset(set(df.columns)):
        required = list(required_columns.difference(set(df.columns)))
        return RequiredColumnMissingProblem(columns=required)
    return None


def check_column_for_duplicate(df: pd.DataFrame, to_check_column: str) -> None | DuplicatesInColumnProblem:
    """
    This function checks if a specified column contains duplicate values.
    Empty cells (pd.NA) also count as duplicates.

    Args:
        df: pd.DataFrame that is checked for duplicates
        to_check_column: Name of the column that must not contain duplicates

    Returns:
        If there are problems it returns an object that stores the relevant user information.

    """
    if df[to_check_column].duplicated().any():
        duplicate_values = df[to_check_column][df[to_check_column].duplicated()].tolist()
        return DuplicatesInColumnProblem(
            column=to_check_column,
            duplicate_values=duplicate_values,
        )
    else:
        return None


def find_missing_required_values(
    df: pd.DataFrame, required_values_columns: list[str], sheetname: str | None = None
) -> list[PositionInExcel] | None:
    """
    If there are empty cells in the specified columns,
    It specifies the column and row numbers of all missing values and
    returns all the locations wrapped in the MissingValuesProblem

    Args:
        df: pd.DataFrame that is checked
        required_values_columns: a list of column names that may not contain empty cells
        sheetname: optional name of the Excel sheet

    Returns:
        Locations of missing values
        None if all are filled
    """
    if missing_values := check_required_values(df, required_values_columns):
        locations = []
        row_nums = get_wrong_row_numbers(missing_values)
        for col, nums in row_nums.items():
            locations.extend([PositionInExcel(sheet=sheetname, column=col, row=x) for x in nums])
        return locations
    return None


def check_required_values(df: pd.DataFrame, required_values_columns: list[str]) -> dict[str, pd.Series[bool]]:
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
    # If all the columns are filled, then it returns an empty dictionary.
    return {col: df[col].isnull() for col in required_values_columns if df[col].isnull().any()}


def _turn_bool_array_into_index_numbers(series: pd.Series[bool], true_remains: bool = True) -> list[int]:
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


def get_wrong_row_numbers(
    wrong_row_dict: dict[str, pd.Series[bool]], true_remains: bool = True
) -> dict[str, list[int]]:
    """
    From the boolean pd.Series the index numbers of the True values are extracted.
    The resulting list is the new value of the dictionary.
    This new dictionary is taken and to each index number 2 is added, so that it corresponds to the Excel row number.

    Args:
        wrong_row_dict: The dictionary which contains column names and a boolean pd.Series
        true_remains: If True then the index of True is taken, if False then the index of False values is taken

    Returns:
        Dictionary with the column name as key and the row number as a list.
    """
    wrong_row_int_dict = {
        k: _turn_bool_array_into_index_numbers(series=v, true_remains=true_remains) for k, v in wrong_row_dict.items()
    }
    return {k: [x + 2 for x in v] for k, v in wrong_row_int_dict.items()}


def get_labels(df_row: pd.Series[Any]) -> LanguageDict:
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
    labels = {lang: label for lang in languages if not pd.isna(label := df_row[f"label_{lang}"])}
    if not labels:
        labels = {lang: label for lang in languages if not pd.isna(label := df_row[lang])}
    return LanguageDict(labels)


def get_comments(df_row: pd.Series[Any]) -> LanguageDict | None:
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
    comments = {lang: comment for lang in languages if not pd.isna(comment := df_row[f"comment_{lang}"])}
    return LanguageDict(comments) if comments else None


def find_one_full_cell_in_cols(df: pd.DataFrame, required_columns: list[str]) -> pd.Series[bool] | None:
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
    return pd.Series(combined_array) if any(combined_array) else None


def col_must_or_not_empty_based_on_other_col(
    df: pd.DataFrame,
    substring_list: list[str],
    substring_colname: str,
    check_empty_colname: str,
    must_have_value: bool,
) -> pd.Series[bool] | None:
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
    return pd.Series(combined_array) if any(combined_array) else None


def add_optional_columns(df: pd.DataFrame, optional_col_set: set[str]) -> pd.DataFrame:
    """
    Adds columns to a df if they are not already present.
    The content of the columns is empty.

    Args:
        df: Dataframe
        optional_col_set: set of columns that may be added

    Returns:
        Dataframe with additional columns if they were not present
    """
    in_df_cols = set(df.columns)
    if not optional_col_set.issubset(in_df_cols):
        additional_col = list(optional_col_set.difference(in_df_cols))
        additional_df = pd.DataFrame(columns=additional_col, index=df.index)
        df = pd.concat(objs=[df, additional_df], axis=1)
    return df
