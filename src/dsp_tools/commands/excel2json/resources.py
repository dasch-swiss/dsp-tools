import importlib.resources
import json
import warnings
from typing import Any, Optional

import jsonpath_ng.ext
import jsonschema
import pandas as pd
import regex

import dsp_tools.commands.excel2json.utils as utl
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.shared import check_notna, prepare_dataframe

languages = ["en", "de", "fr", "it", "rm"]


def _validate_resources(
    resources_list: list[dict[str, Any]],
    excelfile: str,
) -> bool:
    """
    This function checks if the "resources" section of a JSON project file is valid according to the JSON schema,
    and if the resource names are unique.

    Args:
        resources_list: the "resources" section of a JSON project as a list of dicts
        excelfile: path to the Excel file containing the resources

    Raises:
        UserError: if the validation fails

    Returns:
        True if the "resources" section passed validation
    """
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/resources-only.json").open(
        encoding="utf-8"
    ) as schema_file:
        resources_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=resources_list, schema=resources_schema)
    except jsonschema.ValidationError as err:
        err_msg = f"The 'resources' section defined in the Excel file '{excelfile}' did not pass validation. "
        if json_path_to_resource := regex.search(r"^\$\[(\d+)\]", err.json_path):
            # fmt: off
            wrong_res_name = (
                jsonpath_ng.ext.parse(json_path_to_resource.group(0))
                .find(resources_list)[0]
                .value["name"]
            )
            # fmt: on
            if affected_field := regex.search(r"name|labels|comments|super|cardinalities\[(\d+)\]", err.json_path):
                if affected_field.group(0) in ["name", "labels", "comments", "super"]:
                    excel_row = int(json_path_to_resource.group(1)) + 2
                    err_msg += (
                        f"The problem is that the Excel sheet 'classes' contains an invalid value for resource "
                        f"'{wrong_res_name}', in row {excel_row}, column '{affected_field.group(0)}': {err.message}"
                    )
                elif "cardinalities" in affected_field.group(0):
                    excel_row = int(affected_field.group(1)) + 2
                    if err.json_path.endswith("cardinality"):
                        err_msg += (
                            f"The problem is that the Excel sheet '{wrong_res_name}' contains an invalid value "
                            f"in row {excel_row}, column 'Cardinality': {err.message}"
                        )
                    elif err.json_path.endswith("propname"):
                        err_msg += (
                            f"The problem is that the Excel sheet '{wrong_res_name}' contains an invalid value "
                            f"in row {excel_row}, column 'Property': {err.message}"
                        )
        else:
            err_msg += f"The error message is: {err.message}\nThe error occurred at {err.json_path}"
        raise UserError(err_msg) from None

    # check if resource names are unique
    all_names = [r["name"] for r in resources_list]
    if duplicates := {
        index + 2: resdef["name"] for index, resdef in enumerate(resources_list) if all_names.count(resdef["name"]) > 1
    }:
        err_msg = (
            f"Resource names must be unique inside every ontology, "
            f"but your Excel file '{excelfile}' contains duplicates:\n"
        )
        for row_no, resname in duplicates.items():
            err_msg += f" - Row {row_no}: {resname}\n"
        raise UserError(err_msg)

    return True


def _row2resource(
    df_row: pd.Series,
    excelfile: str,
) -> dict[str, Any]:
    """
    Method that reads one row from the "classes" DataFrame,
    opens the corresponding details DataFrame,
    and builds a dict object of the resource.

    Args:
        df_row: row from the "classes" DataFrame
        excelfile: Excel file where the data comes from

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

    # load the cardinalities of this resource
    # if the excel sheet does not exist, pandas raises a ValueError
    try:
        details_df = utl.read_and_clean_excel_file(excelfile=excelfile, sheetname=name)
    except ValueError as err:
        raise UserError(str(err)) from None
    details_df = prepare_dataframe(
        df=details_df,
        required_columns=["Property", "Cardinality"],
        location_of_sheet=f"Sheet '{name}' in file '{excelfile}'",
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
            f"Sheet '{name}' in file '{excelfile}' has invalid content in column 'gui_order': "
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

    Returns:
        a tuple consisting of the "resources" section as Python list,
            and the success status (True if everything went well)
    """

    # load file
    all_classes_df = utl.read_and_clean_excel_file(excelfile=excelfile)
    all_classes_df = prepare_dataframe(
        df=all_classes_df,
        required_columns=["name"],
        location_of_sheet=f"Sheet 'classes' in file '{excelfile}'",
    )

    # validation
    for index, row in all_classes_df.iterrows():
        index = int(str(index))  # index is a label/index/hashable, but we need an int
        if not check_notna(row["super"]):
            raise UserError(f"Sheet 'classes' of '{excelfile}' has a missing value in row {index + 2}, column 'super'")
    if any(all_classes_df.get(lang) is not None for lang in languages):
        warnings.warn(
            f"The file {excelfile} uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )

    # transform every row into a resource
    resources = [_row2resource(row, excelfile) for i, row in all_classes_df.iterrows()]

    # write final "resources" section into a JSON file
    _validate_resources(resources_list=resources, excelfile=excelfile)
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(resources, file, indent=4, ensure_ascii=False)
            print(f"resources section was created successfully and written to file '{path_to_output_file}'")

    return resources, True
