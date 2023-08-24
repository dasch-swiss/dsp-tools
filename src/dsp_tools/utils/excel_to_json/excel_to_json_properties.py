import importlib.resources
import json
import warnings
import os
from typing import Any, Optional

import jsonpath_ng.ext
import jsonschema
import numpy as np
import pandas as pd
import regex

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.excel_to_json.utils import *

languages = ["en", "de", "fr", "it", "rm"]
language_label_col = ["label_en", "label_de", "label_fr", "label_it", "label_rm"]
mandatory_properties = ["name", "object", "gui_element"]


def _search_validation_error(
    list_properties: list[dict[str, Any]], excel_filename: str, validation_error: jsonschema.ValidationError
) -> str:
    err_msg_list = [f"The 'properties' section defined in the Excel file '{excel_filename}' did not pass validation."]
    json_path_to_property = regex.search(r"^\$\[(\d+)\]", validation_error.json_path)
    if json_path_to_property:
        # fmt: off
        wrong_property_name = (
            jsonpath_ng.ext.parse(json_path_to_property.group(0))
            .find(list_properties)[0]
            .value["name"]
        )
        # fmt: on
        excel_row = int(json_path_to_property.group(1)) + 2
        err_msg_list.append(f"The problematic property is '{wrong_property_name}' in Excel row {excel_row}.")
        affected_field = regex.search(
            r"name|labels|comments|super|subject|object|gui_element|gui_attributes",
            validation_error.json_path,
        )
        if affected_field:
            err_msg_list.append(
                f"The problem is that the column '{affected_field.group(0)}' has an invalid value: "
                f"{validation_error.message}"
            )
    else:
        err_msg_list.append(
            f"The error message is: {validation_error.message}\n" f"The error occurred at {validation_error.json_path}"
        )
    return "\n".join(err_msg_list)


def _validate_properties(
    properties_list: list[dict[str, Any]],
    excelfile: str,
) -> bool:
    """
    This function checks if the "properties" section of a JSON project file is valid according to the JSON schema,
    and if the property names are unique.

    Args:
        properties_list: the "properties" section of a JSON project as a list of dicts
        excelfile: path to the Excel file containing the properties

    Raises:
        UserError: if the validation fails

    Returns:
        True if the "properties" section passed validation
    """
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/properties-only.json").open(
        encoding="utf-8"
    ) as schema_file:
        properties_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=properties_list, schema=properties_schema)
    except jsonschema.ValidationError as err:
        err_msg = _search_validation_error(
            list_properties=properties_list, excel_filename=excelfile, validation_error=err
        )
        raise UserError(err_msg) from None
    return True


def _search_convert_numbers(value_str: str) -> str or int or float:
    if regex.search(r"^\d+\.\d+$", value_str):
        return float(value_str)
    elif regex.search(r"^\d+$", value_str):
        return int(value_str)
    else:
        return value_str


def _unpack_gui_attributes(gui_str: str) -> dict[str:str]:
    # Create a list with several attributes
    gui_list = [x.strip() for x in gui_str.split(",") if not x.strip() == ""]
    # create a sub list with the kex value pair of the attribute, if it is an empty string we exclude it
    # this error will be detected when checking for the length of the lists
    gui_list = [[sub.strip() for sub in x.split(":") if sub.strip() != ""] for x in gui_list]
    # if not all sublist contain 2 items something is wrong with the attribute
    if not all(len(sub) is 2 for sub in gui_list):
        raise IndexError
    return {sub[0]: sub[1] for sub in gui_list}


def _format_gui_attribute(attribute_str: str) -> dict[str : str or int or float]:
    attribute_dict = _unpack_gui_attributes(gui_str=attribute_str)
    return {attrb: _search_convert_numbers(value_str=val) for attrb, val in attribute_dict.items()}


def _get_gui_attribute(
    df_row: pd.Series,
    row_num: int,
    excel_filename: str,
) -> dict[str : int or str or float]:
    if pd.isnull(df_row["gui_attributes"]):
        return None
    # If the attribute is not in the correct format a called function may raise an IndexError
    try:
        return _format_gui_attribute(attribute_str=df_row["gui_attributes"])
    except IndexError:
        raise UserError(
            f"Row {row_num} of Excel file {excel_filename} contains invalid data in column 'gui_attributes'.\n"
            "The expected format is '[attribute: value, attribute: value]'."
        ) from None


def _row2prop(
    prop_row: pd.Series,
    row_count: int,
    excel_filename: str,
) -> dict[str, Any]:
    """
    Takes a row from a pandas DataFrame, reads its content, and returns a dict object of the property

    Args:
        prop_row: row from a pandas DataFrame that defines a property
        row_count: row number of Excel file
        excel_filename: name of the original Excel file

    Returns:
        dict object of the property
    """
    _property = {x: prop_row[x] for x in mandatory_properties}
    # These are also mandatory but require formatting
    _property.update(
        {"labels": get_labels(df_row=prop_row), "super": [s.strip() for s in prop_row["super"].split(",")]}
    )
    non_mandatory = {
        "comments": get_comments(df_row=prop_row),
        "gui_attributes": _get_gui_attribute(df_row=prop_row, row_num=row_count, excel_filename=excel_filename),
    }
    # These functions may return None, this is checked before the update
    _property = update_dict_ifnot_value_none(additional_dict=non_mandatory, to_update_dict=_property)
    return _property


