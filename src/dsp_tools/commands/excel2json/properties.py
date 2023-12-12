import importlib.resources
import json
import warnings
from typing import Any, Optional

import jsonpath_ng.ext
import jsonschema
import numpy as np
import pandas as pd
import regex

from dsp_tools.commands.excel2json.input_error import (
    InvalidExcelContentProblem,
    JsonValidationPropertyProblem,
    MissingValuesInRowProblem,
    MoreThanOneSheetProblem,
    PositionInExcel,
    Problem,
)
from dsp_tools.commands.excel2json.utils import (
    add_optional_columns,
    check_column_for_duplicate,
    check_contains_required_columns,
    check_required_values,
    col_must_or_not_empty_based_on_other_col,
    find_one_full_cell_in_cols,
    get_comments,
    get_labels,
    get_wrong_row_numbers,
    read_and_clean_all_sheets,
)
from dsp_tools.models.exceptions import InputError

languages = ["en", "de", "fr", "it", "rm"]
language_label_col = ["label_en", "label_de", "label_fr", "label_it", "label_rm"]
mandatory_properties = ["name", "object", "gui_element"]


def _find_validation_problem(
    properties_list: list[dict[str, Any]],
    validation_error: jsonschema.ValidationError,
) -> JsonValidationPropertyProblem:
    """
    This function takes a list of properties, which were transformed from an Excel to a json.
    The validation raised an error.
    This function searches for the exact location in the Excel where the error was caused.
    It returns a string with a user-friendly version of the original json validation error message.

    Args:
        properties_list: List of properties
        validation_error: The error from the calling function

    Returns:
        A class containing the information which is used in the Error message.
    """
    if json_path_to_property := regex.search(r"^\$\[(\d+)\]", validation_error.json_path):
        # fmt: off
        wrong_property_name = (
            jsonpath_ng.ext.parse(json_path_to_property.group(0))
            .find(properties_list)[0]
            .value["name"]
        )
        # fmt: on
        excel_row = int(json_path_to_property.group(1)) + 2

        column = None
        val_msg = None
        if affected_field := regex.search(
            r"name|labels|comments|super|subject|object|gui_element|gui_attributes",
            validation_error.json_path,
        ):
            column = affected_field.group(0)
            val_msg = validation_error.message

        return JsonValidationPropertyProblem(
            problematic_property=wrong_property_name,
            excel_position=PositionInExcel(column=column, row=excel_row),
            original_msg=val_msg,
        )
    return JsonValidationPropertyProblem(
        original_msg=validation_error.message,
        message_path=validation_error.json_path,
    )


def _validate_properties(
    properties_list: list[dict[str, Any]],
    excelfile: str,
) -> None:
    """
    This function checks if the "properties" section of a JSON project file is valid, according to the JSON schema.

    Args:
        properties_list: the "properties" section of a JSON project as a list of dicts
        excelfile: path to the Excel file containing the properties

    Raises:
        InputError: if the validation fails
    """
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/properties-only.json").open(
        encoding="utf-8"
    ) as schema_file:
        properties_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=properties_list, schema=properties_schema)
    except jsonschema.ValidationError as err:
        err_msg = _find_validation_problem(properties_list=properties_list, validation_error=err)
        msg = f"\nThe Excel file '{excelfile}' did not pass validation." + err_msg.execute_error_protocol()
        raise InputError(msg) from None


def _search_convert_numbers(value_str: str) -> str | int | float:
    """
    This function takes a string and searches if the string contains a float or an integer.
    In those cases, it converts the string to the corresponding data type.
    If it is not a float or integer, it returns the string as is.

    Args:
        value_str: The value which is checked and may be converted

    Returns:
        A int if the string was an integer, float if the string was a float or str if it was neither
    """
    if regex.search(r"^\d+$", value_str):
        return int(value_str)
    elif regex.search(r"^\d+\.\d+$", value_str):
        return float(value_str)
    else:
        return value_str


