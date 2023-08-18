import importlib.resources
import json
import warnings
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
    # TODO: rewrite
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/properties-only.json").open(
        encoding="utf-8"
    ) as schema_file:
        properties_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=properties_list, schema=properties_schema)
    except jsonschema.ValidationError as err:
        err_msg = f"The 'properties' section defined in the Excel file '{excelfile}' did not pass validation. "
        json_path_to_property = regex.search(r"^\$\[(\d+)\]", err.json_path)
        if json_path_to_property:
            # fmt: off
            wrong_property_name = (
                jsonpath_ng.ext.parse(json_path_to_property.group(0))
                .find(properties_list)[0]
                .value["name"]
            )
            # fmt: on
            excel_row = int(json_path_to_property.group(1)) + 2
            err_msg += f"The problematic property is '{wrong_property_name}' in Excel row {excel_row}. "
            affected_field = regex.search(
                r"name|labels|comments|super|subject|object|gui_element|gui_attributes",
                err.json_path,
            )
            if affected_field:
                err_msg += (
                    f"The problem is that the column '{affected_field.group(0)}' has an invalid value: {err.message}"
                )
        else:
            err_msg += f"The error message is: {err.message}\nThe error occurred at {err.json_path}"
        raise UserError(err_msg) from None
    return True


def _get_gui_attribute(
    # TODO: Test and then revise (this is somewhat butchered maybe re-copy it from original)
    df_row: pd.Series,
    row_num: int,
    excel_filename: str,
) -> dict[str:Any] or None:
    # TODO: revise and add check that it exists for all lists, how would hlist look like? -> only list name
    gui_element = df_row["gui_element"]
    gui_attributes = dict()
    if df_row.get("hlist"):
        gui_attributes["hlist"] = df_row["hlist"]
    if df_row.get("gui_attributes"):
        pairs = df_row["gui_attributes"].split(",")
        for pair in pairs:
            if pair.count(":") != 1:
                raise UserError(
                    f"Row {row_num} of Excel file {excel_filename} contains invalid data in column 'gui_attributes'. "
                    "The expected format is 'attribute: value[, attribute: value]'."
                )
            attr, val = [x.strip() for x in pair.split(":")]
            if regex.search(r"^\d+\.\d+$", val):
                val = float(val)
            elif regex.search(r"^\d+$", val):
                val = int(val)
            gui_attributes[attr] = val
    return gui_attributes


def _row2prop(
    # TODO: Test
    row: pd.Series,
    row_count: int,
    excelfile: str,
) -> dict[str, Any]:
    """
    Takes a row from a pandas DataFrame, reads its content, and returns a dict object of the property

    Args:
        row: row from a pandas DataFrame that defines a property
        row_count: row number of Excel file
        excelfile: name of the original Excel file

    Raises:
        UserError: if the row contains invalid data

    Returns:
        dict object of the property
    """
    mandatory_properties = ["name", "object", "gui_element"]
    _property = {x: row[x] for x in mandatory_properties}
    _property.update({"labels": get_labels(df_row=row), "super": [s.strip() for s in row["super"].split(",")]})
    non_mandatory = {
        "comments": get_comments(df_row=row),
        "gui_attributes": _get_gui_attribute(df_row=row, row_num=row_count, excel_filename=excelfile),
    }
    _property = update_dict_ifnot_value_none(new_dict=non_mandatory, to_update_dict=_property)
    return _property


def _check_gui_attributes(check_df: pd.DataFrame) -> dict[str : pd.Series] or None:
    mandatory_attributes = ["Spinbox", "List"]
    mandatory_check = col_must_or_not_empty_based_on_other_col(
        input_df=check_df,
        substring_list=mandatory_attributes,
        substring_colname="gui_element",
        check_empty_colname="gui_attributes",
        must_have_value=True,
    )
    no_attributes = ["Checkbox", "Date", "Geonames", "Richtext", "TimeStamp"]
    no_attribute_check = col_must_or_not_empty_based_on_other_col(
        input_df=check_df,
        substring_list=no_attributes,
        substring_colname="gui_element",
        check_empty_colname="gui_attributes",
        must_have_value=False,
    )
    if mandatory_check is None and no_attribute_check is None:
        return None
    elif mandatory_check is not None and no_attribute_check is not None:
        list_combined = pd.Series(np.logical_or(mandatory_check, no_attribute_check))
    elif mandatory_check is not None:
        list_combined = mandatory_check
    else:
        list_combined = no_attribute_check
    return {"wrong gui_attributes": list_combined}


