from __future__ import annotations

import numpy as np
import pandas as pd
import regex

from dsp_tools.models.exceptions import UserError

languages = ["en", "de", "fr", "it", "rm"]


def read_excel_file(excel_filename: str) -> pd.DataFrame:
    """
    This function reads an Excel file, if there is a ValueError then it patches the openpyxl part that creates the
    error and opens it with that patch. It cleans and then returns the pd.DataFrame.

    Args:
        excel_filename: The name of the Excel file

    Returns: A pd.DataFrame
    """
    # load file
    try:
        read_df: pd.DataFrame = pd.read_excel(excel_filename)
    except ValueError:
        # Pandas relies on openpyxl to parse XLSX files.
        # A strange behaviour of openpyxl prevents pandas from opening files with some formatting properties
        # (unclear which formatting properties exactly).
        # Apparently, the excel2json test files have one of the unsupported formatting properties.
        # The following two lines of code help out.
        # Credits: https://stackoverflow.com/a/70537454/14414188
        # pylint: disable-next=import-outside-toplevel
        from unittest import mock

        p = mock.patch("openpyxl.styles.fonts.Font.family.max", new=100)
        p.start()
        read_df = pd.read_excel(excel_filename)
        p.stop()
    read_df = clean_data_frame(unclean_df=read_df)
    return read_df