def _unpack_gui_attributes(attribute_str: str) -> dict[str, str]:
    """
    This function takes a string which contains the gui_attributes.
    If the string is not formatted correctly, this raises an IndexError.

    Args:
        attribute_str: A string containing the gui_attributes

    Returns:
        A dictionary with the gui_attribute name as key and the attribute as value.

    Raises:
        IndexError: if the sub-lists do not contain each two items
    """
    # Create a list with several attributes
    gui_list = [x.strip() for x in attribute_str.split(",") if x.strip() != ""]
    # create a sub list with the key value pair of the attribute.
    # If it is an empty string, we exclude it.
    sub_gui_list = [[sub.strip() for sub in x.split(":") if sub.strip() != ""] for x in gui_list]
    # if not all sublist contain two items, something is wrong with the attribute
    if any(len(sub) != 2 for sub in sub_gui_list):
        raise IndexError
    return {sub[0]: sub[1] for sub in sub_gui_list}


def _format_gui_attribute(attribute_str: str) -> dict[str, str | int | float]:
    """
    This function takes a string containing the information about the gui_attributes and formats it correctly.

    Args:
        attribute_str: A string containing the attributes

    Returns:
        A dictionary with the attribute name as a key and the attribute as value.

    Raises:
        IndexError: if the attributes are not formatted correctly
    """
    attribute_dict = _unpack_gui_attributes(attribute_str=attribute_str)
    return {attrib: _search_convert_numbers(value_str=val) for attrib, val in attribute_dict.items()}


def _get_gui_attribute(
    df_row: pd.Series,
    row_num: int,
) -> dict[str, int | str | float] | InvalidExcelContentProblem | None:
    """
    This function checks if the cell "gui_attributes" is empty.
    If it is, it returns None.
    If there is information, it extracts and formats it correctly.

    Args:
        df_row: Row of a pd.DataFrame
        row_num: The number of the row (index + 2)

    Returns:
        A gui_attribute dictionary or None if there are no attributes
    """
    if pd.isnull(df_row["gui_attributes"]):
        return None
    # If the attribute is not in the correct format, a called function may raise an IndexError
    try:
        return _format_gui_attribute(attribute_str=df_row["gui_attributes"])
    except IndexError:
        return InvalidExcelContentProblem(
            expected_content="attribute: value, attribute: value",
            actual_content=df_row["gui_attributes"],
            excel_position=PositionInExcel(column="gui_attributes", row=row_num),
        )


def _row2prop(df_row: pd.Series, row_num: int, excelfile: str) -> dict[str, Any]:
    """
    Takes a row from a pd.DataFrame, reads its content, and returns a dict object of the property.

    Args:
        df_row: row from a pd.DataFrame that defines a property
        row_num: row number of Excel file
        excelfile: name of the original Excel file

    Returns:
        dict object of the property

    Raises:
        InputError: if there are any formal mistakes in the "gui_attributes" column
    """
    _property = {x: df_row[x] for x in mandatory_properties} | {
        "labels": get_labels(df_row=df_row),
        "super": [s.strip() for s in df_row["super"].split(",")],
    }

    gui_attrib = _get_gui_attribute(df_row=df_row, row_num=row_num)
    match gui_attrib:
        case dict():
            _property["gui_attributes"] = gui_attrib
        case InvalidExcelContentProblem():
            msg = f"There is a problem with the excel file: '{excelfile}'\n" + gui_attrib.execute_error_protocol()
            raise InputError(msg) from None

    if comment := get_comments(df_row=df_row):
        _property["comments"] = comment

    return _property


def _check_compliance_gui_attributes(df: pd.DataFrame) -> dict[str, pd.Series] | None:
    """
    This function takes a pd.DataFrame and checks if the "gui_attributes" column is filled correctly.
    If any or all of the checks fail,
    it creates a dictionary with a pd.Series as value which contains True for all rows where
    there is a problem otherwise, it returns None.

    Args:
        df: pd.DataFrame that should be checked

    Returns:
        A dictionary with a pd.Series that contains the information where there is a problem or None if all the
        checks passed.

    Raises:
        InputError if any of the checks fail
    """
    mandatory_attributes = ["Spinbox", "List"]
    mandatory_check = col_must_or_not_empty_based_on_other_col(
        df=df,
        substring_list=mandatory_attributes,
        substring_colname="gui_element",
        check_empty_colname="gui_attributes",
        must_have_value=True,
    )
    no_attributes = ["Checkbox", "Date", "Geonames", "Richtext", "TimeStamp"]
    no_attribute_check = col_must_or_not_empty_based_on_other_col(
        df=df,
        substring_list=no_attributes,
        substring_colname="gui_element",
        check_empty_colname="gui_attributes",
        must_have_value=False,
    )
    # If neither has a problem, we return None
    match mandatory_check, no_attribute_check:
        case None, None:
            return None
        case pd.Series(), pd.Series():
            final_series = pd.Series(np.logical_or(mandatory_check, no_attribute_check))  # type: ignore[arg-type]
        case pd.Series(), None:
            final_series = mandatory_check
        case None, pd.Series:
            final_series = no_attribute_check
    # The boolean series is returned
    return {"gui_attributes": final_series}


