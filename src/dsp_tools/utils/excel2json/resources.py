import importlib.resources
import json
import warnings
from typing import Any, Optional

import jsonpath_ng.ext
import jsonschema
import pandas as pd
import regex

import dsp_tools.utils.excel2json.utils as utl
from dsp_tools.models.exceptions import UserError

languages = ["en", "de", "fr", "it", "rm"]
language_label_col = ["label_en", "label_de", "label_fr", "label_it", "label_rm"]


def _validate_resources(
    resources_list: list[dict[str, Any]],
    excelfile: str,
) -> bool:
    # TODO: revamp
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
        json_path_to_resource = regex.search(r"^\$\[(\d+)\]", err.json_path)
        if json_path_to_resource:
            # fmt: off
            wrong_resource_name = (
                jsonpath_ng.ext.parse(json_path_to_resource.group(0))
                .find(resources_list)[0]
                .value["name"]
            )
            # fmt: on
            affected_field = regex.search(r"name|labels|comments|super|cardinalities\[(\d+)\]", err.json_path)
            if affected_field and affected_field.group(0) in ["name", "labels", "comments", "super"]:
                excel_row = int(json_path_to_resource.group(1)) + 2
                err_msg += (
                    f"The problem is that the Excel sheet 'classes' contains an invalid value for resource "
                    f"'{wrong_resource_name}', in row {excel_row}, column '{affected_field.group(0)}': {err.message}"
                )
            elif affected_field and "cardinalities" in affected_field.group(0):
                excel_row = int(affected_field.group(1)) + 2
                if err.json_path.endswith("cardinality"):
                    err_msg += (
                        f"The problem is that the Excel sheet '{wrong_resource_name}' contains an invalid value "
                        f"in row {excel_row}, column 'Cardinality': {err.message}"
                    )
                elif err.json_path.endswith("propname"):
                    err_msg += (
                        f"The problem is that the Excel sheet '{wrong_resource_name}' contains an invalid value "
                        f"in row {excel_row}, column 'Property': {err.message}"
                    )
        else:
            err_msg += f"The error message is: {err.message}\nThe error occurred at {err.json_path}"
        raise UserError(err_msg) from None

    # check if resource names are unique
    all_names = [r["name"] for r in resources_list]
    duplicates: dict[int, str] = dict()
    for index, resdef in enumerate(resources_list):
        if all_names.count(resdef["name"]) > 1:
            duplicates[index + 2] = resdef["name"]
    if duplicates:
        err_msg = (
            f"Resource names must be unique inside every ontology, "
            f"but your Excel file '{excelfile}' contains duplicates:\n"
        )
        for row_no, resname in duplicates.items():
            err_msg += f" - Row {row_no}: {resname}\n"
        raise UserError(err_msg)

    return True


def _check_fill_gui_order(resource_df: pd.DataFrame, excel_sheet: str, excelfile: str) -> pd.DataFrame:
    pass


def _row2resource(df_row: pd.Series, excelfile: str, entire_df: str) -> dict[str, Any]:
    """
    Method that reads one row from the "classes" DataFrame,
    opens the corresponding details DataFrame,
    and builds a dict object of the resource.

    Args:
        df_row: row from the "classes" DataFrame
        excelfile: Excel file where the data comes from
        entire_df: pd.DataFrame that contains the property information

    Raises:
        UserError: if the row or the details sheet contains invalid data

    Returns:
        dict object of the resource
    """
    # TODO: complete revamp

    # TODO: change this to utl function and move it into the write function
    name = df_row["name"]
    labels = {lang: df_row[f"label_{lang}"] for lang in languages if df_row.get(f"label_{lang}")}
    if not labels:
        labels = {lang: df_row[lang] for lang in languages if df_row.get(lang)}
    comments = {lang: df_row[f"comment_{lang}"] for lang in languages if df_row.get(f"comment_{lang}")}
    supers = [s.strip() for s in df_row["super"].split(",")]

    # TODO: remove this to own function
    # validation
    # 4 cases:
    #  - column gui_order absent
    #  - column gui_order empty
    #  - column gui_order present but not properly filled in (missing values / not integers)
    #  - column gui_order present and properly filled in
    all_gui_order_cells = []
    if "gui_order" in entire_df:
        all_gui_order_cells = [x for x in entire_df["gui_order"] if x]
    validation_passed = True
    if not all_gui_order_cells:  # column gui_order absent or empty
        pass
    elif len(all_gui_order_cells) == len(entire_df["property"]):  # column gui_order filled in. try casting to int
        try:
            [int(float(x)) for x in entire_df["gui_order"]]
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
    for j, detail_row in entire_df.iterrows():
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


# TODO: this comes when we construct the individual sheets, otherwise the error message gets too messy
def _do_individual_class_resource_excel_compliance(
    class_df: pd.DataFrame,
    df_dict: dict[str, pd.DataFrame],
    excelfile: str,
) -> None:
    # TODO: Testing
    # check that each sheet complies
    required_columns = {"Property", "Cardinality"}
    accepted_values = {"1", "0-1", "1-n", "0-n"}


