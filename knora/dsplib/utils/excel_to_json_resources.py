import json
import os
from typing import Any, Optional

import jsonschema
import pandas as pd

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.utils.shared import prepare_dataframe, check_notna

languages = ["en", "de", "fr", "it", "rm"]


def _validate_resources_with_schema(resources_list: list[dict[str, Any]]) -> bool:
    """
    This function checks if the "resources" section of a JSON project file is valid according to the schema.

    Args:
        resources_list: the "resources" section of a JSON project as a list of dicts

    Returns:
        True if the "resources" section passed validation. Otherwise, a BaseError with a detailed error report is raised.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, "../schemas/resources-only.json")) as schema:
        resources_schema = json.load(schema)
    try:
        jsonschema.validate(instance=resources_list, schema=resources_schema)
    except jsonschema.exceptions.ValidationError as err:
        raise BaseError(f'"resources" section did not pass validation. The error message is: {err.message}\n'
                        f'The error occurred at {err.json_path}')
    return True


def _row2resource(row: pd.Series, excelfile: str) -> dict[str, Any]:
    """
    Method that takes a row from a pandas DataFrame, reads its content, and returns a dict object of the resource

    Args:
        row: row from a pandas DataFrame that defines a resource
        excelfile: Excel file where the data comes from

    Returns:
        dict object of the resource
    """

    name = row["name"]
    labels = {lang: row[lang] for lang in languages if row.get(lang)}
    comments = {lang: row[f"comment_{lang}"] for lang in languages if row.get(f"comment_{lang}")}
    supers = [s.strip() for s in row["super"].split(",")]

    # load the cardinalities of this resource
    details_df = pd.read_excel(excelfile, sheet_name=name)
    details_df = prepare_dataframe(
        df=details_df,
        required_columns=["Property", "Cardinality"],
        location_of_sheet=f"Sheet '{name}' in file '{excelfile}'"
    )

    cards = []
    for j, detail_row in details_df.iterrows():
        property_ = {
            "propname": ":" + detail_row["property"],
            "cardinality": detail_row["cardinality"].lower(),
            "gui_order": j + 1  # gui_order is equal to order in the sheet
        }
        cards.append(property_)

    # build the dict structure of this resource and append it to the list of resources
    resource = {
        "name": name,
        "super": supers,
        "labels": labels
    }
    if comments:
        resource["comments"] = comments
    resource["cardinalities"] = cards

    return resource


def excel2resources(excelfile: str, path_to_output_file: Optional[str] = None) -> list[dict[str, Any]]:
    """
    Converts resources described in an Excel file into a "resources" section which can be inserted into a JSON
    project file.

    Args:
        excelfile: path to the Excel file containing the resources
        path_to_output_file: if provided, the output is written into this JSON file

    Returns:
        the "resources" section as Python list
    """

    # load file
    all_classes_df: pd.DataFrame = pd.read_excel(excelfile)
    all_classes_df = prepare_dataframe(
        df=all_classes_df,
        required_columns=["name"],
        location_of_sheet=f"Sheet 'classes' in file '{excelfile}'"
    )

    for index, row in all_classes_df.iterrows():
        if not check_notna(row["super"]):
            raise BaseError(f"Sheet 'classes' of '{excelfile}' has a missing value in row {index + 2}, column 'super'")

    # transform every row into a resource
    resources = [_row2resource(row, excelfile) for i, row in all_classes_df.iterrows()]
    _validate_resources_with_schema(resources)

    # write final "resources" section into a JSON file
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(resources, file, indent=4, ensure_ascii=False)
            print('"resources" section was created successfully and written to file:', path_to_output_file)

    return resources