def _check_missing_values_in_row(df: pd.DataFrame) -> None | list[MissingValuesInRowProblem]:
    """
    This function checks if all the required values are in the df.
    If all the checks are ok, the function ends without any effect.
    If there are any missing values, the function returns the information where the problem is located at.

    Args:
        df: pd.DataFrame that is to be checked

    Returns:
        If there are problems, it returns objects that store the information about it.
    """
    # Every row in these columns must have a value
    required_values = ["name", "super", "object", "gui_element"]
    # If there are no problems, it returns an empty dict
    missing_dict = check_required_values(df=df, required_values_columns=required_values)
    # This checks if the label columns have at least one value per row
    missing_labels = find_one_full_cell_in_cols(df=df, required_columns=language_label_col)
    # If everything is ok, we get None, otherwise we update the dict
    if missing_labels is not None:
        missing_dict.update({"label": missing_labels})
    # Some gui_element require a gui_attributes and others must not have one
    missing_gui_attributes = _check_compliance_gui_attributes(df=df)
    if missing_gui_attributes is not None:
        missing_dict.update(missing_gui_attributes)
    if missing_dict:
        # Get the row numbers from the boolean series
        missing_dict = get_wrong_row_numbers(wrong_row_dict=missing_dict, true_remains=True)
        return [MissingValuesInRowProblem(column=col, row_numbers=row_nums) for col, row_nums in missing_dict.items()]
    else:
        return None


def _do_property_excel_compliance(df: pd.DataFrame, excelfile: str) -> None:
    """
    This function calls three separate functions which each checks if the pd.DataFrame is as we expect it.
    Each of these functions raises an InputError if there is a problem.
    If the checks do not fail, this function ends without an effect.

    Args:
        df: The pd.DataFrame that is checked
        excelfile: The name of the original Excel file

    Raises:
        InputError: if any of the checks fail
    """
    # If it does not pass any one of the tests, the function stops
    required_columns = {
        "name",
        "super",
        "object",
        "gui_element",
        "gui_attributes",
    }
    problems: list[Problem | None] = [
        check_contains_required_columns(df=df, required_columns=required_columns),
        check_column_for_duplicate(df=df, to_check_column="name"),
    ]
    if missing_vals_check := _check_missing_values_in_row(df=df):
        problems.extend(missing_vals_check)
    if any(problems):
        extra = [problem.execute_error_protocol() for problem in problems if problem]
        msg = [f"There is a problem with the excel file: '{excelfile}'", *extra]
        raise InputError("\n\n".join(msg))


def _rename_deprecated_hlist(df: pd.DataFrame, excelfile: str) -> pd.DataFrame:
    """
    This function deals with Excel files that do conform to a previous format.
    If the old column names are not in the pd.DataFrame, then it returns it as was.

    Args:
        df: The pd.DataFrame which is checked and renamed
        excelfile: Name of the original Excel file.

    Returns:
        Renamed pd.DataFrame or the original one

    Warnings:
        A warning for the user that the Excel file is not compliant with the new specifications
    """
    # If the deprecated feature is not in the df, then return the df
    if "hlist" not in df.columns:
        return df
    warnings.warn(
        f"The file '{excelfile}' has a column 'hlist', which is deprecated. "
        f"Please use the column 'gui_attributes' for the attribute 'hlist'."
    )
    # Reformat the string according to the new convention
    df["hlist"] = df["hlist"].apply(lambda x: f"hlist:{x}" if isinstance(x, str) else x)
    # If gui_attributes already exists we have to merge the columns
    if "gui_attributes" in df.columns:
        # In case there is a hlist, it is the only valid value in gui_attributes and has precedence
        df["hlist"] = df["hlist"].fillna(df["gui_attributes"])
        df.pop("gui_attributes")
    df = df.rename(columns={"hlist": "gui_attributes"})
    return df