def _check_if_all_classes_have_sheet(
    class_df: pd.DataFrame,
    df_dict: dict[str, pd.DataFrame],
    excelfile: str,
) -> None:
    # TODO: Testing
    """
    This function checks if all the classes listed in the "classes" sheet have their own excel sheet and all the
    sheets are listed in the "classes" sheet.
    If not, it raises an error.
    Else it passes without an effect.

    Args:
        class_df: df from the "classes" sheet
        df_dict: dictionary with dfs from the other sheets
        excelfile: name of the Excel file

    Raises:
        UserError: If not all classes have sheets or reverse it raises the error.
    """
    classes = set(class_df["name"].tolist())
    sheets = set(df_dict.keys())
    if classes != sheets:
        difference = classes.symmetric_difference(sheets)
        raise UserError(
            f"All classes must also have their own excel sheet, "
            f"likewise all excel sheets must be listed in the 'classes' sheet.\n"
            f"In the excel file '{excelfile}' this is not the case for the class(es): {', '.join(difference)}."
        )


def _check_missing_values_in_class_sheet(df: pd.DataFrame, excelfile: str) -> None:
    """
    This function checks if all the required values are in the df.
    If all the checks are ok, the function ends without any effect.
    If any of the checks fail, a UserError is raised which contains the information in which column and row there
    are problems.

    Args:
        df: pd.DataFrame that is to be checked
        excelfile: Name of the original Excel file

    Raises:
        UserError: if any of the checks are failed
    """
    missing_dict = utl.find_missing_values_in_df(df=df, required_values_columns=["name", "super"])
    # if there are any entries in the dictionary, we call a function that creates a user-friendly error message
    if missing_dict:
        utl.create_missing_values_info_raise_error(missing_dict=missing_dict, excelfile=excelfile)


def _do_general_resource_excel_compliance(
    class_df: pd.DataFrame,
    df_dict: dict[str, pd.DataFrame],
    excelfile: str,
) -> None:
    """
    This function calls three separate functions which each checks if the pd.DataFrame is as we expect it.
    Each of these functions raises a UserError if there is a problem.
    If the checks do not fail, this function ends without an effect.

    Args:
        class_df: The pd.DataFrame that is checked
        excelfile: The name of the original Excel file

    Raises:
        UserError if any of the checks fail
    """
    # check if all the required columns are in the Excel
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
    }
    utl.check_contains_required_columns_else_raise_error(
        df=class_df,
        required_columns=required_columns,
        excelfile=excelfile,
    )
    utl.check_column_for_duplicate_else_raise_error(
        df=class_df,
        to_check_column="name",
        excelfile=excelfile,
    )

    _check_missing_values_in_class_sheet(df=class_df, excelfile=excelfile)

    _check_if_all_classes_have_sheet(class_df=class_df, df_dict=df_dict, excelfile=excelfile)


def _separate_classes_sheet_from_dict(
    df_dict: dict[str : pd.DataFrame],
    excelfile: str,
) -> pd.DataFrame and dict[str : pd.DataFrame]:
    """
    This function takes a dictionary which contains the Excel sheets as keys and the sheets as pd.DataFrame as values.
    The general sheet "classes" will be removed.
    If it doesn't exist, then the function raises an error informing the user.

    Args:
        df_dict: dictionary with df
        excelfile: name of the Excel file

    Returns:
        single df with the general information and the dict with that df removed

    Raises:
        UserError: If the sheet "classes" doesn't exist
    """
    try:
        # extract the df with the general class information
        class_df = df_dict["classes"]
    except KeyError:
        raise UserError(
            f"The excel file must contain a sheet called 'classes'.\n"
            f"The file: '{excelfile}' contains the following sheets:\n"
            f"{', '.join(df_dict.keys())}"
        ) from None

    # remove that df from the dictionary
    df_dict.pop("classes")
    return class_df, df_dict


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
        a tuple consisting of the "resources" section as a Python list,
            and the success status (True if everything went well)
    """

    df_dict = utl.read_and_clean_all_sheets_excel_file(excelfile=excelfile)

    # separate the first sheet from the dict with the other dfs
    class_df, df_dict = _separate_classes_sheet_from_dict(df_dict=df_dict, excelfile=excelfile)

    # check if the old language columns are used if they are, rename them
    class_df = utl.rename_deprecated_lang_cols(df=class_df, excelfile=excelfile)

    # check if the first sheet: "classes" is compliant to the specifications
    _do_general_resource_excel_compliance(class_df=class_df, df_dict=df_dict, excelfile=excelfile)

    # transform every row into a resource
    resources = [
        _row2resource(df_row=row, excelfile=excelfile, entire_df="property_df") for i, row in class_df.iterrows()
    ]

    # write the final "resources" section into a JSON file
    _validate_resources(resources_list=resources, excelfile=excelfile)
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(resources, file, indent=4, ensure_ascii=False)
            print("'resources' section was created successfully and written to file:", path_to_output_file)

    return resources, True
