from __future__ import annotations

import importlib.resources
import json
import warnings
from typing import Any
from typing import Optional
from typing import cast

import jsonpath_ng.ext
import jsonschema
import numpy as np
import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import InvalidExcelContentProblem
from dsp_tools.commands.excel2json.models.input_error import JsonValidationPropertyProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import MoreThanOneSheetProblem
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import PropertyProblem
from dsp_tools.commands.excel2json.models.json_header import PermissionsOverrulesUnprefixed
from dsp_tools.commands.excel2json.models.ontology import GuiAttributes
from dsp_tools.commands.excel2json.models.ontology import OntoProperty
from dsp_tools.commands.excel2json.utils import add_optional_columns
from dsp_tools.commands.excel2json.utils import check_column_for_duplicate
from dsp_tools.commands.excel2json.utils import check_contains_required_columns
from dsp_tools.commands.excel2json.utils import check_permissions
from dsp_tools.commands.excel2json.utils import check_required_values
from dsp_tools.commands.excel2json.utils import col_must_or_not_empty_based_on_other_col
from dsp_tools.commands.excel2json.utils import find_one_full_cell_in_cols
from dsp_tools.commands.excel2json.utils import get_comments
from dsp_tools.commands.excel2json.utils import get_labels
from dsp_tools.commands.excel2json.utils import get_wrong_row_numbers
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.error.exceptions import InputError
from dsp_tools.error.problems import Problem

languages = ["en", "de", "fr", "it", "rm"]
language_label_col = ["label_en", "label_de", "label_fr", "label_it", "label_rm"]


def excel2properties(
    excelfile: str,
    path_to_output_file: Optional[str] = None,
) -> tuple[list[dict[str, Any]], PermissionsOverrulesUnprefixed, bool]:
    """
    Converts properties described in an Excel file into a "properties" section which can be inserted into a JSON
    project file.

    Args:
        excelfile: path to the Excel file containing the properties
        path_to_output_file: if provided, the output is written into this JSON file

    Raises:
        InputError: if something went wrong

    Returns:
        - the "properties" section as a Python list
        - the unprefixed "default_permissions_overrule"
        - the success status (True if everything went well)
    """

    property_df = _read_check_property_df(excelfile)

    property_df = _rename_deprecated_columnnames(df=property_df)

    # Not all columns have to be filled, users may delete some for ease of use, but it would generate an error later
    optional_col_set = {
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
        "subject",
        "default_permissions_overrule",
    }
    property_df = add_optional_columns(property_df, optional_col_set)

    _do_property_excel_compliance(df=property_df)

    _check_for_deprecated_syntax(property_df)

    # transform every row into a property
    props: list[OntoProperty] = []
    problems: list[Problem] = []
    for index, row in property_df.iterrows():
        result = _row2prop(
            df_row=row,
            row_num=int(str(index)) + 2,  # index is a label/index/hashable, but we need an int
        )
        if isinstance(result, PropertyProblem):
            problems.append(result)
        else:
            props.append(result)
    if problems:
        msg = ExcelFileProblem("properties.xlsx", problems).execute_error_protocol()
        raise InputError(msg)

    serialised_prop = [x.serialise() for x in props]
    default_permissions_overrule = _extract_default_permissions_overrule(property_df)

    # write final JSON file
    _validate_properties_section_in_json(properties_list=serialised_prop)
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(serialised_prop, file, indent=4, ensure_ascii=False)
            print(f"properties section was created successfully and written to file '{path_to_output_file}'")

    return serialised_prop, default_permissions_overrule, True


def _check_for_deprecated_syntax(df: pd.DataFrame) -> None:
    pass


def _read_check_property_df(excelfile: str) -> pd.DataFrame:
    sheets_df_dict = read_and_clean_all_sheets(excelfile)
    if len(sheets_df_dict) != 1:
        msg = MoreThanOneSheetProblem("properties.xlsx", list(sheets_df_dict.keys())).execute_error_protocol()
        raise InputError(msg)
    return next(iter(sheets_df_dict.values()))