def clean_data_frame(unclean_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function takes a pd.DataFrame and removes:
        - Leading and trailing spaces from the column names
        - Leading and trailing spaces from each cell
        - Any characters in the cells that are not part of any known language, for example, linebreaks and replaces it
          with a pd.NA.
        - Removes all rows that are empty in all columns

    Args:
        unclean_df: The pd.DataFrame that is to be cleaned

    Returns:
        pd.DataFrame which has the above-mentioned removed
    """
    # Remove leading and trailing blanks in column names and make them lower case
    cleaned_df = unclean_df.rename(columns=lambda x: x.strip().lower())
    # Remove the values of all cells that do not at least contain one character of any known language
    cleaned_df = cleaned_df.applymap(
        lambda x: str(x).strip() if pd.notna(x) and regex.search(r"[\w\p{L}]", str(x), flags=regex.U) else pd.NA
    )
    # drop all the rows that are entirely empty
    cleaned_df.dropna(axis=0, how="all", inplace=True)
    return cleaned_df


def check_required_columns_raises_error(check_df: pd.DataFrame, required_columns: set[str]) -> None:
    """
    This function takes a pd.DataFrame and a set of required column names. It checks if all the columns from the set
    are in the pd.DataFrame. Additional columns to the ones in the set are allowed. It raises an error if any columns
    are missing.

    Args:
        check_df: pd.DataFrame that is checked.
        required_columns: set of column names

    Raises:
        UserError if there are required columns missing
    """
    # This checks if the required columns are in the Dataframe. Other columns are also permitted.
    if not required_columns.issubset(set(check_df.columns)):
        raise UserError(
            f"The following columns are missing in the excel: " f"{required_columns.difference(set(check_df.columns))}"
        )


def check_duplicate_raise_erorr(check_df: pd.DataFrame, duplicate_column: str) -> None:
    """
    This function checks if a specified column contains duplicate values. Empty cells (pd.NA) also count as duplicates.
    If there are any duplicate values, it creates a string with the duplicates which are displayed in the error message.

    Args:
        check_df: pd.DataFrame that is checked for duplicates
        duplicate_column: Name of the column that must not contain duplicates

    Raises:
        UserError if there are duplicates in the column
    """
    # This checks if there are any duplicate values in a column,
    # pd.NA values also count as duplicates if there are several empty cells.
    if check_df[duplicate_column].duplicated().any():
        # If it does, it creates a string with all the duplicate values and raises an error.
        duplicate_values = ",".join(check_df[duplicate_column][check_df[duplicate_column].duplicated()].tolist())
        raise UserError(
            f"The column '{duplicate_column}' may not contain any duplicate values. "
            f"The following values appeared multiple times '{duplicate_values}'."
        )


def check_required_values(check_df: pd.DataFrame, required_values_columns: list[str]) -> dict[str : pd.Series]:
    """
    This function takes a pd.Dataframe and a list of column names which may not contain empty cells. If there are any
    empty cells in the column, it adds the column name and a boolean pd.Series to the dictionary. If there are no empty
    cells, then it is not included in the dictionary. If no column has any empty cells, then it returns an empty
    dictionary.

    Args:
        check_df: pd.DataFrame that is checked
        required_values_columns: a list of column names that may not contain empty cells

    Returns:
        a dictionary with the column names as key and pd.Series as values if there are any empty cells
    """
    # It checks if any of the values in a specified column are empty. If they are, they are added to the dictionary
    # with the column name as key and a boolean series as value that contain true for every pd.NA
    res_dict = {col: check_df[col].isnull() for col in required_values_columns if check_df[col].isnull().any()}
    # If all the columns are filled, then it returns an empty dictionary.
    return res_dict


def turn_bool_array_into_index_numbers(in_series: pd.Series[bool], true_remains: bool = True) -> list[int]:
    """
    This function takes a pd.Series which only contains boolean values, by default, the index numbers of the True values
    are extracted. If the parameter "true_remains" is True then it creates a list with the index numbers of the True
    values. If the parameter is False, then it inverses the pd.Series, and returns a list with the index numbers of
    the original False values.

    Args:
        in_series: pd.Series, which only contains True and False values
        true_remains: If True then the index numbers of the True values are extracted, if False then the reverse

    Returns:
        A list of index numbers
    """
    # By default, it takes the index numbers of the True values.
    # If the False are required, we need to invert the array.
    if not true_remains:
        in_series = ~in_series
    return list(in_series[in_series].index)


def get_wrong_row_numbers(wrong_row_dict: dict[str : pd.Series], true_remains: bool = True) -> dict[str : list[int]]:
    """
    This function takes a dictionary with column names as key and a boolean pd.Series as value. From the boolean
    pd.Series the index numbers of the True values are extracted, and the resulting list is the new value of the
    dictionary. This new dictionary is taken and to each index number 2 is added, so that it corresponds to the Excel
    row number. The result is intended to be used to communicate the exact location of a problem in an error message.

    Args:
        wrong_row_dict: The dictionary which contains column names and a boolean pd.Series
        true_remains: If True then the index of True is taken, if False then the index of False values is taken

    Returns:
        Dictionary with the column name as key and the row number as a list.
    """
    wrong_row_dict = {
        k: turn_bool_array_into_index_numbers(in_series=v, true_remains=true_remains) for k, v in wrong_row_dict.items()
    }
    return {k: [x + 2 for x in v] for k, v in wrong_row_dict.items()}


def update_dict_ifnot_value_none(additional_dict: dict, to_update_dict: dict) -> dict:
    """
    This function takes two dictionaries. The "to_update_dict" should be updated with the information from the
    "additional_dict" only if the value of a particular key is not None or pd.NA.

    Args:
        additional_dict: The dictionary which contains information that may be transferred
        to_update_dict: The dictionary to which the new information should be transferred

    Returns:
        The "to_update_dict" which the additional information
    """
    additional_dict = {k: v for k, v in additional_dict.items() if v is not None and v is not pd.NA}
    to_update_dict.update(additional_dict)
    return to_update_dict


def get_labels(df_row: pd.Series) -> dict[str:str]:
    """
    This function takes a pd.Series which has "label_[language tag]" in the index. If the value of the index is not
    pd.NA, the language tag and the value are added to a dictionary. If it is empty, it is omitted from the dictionary.

    Args:
        df_row: a pd.Series (usually a row of a pd.DataFrame) from which the content of the columns containing the
                label is extracted

    Returns:
        A dictionary with the language tag and the content of the cell
    """
    return {lang: df_row[f"label_{lang}"] for lang in languages if df_row[f"label_{lang}"] is not pd.NA}


def get_comments(df_row: pd.Series) -> dict[str:str] or None:
    """
    This function takes a pd.Series which has "comment_[language tag]" in the index. If the value of the index is not
    pd.NA, the language tag and the value are added to a dictionary. If it is empty, it is omitted from the dictionary.

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


def find_one_full_cell_in_cols(check_df: pd.DataFrame, required_columns: list[str]) -> pd.Series or None:
    """
    This function takes a pd.DataFrame and a list of column names where at least one cell must have a value per row.
    It creates a pd.Series with boolean values that are True if the cell is empty for each column. These series
    are then combined, and in the resulting np.array the values are only True if all the values from the pd.Series
    were True, meaning that in this row, all the specified columns have no values. If any of the values in the np.array
    are True, it converts it into a pd.Series (the data type is relevant at a later point) and returns it.
    If all the values are False then it returns None.

    Args:
        check_df: The pd.DataFrame which should be checked
        required_columns: A list of column names where at least one cell per row must have a value

    Returns:
        None if there is no problem or a pd.Series if there is a problem in a row
    """
    # In order to combine more than two arrays, we need to reduce the arrays, which takes a tuple
    result_arrays = tuple([check_df[col].isnull() for col in required_columns])
    # If all are True logical_and returns True otherwise False
    combined_array = np.logical_and.reduce(result_arrays)
    if any(combined_array):
        return pd.Series(combined_array)
    else:
        return None


def col_must_or_not_empty_based_on_other_col(
    check_df: pd.DataFrame,
    substring_list: list[str],
    substring_colname: str,
    check_empty_colname: str,
    must_have_value: bool,
) -> pd.Series or None:
    """
    It is presumed that the column "substring_colname" has no empty cells. Based on the string content of the individual
    rows, which is specified in the "substring_list", the cell is the column "check_empty_colname" is checked whether it
    is empty or not. The "substring_list" contains the different possibilities regarding the content of the cell. They
    are joined in a RegEx "|" which denotes "or". If it does not match any of the sub-strings, then the RegEx returns
    False which means that the value in the column "check_empty_colname" is not relevant.
    If the parameter "must_have_value" is True, then the cell in the "check_empty_colname" column must
    not be empty. If the parameter is set to False, then it must be empty.

    Args:
        check_df: The pd.DataFrame which is checked
        substring_list: A list of possible information that could be in the column "substring_colname"
        substring_colname: The name of the column that may contain any of the sub-strings
        check_empty_colname: The name of the column which is checked if it is empty or not
        must_have_value: True if the "check_empty_colname" should have a value or the reverse.

    Returns:
        None if all rows are correctly filled or empty. A series which contains True values for the rows, where it does
        not comply with the specifications.
    """
    na_series = check_df[check_empty_colname].isna()
    # If the cells have to be empty, we need to reverse the series
    if not must_have_value:
        na_series = ~na_series
    # This returns True if it finds the substring in the cell
    substring_array = check_df[substring_colname].str.contains("|".join(substring_list), na=False, regex=True)
    # If both are True logical_and returns True otherwise False
    combined_array = np.logical_and(na_series, substring_array)
    if any(combined_array):
        return pd.Series(combined_array)
    else:
        return None