def _check_missing_values_in_row(to_check_df: pd.DataFrame, excel_filename: str) -> None:
    required_values = ["name", "super", "object", "gui_element"]
    missing_dict = check_required_values(check_df=to_check_df, required_values_columns=required_values)
    missing_labels = find_one_full_cell_in_cols(check_df=to_check_df, required_columns=language_label_col)
    if missing_labels is not None:
        missing_dict.update({"label": missing_labels})
    missing_gui_attributes = _check_gui_attributes(check_df=to_check_df)
    if missing_gui_attributes is not None:
        missing_dict.update(missing_gui_attributes)
    if missing_dict != {}:
        missing_dict = get_wrong_row_numbers(wrong_row_dict=missing_dict, true_remains=True)
        error_str = "\n".join([f"Column Name:{k} Row Number: {v}" for k, v in missing_dict.items()])
        raise UserError(
            f"The file '{excel_filename}' is missing values in some rows. See below for more information:\n"
            f"{error_str}"
        )


def _do_property_excel_compliance(compliance_df: pd.DataFrame, excel_filename: str) -> None:
    # If does not pass any one of the test the function stops
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
    _check_missing_values_in_row(to_check_df=compliance_df, excel_filename=excel_filename)


def _rename_hlist(input_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    # If the deprecated feature is not in the df then return the df
    if "hlist" not in input_df.columns:
        return input_df
    warnings.warn(
        f"The file '{excel_filename}' has a column 'hlist', which is deprecated. "
        f"Please use the column 'gui_attributes' for the attribute 'hlist'."
    )
    input_df["hlist"] = input_df["hlist"].apply(lambda x: f"hlist:{x}" if isinstance(x, str) else x)
    if "gui_attributes" not in input_df.columns:
        input_df.rename(columns={"hlist": "gui_attributes"}, inplace=True)
    else:
        input_df["combined"] = pd.NA
        # In case there is a hlist, it is the only valid value in gui_attributes and has precedence
        input_df["combined"] = input_df["combined"].fillna(input_df["hlist"])
        # The cells that do not have a hlist will be filled with the values from gui_attributes
        input_df["combined"] = input_df["combined"].fillna(input_df["gui_attributes"])
        # The original column is removed and the combined column renamed
        input_df.pop("gui_attributes")
        input_df.pop("hlist")
        input_df.rename(columns={"combined": "gui_attributes"}, inplace=True)
    return input_df


def _rename_lang_cols(input_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    # If the columns are named correctly return the df
    if set(language_label_col).issubset(set(input_df.columns)):
        return input_df
    if set(languages).issubset(set(input_df.columns)):
        warnings.warn(
            f"The file '{excel_filename}' uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )
    rename_dict = dict(zip(languages, language_label_col))
    input_df.rename(columns=rename_dict, inplace=True)
    return input_df


def _rename_deprecated_columnnames(in_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    in_df = _rename_lang_cols(input_df=in_df, excel_filename=excel_filename)
    in_df = _rename_hlist(input_df=in_df, excel_filename=excel_filename)
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
    df = read_excel_file(excel_filename=excelfile)

    df = _rename_deprecated_columnnames(in_df=df, excel_filename=excelfile)

    _do_property_excel_compliance(compliance_df=df, excel_filename=excelfile)

    # transform every row into a property
    props: list[dict[str, Any]] = []
    for index, row in df.iterrows():
        props.append(
            _row2prop(
                row=row,
                row_count=int(str(index)),  # index is a label/index/hashable, but we need an int
                excelfile=excelfile,
            )
        )

    # write final JSON file
    _validate_properties(properties_list=props, excelfile=excelfile)
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(props, file, indent=4, ensure_ascii=False)
            print('"properties" section was created successfully and written to file:', path_to_output_file)

    return props, True