def _rename_deprecated_columnnames(df: pd.DataFrame) -> pd.DataFrame:
    df = _rename_deprecated_lang_cols(df=df)
    df = _rename_deprecated_hlist(df=df)
    return df


def _rename_deprecated_lang_cols(df: pd.DataFrame) -> pd.DataFrame:
    if set(language_label_col).issubset(set(df.columns)):
        return df
    if set(languages).issubset(set(df.columns)):
        warnings.warn(
            f"The file 'properties.xlsx' uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )
    rename_dict = dict(zip(languages, language_label_col))
    df = df.rename(columns=rename_dict)
    return df


def _rename_deprecated_hlist(df: pd.DataFrame) -> pd.DataFrame:
    # This function deals with Excel files that do conform to a previous format.
    if "hlist" not in df.columns:
        return df
    warnings.warn(
        "The file 'properties.xlsx' has a column 'hlist', which is deprecated. "
        "Please use the column 'gui_attributes' for the attribute 'hlist'."
    )
    df["hlist"] = df["hlist"].apply(lambda x: f"hlist:{x}" if isinstance(x, str) else x)
    # If gui_attributes already exists we have to merge the columns
    if "gui_attributes" in df.columns:
        # In case there is a hlist, it is the only valid value in gui_attributes and has precedence
        df["hlist"] = df["hlist"].fillna(df["gui_attributes"])
        df.pop("gui_attributes")
    df = df.rename(columns={"hlist": "gui_attributes"})
    return df


def _do_property_excel_compliance(df: pd.DataFrame) -> None:
    required_columns = {
        "name",
        "super",
        "object",
        "gui_element",
        "gui_attributes",
    }
    problems: list[Problem] = []
    if req_prob := check_contains_required_columns(df=df, required_columns=required_columns):
        problems.append(req_prob)
    if col_prob := check_column_for_duplicate(df=df, to_check_column="name"):
        problems.append(col_prob)
    if missing_vals_check := _check_missing_values_in_row(df=df):
        problems.append(missing_vals_check)
    if permissions_prob := check_permissions(df=df, allowed_vals=["private"]):
        problems.append(permissions_prob)
    if any(problems):
        excel_prob = ExcelFileProblem("properties.xlsx", problems)
        msg = excel_prob.execute_error_protocol()
        raise InputError(msg)


def _check_missing_values_in_row(df: pd.DataFrame) -> None | MissingValuesProblem:
    required_values = ["name", "super", "object", "gui_element"]
    missing_dict = check_required_values(df=df, required_values_columns=required_values)
    missing_labels = find_one_full_cell_in_cols(df=df, required_columns=language_label_col)
    if missing_labels is not None:
        missing_dict.update({"label": missing_labels})
    missing_gui_attributes = _check_compliance_gui_attributes(df=df)
    if missing_gui_attributes is not None:
        missing_dict.update(missing_gui_attributes)
    if missing_dict:
        missing_int_dict = get_wrong_row_numbers(wrong_row_dict=missing_dict, true_remains=True)
        locs = []
        for col, row_nums in missing_int_dict.items():
            locs.extend([PositionInExcel(column=col, row=x) for x in row_nums])
        return MissingValuesProblem(locs)
    else:
        return None


def _check_compliance_gui_attributes(df: pd.DataFrame) -> dict[str, pd.Series[bool]] | None:
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
    final_series = _get_final_series(mandatory_check, no_attribute_check)
    return {"gui_attributes": final_series} if final_series is not None else None


def _get_final_series(
    mandatory_check: pd.Series[bool] | None, no_attribute_check: pd.Series[bool] | None
) -> pd.Series[bool] | None:
    final_series: pd.Series[bool] = pd.Series()
    match mandatory_check, no_attribute_check:
        case None, None:
            return None
        case pd.Series(), pd.Series():
            final_series = pd.Series(np.logical_or(mandatory_check, no_attribute_check))
        case pd.Series(), None:
            final_series = mandatory_check
        case None, pd.Series():
            final_series = no_attribute_check
    return final_series


def _row2prop(df_row: pd.Series[Any], row_num: int) -> OntoProperty | PropertyProblem:
    subj = df_row["subject"] if not pd.isna(df_row["subject"]) else None
    comment = get_comments(df_row=df_row)
    gui_attrib = _get_gui_attribute(df_row=df_row, row_num=row_num)
    if isinstance(gui_attrib, InvalidExcelContentProblem):
        return PropertyProblem(df_row["name"], cast(list[Problem], [gui_attrib]))
    prop = OntoProperty(
        name=df_row["name"],
        super=[s.strip() for s in df_row["super"].split(",")],
        object=df_row["object"],
        subject=subj,
        labels=get_labels(df_row=df_row),
        comments=comment,
        gui_element=df_row["gui_element"],
        gui_attributes=gui_attrib,
    )
    return prop


def _get_gui_attribute(
    df_row: pd.Series[Any],
    row_num: int,
) -> GuiAttributes | InvalidExcelContentProblem | None:
    if pd.isnull(df_row["gui_attributes"]):
        return None
    # If the attribute is not in the correct format, a called function may raise an InputError
    try:
        return _format_gui_attribute(attribute_str=df_row["gui_attributes"])
    except InputError:
        return InvalidExcelContentProblem(
            expected_content="attribute1: value, attribute2: value (no attribute key may be duplicated)",
            actual_content=df_row["gui_attributes"],
            excel_position=PositionInExcel(column="gui_attributes", row=row_num),
        )


def _format_gui_attribute(attribute_str: str) -> GuiAttributes:
    attribute_dict = _unpack_gui_attributes(attribute_str=attribute_str)
    return GuiAttributes(
        {attrib: _search_convert_numbers_in_str(value_str=val) for attrib, val in attribute_dict.items()}
    )


def _unpack_gui_attributes(attribute_str: str) -> dict[str, str]:
    gui_list = [x.strip() for x in attribute_str.split(",") if x.strip() != ""]
    gui_attrib = {}
    for attrib in gui_list:
        attrib_key, attrib_val = _extract_information_from_single_gui_attribute(attrib)
        if attrib_key in gui_attrib:
            raise InputError("Duplicate gui attribute")
        gui_attrib[attrib_key] = attrib_val
    return gui_attrib


def _extract_information_from_single_gui_attribute(attribute_str: str) -> tuple[str, str]:
    attrib_format = r"(\S+)\s*:\s*(.+)"
    if found := regex.search(attrib_format, attribute_str):
        return found.group(1), found.group(2)
    raise InputError("Invalid gui attribute")


def _search_convert_numbers_in_str(value_str: str) -> str | int | float:
    if regex.search(r"^\d+$", value_str):
        return int(value_str)
    elif regex.search(r"^\d+\.\d+$", value_str):
        return float(value_str)
    else:
        return value_str


def _validate_properties_section_in_json(
    properties_list: list[dict[str, Any]],
) -> None:
    with (
        importlib.resources.files("dsp_tools")
        .joinpath("resources/schema/properties-only.json")
        .open(encoding="utf-8") as schema_file
    ):
        properties_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=properties_list, schema=properties_schema)
    except jsonschema.ValidationError as err:
        validation_problem = _find_validation_problem(properties_list=properties_list, validation_error=err)
        msg = ExcelFileProblem("properties.xlsx", [validation_problem]).execute_error_protocol()
        raise InputError(msg) from None


def _find_validation_problem(
    properties_list: list[dict[str, Any]],
    validation_error: jsonschema.ValidationError,
) -> JsonValidationPropertyProblem:
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


def _extract_default_permissions_overrule(property_df: pd.DataFrame) -> PermissionsOverrulesUnprefixed:
    result = PermissionsOverrulesUnprefixed(private=[], limited_view=[])
    for _, row in property_df.iterrows():
        perm = row.get("default_permissions_overrule")
        if pd.isna(perm):
            continue
        if perm.strip().lower() == "private":
            result.private.append(row["name"])
    return result
