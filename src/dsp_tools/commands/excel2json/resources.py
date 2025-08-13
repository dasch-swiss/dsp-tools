from __future__ import annotations

import importlib.resources
import json
import warnings
from copy import deepcopy
from typing import Any
from typing import Optional

import jsonpath_ng.ext
import jsonschema
import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import JsonValidationResourceProblem
from dsp_tools.commands.excel2json.models.input_error import MandatorySheetsMissingProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import ResourceSheetNotListedProblem
from dsp_tools.commands.excel2json.models.json_header import PermissionsOverrulesUnprefixed
from dsp_tools.commands.excel2json.models.ontology import OntoResource
from dsp_tools.commands.excel2json.models.ontology import ResourceCardinality
from dsp_tools.commands.excel2json.utils import add_optional_columns
from dsp_tools.commands.excel2json.utils import check_column_for_duplicate
from dsp_tools.commands.excel2json.utils import check_contains_required_columns
from dsp_tools.commands.excel2json.utils import check_permissions
from dsp_tools.commands.excel2json.utils import find_missing_required_values
from dsp_tools.commands.excel2json.utils import get_comments
from dsp_tools.commands.excel2json.utils import get_labels
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.error.exceptions import InputError
from dsp_tools.error.problems import Problem

languages = ["en", "de", "fr", "it", "rm"]


def excel2resources(
    excelfile: str,
    path_to_output_file: Optional[str] = None,
) -> tuple[list[dict[str, Any]], PermissionsOverrulesUnprefixed, bool]:
    """
    Converts resources described in an Excel file into a "resources" section which can be inserted into a JSON
    project file.

    Args:
        excelfile: path to the Excel file containing the resources
        path_to_output_file: if provided, the output is written into this JSON file
            (otherwise, it's only returned as return value)

    Raises:
        InputError: if something went wrong

    Returns:
        - the "resources" section as Python list,
        - the unprefixed "default_permissions_overrule",
        - the success status (True if everything went well)
    """

    all_dfs = read_and_clean_all_sheets(excelfile)

    if validation_problems := _validate_excel_file(all_dfs):
        msg = validation_problems.execute_error_protocol()
        raise InputError(msg)
    classes_df, resource_dfs = _prepare_classes_df(all_dfs)

    # transform every row into a resource
    res = [_row2resource(row, resource_dfs.get(row["name"])) for i, row in classes_df.iterrows()]
    resources = [x.serialise() for x in res]
    default_permissions_overrule = _extract_default_permissions_overrule(classes_df)

    # write final "resources" section into a JSON file
    _validate_resources(resources_list=resources)

    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(resources, file, indent=4, ensure_ascii=False)
            print(f"resources section was created successfully and written to file '{path_to_output_file}'")

    return resources, default_permissions_overrule, True


def _validate_excel_file(all_dfs: dict[str, pd.DataFrame]) -> ExcelFileProblem | None:
    df_dict = deepcopy(all_dfs)
    lower_case_to_original = {k.lower(): k for k in df_dict}
    if not (cls_name := lower_case_to_original.get("classes")):
        return ExcelFileProblem(
            "resources.xlsx", [MandatorySheetsMissingProblem(["classes"], list(lower_case_to_original.values()))]
        )
    classes_df = df_dict.pop(cls_name)
    problems: list[Problem] = []
    if cls_problem := _validate_classes_excel_sheet(classes_df, set(df_dict)):
        problems.append(cls_problem)
    if sheet_problems := _validate_individual_class_sheets(df_dict):
        problems.extend(sheet_problems)
    if permissions_prob := check_permissions(df=classes_df, allowed_vals=["private", "limited_view"]):
        problems.append(permissions_prob)
    if problems:
        return ExcelFileProblem("resources.xlsx", problems)
    return None


