from __future__ import annotations

import importlib.resources
import json
import warnings
from typing import Any
from typing import Optional

import jsonpath_ng.ext
import jsonschema
import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import InvalidContentInSheetProblem
from dsp_tools.commands.excel2json.models.input_error import JsonValidationResourceProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.models.input_error import ResourcesSheetsNotAsExpected
from dsp_tools.commands.excel2json.utils import add_optional_columns
from dsp_tools.commands.excel2json.utils import check_column_for_duplicate
from dsp_tools.commands.excel2json.utils import check_contains_required_columns
from dsp_tools.commands.excel2json.utils import check_required_values
from dsp_tools.commands.excel2json.utils import get_wrong_row_numbers
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.models.exceptions import InputError

languages = ["en", "de", "fr", "it", "rm"]


def _validate_resources(resources_list: list[dict[str, Any]]) -> None:
    """
    This function checks if the "resources" section of a JSON project file is valid according to the JSON schema,
    and if the resource names are unique.

    Args:
        resources_list: the "resources" section of a JSON project as a list of dicts

    Raises:
        InputError: if the validation fails
    """
    with (
        importlib.resources.files("dsp_tools")
        .joinpath("resources/schema/resources-only.json")
        .open(encoding="utf-8") as schema_file
    ):
        resources_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=resources_list, schema=resources_schema)
    except jsonschema.ValidationError as err:
        validation_problem = _find_validation_problem(
            validation_error=err,
            resources_list=resources_list,
        )
        msg = "\nThe Excel file 'resources.xlsx' did not pass validation." + validation_problem.execute_error_protocol()
        raise InputError(msg) from None


def _find_validation_problem(
    validation_error: jsonschema.ValidationError, resources_list: list[dict[str, Any]]
) -> JsonValidationResourceProblem:
    if json_path_to_resource := regex.search(r"^\$\[(\d+)\]", validation_error.json_path):
        # fmt: off
        wrong_res_name = (
            jsonpath_ng.ext.parse(json_path_to_resource.group(0))
            .find(resources_list)[0]
            .value["name"]
        )
        # fmt: on
        if affected_field := regex.search(
            r"name|labels|comments|super|cardinalities\[(\d+)\]", validation_error.json_path
        ):
            affected_value = affected_field.group(0)
            problematic_resource, excel_sheet, excel_row, excel_column = "", None, None, None

            if affected_value in ["name", "labels", "comments", "super"]:
                excel_sheet = "classes"
                problematic_resource = wrong_res_name
                excel_row = int(json_path_to_resource.group(1)) + 2
                excel_column = affected_value

            elif "cardinalities" in affected_value:
                excel_row = int(affected_field.group(1)) + 2
                excel_sheet = wrong_res_name

                if validation_error.json_path.endswith("cardinality"):
                    excel_column = "Cardinality"

                elif validation_error.json_path.endswith("propname"):
                    excel_column = "Property"

            return JsonValidationResourceProblem(
                problematic_resource=problematic_resource,
                excel_position=PositionInExcel(sheet=excel_sheet, column=excel_column, row=excel_row),
                original_msg=validation_error.message,
            )
    return JsonValidationResourceProblem(
        original_msg=validation_error.message,
        message_path=validation_error.json_path,
    )


def _row2resource(
    class_info_row: pd.Series[Any],
    class_df_with_cardinalities: pd.DataFrame | None,
) -> dict[str, Any]:
    """
    Method that reads one row from the "classes" DataFrame,
    opens the corresponding details DataFrame,
    and builds a dict object of the resource.

    Args:
        class_info_row: row from the "classes" DataFrame
        class_df_with_cardinalities: Excel sheet of the individual class

    Raises:
        UserError: if the row or the details sheet contains invalid data

    Returns:
        dict object of the resource
    """

    class_name = class_info_row["name"]
    labels = {
        lang: class_info_row[f"label_{lang}"] for lang in languages if not pd.isna(class_info_row[f"label_{lang}"])
    }
    if not labels:
        labels = {lang: class_info_row[lang] for lang in languages if not pd.isna(class_info_row[lang])}
    supers = [s.strip() for s in class_info_row["super"].split(",")]

    resource = {"name": class_name, "super": supers, "labels": labels}

    comments = {
        lang: class_info_row[f"comment_{lang}"] for lang in languages if not pd.isna(class_info_row[f"comment_{lang}"])
    }
    if comments:
        resource["comments"] = comments

    cards = _make_cardinality_section(class_name, class_df_with_cardinalities)
    if cards:
        resource["cardinalities"] = cards

    return resource


def _make_cardinality_section(
    class_name: str, class_df_with_cardinalities: pd.DataFrame | None
) -> list[dict[str, str | int]]:
    if class_df_with_cardinalities is None:
        return []
    if len(class_df_with_cardinalities) == 0:
        return []
    cards = _create_all_cardinalities(class_name, class_df_with_cardinalities)
    return cards


def _create_all_cardinalities(class_name: str, class_df_with_cardinalities: pd.DataFrame) -> list[dict[str, str | int]]:
    class_df_with_cardinalities = _check_complete_gui_order(class_name, class_df_with_cardinalities)
    cards = [_make_one_property(detail_row) for _, detail_row in class_df_with_cardinalities.iterrows()]
    return cards


def _make_one_property(detail_row: pd.Series[str | int]) -> dict[str, str | int]:
    return {
        "propname": f':{detail_row["property"]}',
        "cardinality": str(detail_row["cardinality"]).lower(),
        "gui_order": detail_row["gui_order"],
    }