def _rename_deprecated_lang_cols(df: pd.DataFrame, excelfile: str) -> pd.DataFrame:
    """
    This function takes a pd.DataFrame and checks if the columns with the language label are named according to the old
    specifications.
    If they are, it renames them and informs the user that an old format is used.
    Otherwise, it returns the pd.Dataframe as was.

    Args:
        df: pd.DataFrame, which is to be checked
        excelfile: Name of the Excel file

    Returns:
        pd.DataFrame which has the columns renamed according to the new format

    Warnings:
        A warning for the user that the Excel file is not compliant with the new specifications
    """
    # If the columns are named correctly, return the df
    if set(language_label_col).issubset(set(df.columns)):
        return df
    if set(languages).issubset(set(df.columns)):
        warnings.warn(
            f"The file '{excelfile}' uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )
    rename_dict = dict(zip(languages, language_label_col))
    df = df.rename(columns=rename_dict)
    return df


def _rename_deprecated_columnnames(df: pd.DataFrame, excelfile: str) -> pd.DataFrame:
    """
    This function calls two other functions that check and rename a deprecated Excel format.
    Afterward, the pd.DataFrame is compliant with the current format.
    In case the pd.DataFrame was already in the current format, the function passes without an effect.

    Args:
        df: pd.DataFrame that is checked and renamed
        excelfile: Name of the original Excel

    Returns:
        pd.DataFrame that is renamed

    Warnings:
        Two user warnings if the pd.DataFrame is not according to the current specifications
    """
    df = _rename_deprecated_lang_cols(df=df, excelfile=excelfile)
    df = _rename_deprecated_hlist(df=df, excelfile=excelfile)
    return df


def excel2properties(
    excelfile: str,
    path_to_output_file: Optional[str] = None,
) -> tuple[list[dict[str, Any]], bool]:
    """
    Converts properties described in an Excel file into a "properties" section which can be inserted into a JSON
    project file.

    Args:
        excelfile: path to the Excel file containing the properties
        path_to_output_file: if provided, the output is written into this JSON file

    Raises:
        InputError: if something went wrong

    Returns:
        a tuple consisting of the "properties" section as a Python list,
            and the success status (True if everything went well)
    """

    property_df = _read_check_property_df(excelfile)

    property_df = _rename_deprecated_columnnames(df=property_df, excelfile=excelfile)

    _do_property_excel_compliance(df=property_df, excelfile=excelfile)

    # Not all columns have to be filled, users may delete some for ease of use, but it would generate an error later
    property_df = add_optional_columns(
        df=property_df,
        optional_col_set={
            "label_en",
            "label_de",
            "label_fr",
            "label_it",
            "label_rm",
            "comment_en",
            "comment_de",
            "comment_fr",
            "comment_it",
            "comment_rm",
        },
    )

    # transform every row into a property
    props = [
        _row2prop(
            df_row=row,
            row_num=int(str(index)) + 2,  # index is a label/index/hashable, but we need an int
            excelfile=excelfile,
        )
        for index, row in property_df.iterrows()
    ]

    # write final JSON file
    _validate_properties(properties_list=props, excelfile=excelfile)
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(props, file, indent=4, ensure_ascii=False)
            print(f"properties section was created successfully and written to file '{path_to_output_file}'")

    return props, True


def _read_check_property_df(excelfile: str) -> pd.DataFrame | None:
    sheets_df_dict = read_and_clean_all_sheets(excelfile=excelfile)
    if len(sheets_df_dict) != 1:
        msg = str(MoreThanOneSheetProblem("properties.xlsx", list(sheets_df_dict.keys())))
        raise InputError(msg)
    return list(sheets_df_dict.values())[0]
