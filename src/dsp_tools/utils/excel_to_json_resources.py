import importlib.resources
import json
import warnings
from typing import Any, Optional

import jsonpath_ng.ext
import jsonschema
import pandas as pd
import regex

from dsp_tools.models.exceptions import BaseError
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
        BaseError with a detailed error report if the validation fails

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
        raise BaseError(err_msg) from None

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
        raise BaseError(err_msg)

    return True


def _row2resource(
    row: pd.Series,
    excelfile: str,
) -> dict[str, Any]:
    """
    Method that reads one row from the "classes" DataFrame,
    opens the corresponding details DataFrame,
    and builds a dict object of the resource.

    Args:
        row: row from the "classes" DataFrame
        excelfile: Excel file where the data comes from

    Raises:
        BaseError if the row or the details sheet contains invalid data

    Returns:
        dict object of the resource
    """

    name = row["name"]
    labels = {lang: row[f"label_{lang}"] for lang in languages if row.get(f"label_{lang}")}
    if not labels:
        labels = {lang: row[lang] for lang in languages if row.get(lang)}
    comments = {lang: row[f"comment_{lang}"] for lang in languages if row.get(f"comment_{lang}")}
    supers = [s.strip() for s in row["super"].split(",")]

    # load the cardinalities of this resource
    try:
        details_df = pd.read_excel(excelfile, sheet_name=name)
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
        try:
            details_df = pd.read_excel(excelfile, sheet_name=name)
        except ValueError as err:
            raise BaseError(str(err)) from None
        p.stop()
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
        raise BaseError(
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
        BaseError if something went wrong

    Returns:
        a tuple consisting of the "resources" section as Python list,
            and the success status (True if everything went well)
    """

    # load file
    try:
        all_classes_df: pd.DataFrame = pd.read_excel(excelfile)
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
        all_classes_df = pd.read_excel(excelfile)
        p.stop()
    all_classes_df = prepare_dataframe(
        df=all_classes_df,
        required_columns=["name"],
        location_of_sheet=f"Sheet 'classes' in file '{excelfile}'",
    )

    # validation
    for index, row in all_classes_df.iterrows():
        index = int(str(index))  # index is a label/index/hashable, but we need an int
        if not check_notna(row["super"]):
            raise BaseError(f"Sheet 'classes' of '{excelfile}' has a missing value in row {index + 2}, column 'super'")
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
            print('"resources" section was created successfully and written to file:', path_to_output_file)

    return resources, True
