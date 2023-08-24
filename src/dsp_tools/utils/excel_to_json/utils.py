from __future__ import annotations

import numpy as np
import pandas as pd
import regex

from dsp_tools.models.exceptions import UserError

languages = ["en", "de", "fr", "it", "rm"]


def read_excel_file(excel_filename: str) -> pd.DataFrame:
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
    # This checks if the required columns are in the excel. Other columns are also permitted.
    if not required_columns.issubset(set(check_df.columns)):
        raise UserError(
            f"The following columns are missing in the excel: " f"{required_columns.difference(set(check_df.columns))}"
        )


def check_duplicate_raise_erorr(check_df: pd.DataFrame, duplicate_column: str) -> None:
    # This checks if there are any duplicate values in a column,
    # pd.NA values also count as duplicates if there are several empty cells.
    if check_df[duplicate_column].duplicated().any():
        # If it does, it creates a string with all the duplicate values and raises an error.
        duplicate_values = ",".join(check_df[duplicate_column][check_df[duplicate_column].duplicated()].tolist())
        raise UserError(
            f"The column '{duplicate_column}' may not contain any duplicate values. "
            f"The following values appeared multiple times '{duplicate_values}'."
        )


def check_required_values(check_df: pd.DataFrame, required_values_columns: list[str]) -> dict:
    # It checks if any of the values in a specified column are empty. If they are, they are added to the dictionary
    # with the column name as key and a boolean series as value that contain true for every pd.NA
    res_dict = {col: check_df[col].isnull() for col in required_values_columns if check_df[col].isnull().any()}
    # If all the columns are filled then it returns an empty dictionary.
    return res_dict


def turn_bool_array_into_index_numbers(in_series: pd.Series, true_remains: bool = True) -> list[int]:
    # By default, it takes the index numbers of the True values.
    # If the False are required, we need to invert the array.
    if not true_remains:
        in_series = ~in_series
    return list(in_series[in_series].index)


def get_wrong_row_numbers(wrong_row_dict: dict[str : pd.Series], true_remains: bool = True) -> dict[str : list[int]]:
    wrong_row_dict = {
        k: turn_bool_array_into_index_numbers(in_series=v, true_remains=true_remains) for k, v in wrong_row_dict.items()
    }
    return {k: [x + 2 for x in v] for k, v in wrong_row_dict.items()}


def update_dict_ifnot_value_none(additional_dict: dict, to_update_dict: dict) -> dict:
    additional_dict = {k: v for (k, v) in additional_dict.items() if v is not None and v is not pd.NA}
    to_update_dict.update(additional_dict)
    return to_update_dict


def get_labels(df_row: pd.Series) -> dict[str:str]:
    return {lang: df_row[f"label_{lang}"] for lang in languages if df_row[f"label_{lang}"] is not pd.NA}


def get_comments(df_row: pd.Series) -> dict[str:str] or None:
    comments = {lang: df_row[f"comment_{lang}"] for lang in languages if df_row[f"comment_{lang}"] is not pd.NA}
    if comments == {}:
        return None
    else:
        return comments


def find_one_full_cell_in_cols(check_df: pd.DataFrame, required_columns: list[str]) -> pd.Series or None:
    # In order to combine more than two arrays, we need to reduce the arrays, which takes a tuple
    result_arrays = tuple([check_df[col].isnull() for col in required_columns])
    # If both are True logical_and returns True otherwise False
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
    na_series = check_df[check_empty_colname].isna()
    # If the cells have to be empty, we need to reverse the series
    if not must_have_value:
        na_series = ~na_series
    # This returns true if it finds the substring in the cell
    substring_array = check_df[substring_colname].str.contains("|".join(substring_list), na=False, regex=True)
    # If both are True logical_and returns True otherwise False
    combined_array = np.logical_and(na_series, substring_array)
    if any(combined_array):
        return pd.Series(combined_array)
    else:
        return None