def _check_gui_attributes(check_df: pd.DataFrame) -> dict[str : pd.Series] or None:
    mandatory_attributes = ["Spinbox", "List"]
    mandatory_check = col_must_or_not_empty_based_on_other_col(
        check_df=check_df,
        substring_list=mandatory_attributes,
        substring_colname="gui_element",
        check_empty_colname="gui_attributes",
        must_have_value=True,
    )
    no_attributes = ["Checkbox", "Date", "Geonames", "Richtext", "TimeStamp"]
    no_attribute_check = col_must_or_not_empty_based_on_other_col(
        check_df=check_df,
        substring_list=no_attributes,
        substring_colname="gui_element",
        check_empty_colname="gui_attributes",
        must_have_value=False,
    )
    # If neither has a problem we return None
    if mandatory_check is None and no_attribute_check is None:
        return None
    # If both have problems we combine the series
    elif mandatory_check is not None and no_attribute_check is not None:
        final_series = pd.Series(np.logical_or(mandatory_check, no_attribute_check))
    elif mandatory_check is not None:
        final_series = mandatory_check
    else:
        final_series = no_attribute_check
    # The boolean series is returned
    return {"wrong gui_attributes": final_series}


def _check_missing_values_in_row_raise_error(to_check_df: pd.DataFrame, excel_filename: str) -> None:
    # Every row in these columns must have a value
    required_values = ["name", "super", "object", "gui_element"]
    # If there are no problem it returns an empty dict
    missing_dict = check_required_values(check_df=to_check_df, required_values_columns=required_values)
    # This checks if the label columns have at least one value per row
    missing_labels = find_one_full_cell_in_cols(check_df=to_check_df, required_columns=language_label_col)
    # If everything is ok, we get None, otherwise we update the dict
    if missing_labels is not None:
        missing_dict.update({"label": missing_labels})
    # Some gui_element require a gui_attributes and others must not have one
    missing_gui_attributes = _check_gui_attributes(check_df=to_check_df)
    if missing_gui_attributes is not None:
        missing_dict.update(missing_gui_attributes)
    if missing_dict != {}:
        # Get the row numbers from the boolean series
        missing_dict = get_wrong_row_numbers(wrong_row_dict=missing_dict, true_remains=True)
        error_str = "\n".join([f"Column Name:{k} Row Number: {v}" for k, v in missing_dict.items()])
        raise UserError(
            f"The file '{excel_filename}' is missing values in some rows. See below for more information:\n"
            f"{error_str}"
        )


def _do_property_excel_compliance(compliance_df: pd.DataFrame, excel_filename: str) -> None:
    # If does not pass any one of the tests the function stops
    required_columns = {
        "name",
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
        "super",
        "object",
        "gui_element",
        "gui_attributes",
    }
    check_required_columns_raises_error(check_df=compliance_df, required_columns=required_columns)
    check_duplicate_raise_erorr(check_df=compliance_df, duplicate_column="name")
    _check_missing_values_in_row_raise_error(to_check_df=compliance_df, excel_filename=excel_filename)


def _rename_deprecated_hlist(rename_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    # If the deprecated feature is not in the df then return the df
    if "hlist" not in rename_df.columns:
        return rename_df
    warnings.warn(
        f"The file '{excel_filename}' has a column 'hlist', which is deprecated. "
        f"Please use the column 'gui_attributes' for the attribute 'hlist'."
    )
    # Reformat the string according to the new convention
    rename_df["hlist"] = rename_df["hlist"].apply(lambda x: f"hlist:{x}" if isinstance(x, str) else x)
    # If gui_attributes already exists we have to merge the columns
    if "gui_attributes" in rename_df.columns:
        # In case there is a hlist, it is the only valid value in gui_attributes and has precedence
        rename_df["hlist"] = rename_df["hlist"].fillna(rename_df["gui_attributes"])
        rename_df.pop("gui_attributes")
    rename_df.rename(columns={"hlist": "gui_attributes"}, inplace=True)
    return rename_df


def _rename_deprecated_lang_cols(rename_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    # If the columns are named correctly return the df
    if set(language_label_col).issubset(set(rename_df.columns)):
        return rename_df
    if set(languages).issubset(set(rename_df.columns)):
        warnings.warn(
            f"The file '{excel_filename}' uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )
    rename_dict = dict(zip(languages, language_label_col))
    rename_df.rename(columns=rename_dict, inplace=True)
    return rename_df


def _rename_deprecated_columnnames(in_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    in_df = _rename_deprecated_lang_cols(rename_df=in_df, excel_filename=excel_filename)
    in_df = _rename_deprecated_hlist(rename_df=in_df, excel_filename=excel_filename)
    return in_df


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
        UserError: if something went wrong

    Returns:
        a tuple consisting of the "properties" section as Python list,
            and the success status (True if everything went well)
    """
    property_df = read_excel_file(excel_filename=excelfile)

    property_df = _rename_deprecated_columnnames(in_df=property_df, excel_filename=excelfile)

    _do_property_excel_compliance(compliance_df=property_df, excel_filename=excelfile)

    # transform every row into a property
    props: list[dict[str, Any]] = []
    for index, row in property_df.iterrows():
        props.append(
            _row2prop(
                prop_row=row,
                row_count=int(str(index)),  # index is a label/index/hashable, but we need an int
                excel_filename=excelfile,
            )
        )

    # write final JSON file
    _validate_properties(properties_list=props, excelfile=excelfile)
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(props, file, indent=4, ensure_ascii=False)
            print('"properties" section was created successfully and written to file:', path_to_output_file)

    return props, True