def _validate_classes_excel_sheet(classes_df: pd.DataFrame, sheet_names: set[str]) -> ExcelSheetProblem | None:
    if any(classes_df.get(lang) is not None for lang in languages):
        warnings.warn(
            f"The file 'resources.xlsx' uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )
    problems: list[Problem] = []
    required_cols = ["name", "super"]
    if missing_cols := check_contains_required_columns(classes_df, set(required_cols)):
        # If this condition is not fulfilled the following tests will produce KeyErrors
        return ExcelSheetProblem("classes", [missing_cols])
    names_listed = set(classes_df["name"].tolist())
    if not sheet_names.issubset(names_listed):
        problems.append(ResourceSheetNotListedProblem(sheet_names - names_listed))
    if missing_values := find_missing_required_values(classes_df, required_cols):
        problems.extend(missing_values)
    if duplicate_check := check_column_for_duplicate(classes_df, "name"):
        problems.append(duplicate_check)
    if problems:
        return ExcelSheetProblem("classes", problems)
    return None


def _validate_individual_class_sheets(class_df_dict: dict[str, pd.DataFrame]) -> list[Problem]:
    required_cols = ["property", "cardinality"]
    missing_required_columns = {
        sheet: missing_cols
        for sheet, df in class_df_dict.items()
        if (missing_cols := check_contains_required_columns(df, set(required_cols)))
    }
    if missing_required_columns:
        return [ExcelSheetProblem(sheet, [missing]) for sheet, missing in missing_required_columns.items()]
    missing_values_position: list[PositionInExcel] = []
    for sheet_name, df in class_df_dict.items():
        if missing_vals_position := find_missing_required_values(df, required_cols, sheet_name):
            missing_values_position.extend(missing_vals_position)
    if missing_values_position:
        return [MissingValuesProblem(missing_values_position)]
    return []


def _prepare_classes_df(resource_dfs: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    lower_case_to_original = {k.lower(): k for k in resource_dfs}
    classes_df = resource_dfs.pop(lower_case_to_original["classes"])
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
            "default_permissions_overrule",
        },
    )
    resource_dfs = {k: add_optional_columns(v, {"gui_order"}) for k, v in resource_dfs.items()}
    return classes_df, resource_dfs


def _row2resource(
    class_info_row: pd.Series[Any],
    class_df_with_cardinalities: pd.DataFrame | None,
) -> OntoResource:
    """
    Method that reads one row from the "classes" DataFrame,
    opens the corresponding details DataFrame,
    and builds a dict object of the resource.

    Args:
        class_info_row: row from the "classes" DataFrame
        class_df_with_cardinalities: Excel sheet of the individual class

    Raises:
        InputError: if the row or the details sheet contains invalid data

    Returns:
        dict object of the resource
    """

    class_name = class_info_row["name"]
    labels = get_labels(class_info_row)
    supers = [s.strip() for s in class_info_row["super"].split(",")]
    comments = get_comments(class_info_row)
    cards = _make_cardinality_section(class_name, class_df_with_cardinalities)
    return OntoResource(name=class_name, super=supers, labels=labels, comments=comments, cardinalities=cards)


def _make_cardinality_section(
    class_name: str, class_df_with_cardinalities: pd.DataFrame | None
) -> list[ResourceCardinality] | None:
    if class_df_with_cardinalities is None:
        return None
    if len(class_df_with_cardinalities) == 0:
        return None
    return _create_all_cardinalities(class_name, class_df_with_cardinalities)


def _create_all_cardinalities(class_name: str, class_df_with_cardinalities: pd.DataFrame) -> list[ResourceCardinality]:
    class_df_with_cardinalities = _check_complete_gui_order(class_name, class_df_with_cardinalities)
    cards = [_make_one_cardinality(detail_row) for _, detail_row in class_df_with_cardinalities.iterrows()]
    return cards


def _make_one_cardinality(detail_row: pd.Series[str | int]) -> ResourceCardinality:
    return ResourceCardinality(
        f":{detail_row['property']}", str(detail_row["cardinality"]).lower(), int(detail_row["gui_order"])
    )


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


def _extract_default_permissions_overrule(classes_df: pd.DataFrame) -> PermissionsOverrulesUnprefixed:
    result = PermissionsOverrulesUnprefixed(private=[], limited_view=[])
    for _, row in classes_df.iterrows():
        perm = row.get("default_permissions_overrule")
        if pd.isna(perm):
            continue
        if perm.strip().lower() == "private":
            result.private.append(row["name"])
        elif perm.strip().lower() == "limited_view":
            result.limited_view.append(row["name"])
    return result
