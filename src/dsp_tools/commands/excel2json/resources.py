import importlib.resources
import json
import warnings
from typing import Any, Optional

import jsonpath_ng.ext
import jsonschema
import pandas as pd
import regex

from dsp_tools.commands.excel2json.input_error import (
    JsonValidationResourceProblem,
    PositionInExcel,
    ResourcesSheetsNotAsExpected,
)
from dsp_tools.commands.excel2json.utils import check_column_for_duplicate, read_and_clean_all_sheets
from dsp_tools.models.exceptions import InputError, UserError
from dsp_tools.utils.shared import check_notna, prepare_dataframe

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
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/resources-only.json").open(
        encoding="utf-8"
    ) as schema_file:
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
    df_row: pd.Series,
    details_df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Method that reads one row from the "classes" DataFrame,
    opens the corresponding details DataFrame,
    and builds a dict object of the resource.

    Args:
        df_row: row from the "classes" DataFrame
        details_df: Excel sheet of the individual class

    Raises:
        UserError: if the row or the details sheet contains invalid data

    Returns:
        dict object of the resource
    """

    name = df_row["name"]
    labels = {lang: df_row[f"label_{lang}"] for lang in languages if df_row.get(f"label_{lang}")}
    if not labels:
        labels = {lang: df_row[lang] for lang in languages if df_row.get(lang)}
    comments = {lang: df_row[f"comment_{lang}"] for lang in languages if df_row.get(f"comment_{lang}")}
    supers = [s.strip() for s in df_row["super"].split(",")]

    details_df = prepare_dataframe(
        df=details_df,
        required_columns=["Property", "Cardinality"],
        location_of_sheet=f"Sheet '{name}' in file 'resources.xlsx'",
    )

    # validation
    # 4 cases:
    #  - column gui_order absent
    #  - column gui_order empty
    #  - column gui_order present but not properly filled in (missing values / not integers)
    #  - column gui_order present and properly filled in
    all_gui_order_cells = []
    if "gui_order" in details_df:
        all_gui_order_cells = [x for x in details_df["gui_order"] if x]
    validation_passed = True
    if not all_gui_order_cells:  # column gui_order absent or empty
        pass
    elif len(all_gui_order_cells) == len(details_df["property"]):  # column gui_order filled in. try casting to int
        try:
            [int(float(x)) for x in details_df["gui_order"]]
        except ValueError:
            validation_passed = False
    else:  # column gui_order present but not properly filled in (missing values)
        validation_passed = False
    if not validation_passed:
        raise UserError(
            f"Sheet '{name}' in file 'resources.xlsx' has invalid content in column 'gui_order': "
            f"only positive integers allowed (or leave column empty altogether)"
        )

    cards = []
    for j, detail_row in details_df.iterrows():
        j = int(str(j))  # j is a label/index/hashable, but we need an int
        gui_order = detail_row.get("gui_order", "")
        gui_order = regex.sub(r"\.0+", "", str(gui_order))
        property_ = {
            "propname": ":" + detail_row["property"],
            "cardinality": detail_row["cardinality"].lower(),
            "gui_order": int(gui_order or j + 1),  # if gui_order not given: take sheet order
        }
        cards.append(property_)

    # build the dict structure of this resource and append it to the list of resources
    resource = {"name": name, "super": supers, "labels": labels}
    if comments:
        resource["comments"] = comments
    resource["cardinalities"] = cards

    return resource


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

    resource_dfs = read_and_clean_all_sheets(excelfile)
    classes_df = resource_dfs.pop("classes")
    classes_df = prepare_dataframe(
        df=classes_df,
        required_columns=["name"],
        location_of_sheet=f"Sheet 'classes' in file '{excelfile}'",
    )

    if validation_problem := _validate_excel_file(classes_df, resource_dfs):
        err_msg = validation_problem.execute_error_protocol()
        raise InputError(err_msg)

    # transform every row into a resource
    resources = [_row2resource(row, resource_dfs[row["name"]]) for i, row in classes_df.iterrows()]

    # write final "resources" section into a JSON file
    _validate_resources(resources_list=resources)

    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(resources, file, indent=4, ensure_ascii=False)
            print(f"resources section was created successfully and written to file '{path_to_output_file}'")

    return resources, True


def _validate_excel_file(
    classes_df: pd.DataFrame, df_dict: dict[str, pd.DataFrame]
) -> ResourcesSheetsNotAsExpected | None:
    for index, row in classes_df.iterrows():
        index = int(str(index))  # index is a label/index/hashable, but we need an int
        if not check_notna(row["super"]):
            raise UserError(
                f"Sheet 'classes' of 'resources.xlsx' has a missing value in row {index + 2}, column 'super'"
            )
    if any(classes_df.get(lang) is not None for lang in languages):
        warnings.warn(
            f"The file 'resources.xlsx' uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )
    duplicate_check = check_column_for_duplicate(classes_df, "name")
    if duplicate_check:
        msg = "The excel file 'resources.xlsx', sheet 'classes' has a problem.\n"
        msg += duplicate_check.execute_error_protocol()
        raise InputError(msg)
    # check that all the sheets have an entry in the names column and vice versa
    if (all_names := set(classes_df["name"].tolist())) != (all_sheets := set(df_dict.keys())):
        return ResourcesSheetsNotAsExpected(all_names, all_sheets)
    return None