def _check_complete_gui_order(class_name: str, class_df_with_cardinalities: pd.DataFrame) -> pd.DataFrame:
    detail_problem_msg = ""
    attempt_conversion = False
    if "gui_order" not in class_df_with_cardinalities:
        pass
    elif class_df_with_cardinalities["gui_order"].isna().all():
        pass
    elif class_df_with_cardinalities["gui_order"].isna().any():
        detail_problem_msg = "some rows in the column 'gui_order' are empty."
    elif not class_df_with_cardinalities["gui_order"].isna().all():
        attempt_conversion = True

    if attempt_conversion:
        try:
            class_df_with_cardinalities["gui_order"] = [int(float(x)) for x in class_df_with_cardinalities["gui_order"]]
            return class_df_with_cardinalities
        except ValueError:
            detail_problem_msg = (
                "some rows in the column 'gui_order' contain invalid characters "
                "that could not be converted to an integer."
            )

    class_df_with_cardinalities["gui_order"] = list(range(1, len(class_df_with_cardinalities) + 1))

    if detail_problem_msg:
        complete_msg = (
            f"In the sheet '{class_name}' of the file 'resources.xlsx', "
            f"{detail_problem_msg}\n"
            f"Values have been filled in automatically, "
            f"so that the gui-order reflects the order of the properties in the file."
        )
        warnings.warn(complete_msg)
    return class_df_with_cardinalities


def excel2resources(
    excelfile: str,
    path_to_output_file: Optional[str] = None,
) -> tuple[list[dict[str, Any]], bool]:
    """
    Converts resources described in an Excel file into a "resources" section which can be inserted into a JSON
    project file.

    Args:
        excelfile: path to the Excel file containing the resources
        path_to_output_file: if provided, the output is written into this JSON file
            (otherwise, it's only returned as return value)

    Raises:
        UserError: if something went wrong
        InputError: is something went wrong

    Returns:
        a tuple consisting of the "resources" section as Python list,
            and the success status (True if everything went well)
    """

    all_dfs = read_and_clean_all_sheets(excelfile)
    classes_df, resource_dfs = _prepare_classes_df(all_dfs)

    if validation_problems := _validate_excel_file(classes_df, resource_dfs):
        msg = validation_problems.execute_error_protocol()
        raise InputError(msg)

    # transform every row into a resource
    resources = [_row2resource(row, resource_dfs.get(row["name"])) for i, row in classes_df.iterrows()]

    # write final "resources" section into a JSON file
    _validate_resources(resources_list=resources)

    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(resources, file, indent=4, ensure_ascii=False)
            print(f"resources section was created successfully and written to file '{path_to_output_file}'")

    return resources, True


def _prepare_classes_df(resource_dfs: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    resource_dfs = {k.strip(): v for k, v in resource_dfs.items()}
    sheet_name_list = list(resource_dfs)
    cls_sheet_name = [
        ok.group(0) for x in sheet_name_list if (ok := regex.search(r"classes", flags=regex.IGNORECASE, string=x))
    ]
    if not cls_sheet_name:
        msg = ResourcesSheetsNotAsExpected(set(), names_sheets={"classes"}).execute_error_protocol()
        raise InputError(msg)
    elif len(cls_sheet_name) == 1:
        classes_df = resource_dfs.pop(cls_sheet_name[0])
    else:
        msg = (
            "The excel file 'resources.xlsx' has some problems.\n"
            "There is more than one excel sheet called 'classes'.\n"
            "This is a protected name and cannot be used for other sheets."
        )
        raise InputError(msg)
    classes_df = add_optional_columns(
        classes_df,
        {
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
    resource_dfs = {k: add_optional_columns(v, {"gui_order"}) for k, v in resource_dfs.items()}
    return classes_df, resource_dfs


def _validate_excel_file(classes_df: pd.DataFrame, df_dict: dict[str, pd.DataFrame]) -> ExcelFileProblem | None:
    problems = _validate_classes_excel_sheet(classes_df)
    if sheet_problems := _validate_individual_class_sheets(df_dict):
        problems.extend(sheet_problems)
    if problems:
        return ExcelFileProblem("resources.xlsx", problems)
    return None


def _validate_classes_excel_sheet(classes_df: pd.DataFrame) -> list[Problem]:
    if any(classes_df.get(lang) is not None for lang in languages):
        warnings.warn(
            f"The file 'resources.xlsx' uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )
    problems: list[Problem] = []
    required_cols = ["name", "super"]
    if missing_cols := check_contains_required_columns(classes_df, set(required_cols)):
        return [InvalidContentInSheetProblem("classes", [missing_cols])]
    if missing_values := check_required_values(classes_df, required_cols):
        row_nums = get_wrong_row_numbers(missing_values)
        for col, nums in row_nums.items():
            problems.extend([PositionInExcel("classes", col, x) for x in nums])
    if duplicate_check := check_column_for_duplicate(classes_df, "name"):
        problems.append(duplicate_check)
    return problems


def _validate_individual_class_sheets(class_df_dict: dict[str, pd.DataFrame]) -> list[Problem]:
    required_cols = ["property", "cardinality"]
    missing_required_columns = {
        sheet: missing_cols
        for sheet, df in class_df_dict.items()
        if (missing_cols := check_contains_required_columns(df, set(required_cols)))
    }
    if missing_required_columns:
        return [InvalidContentInSheetProblem(sheet, [missing]) for sheet, missing in missing_required_columns.items()]
    problem_list: list[PositionInExcel] = []
    for sheet_name, df in class_df_dict.items():
        if missing_dict := check_required_values(df, required_cols):
            row_nums = get_wrong_row_numbers(missing_dict)
            for col, nums in row_nums.items():
                problem_list.extend([PositionInExcel(sheet_name, col, x) for x in nums])
    if problem_list:
        return [MissingValuesProblem(problem_list)]
    return []
