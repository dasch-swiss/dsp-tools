import json
import os
import re
from typing import Any, Optional

import jsonschema
import pandas as pd

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.utils.shared import prepare_dataframe, check_notna

languages = ["en", "de", "fr", "it", "rm"]


def _validate_properties_with_schema(properties_list: list[dict[str, Any]]) -> bool:
    """
    This function checks if the "properties" section of a JSON project file is valid according to the schema.

    Args:
        properties_list: the "properties" section of a JSON project as a list of dicts

    Returns:
        True if the "properties" section passed validation. Otherwise, a BaseError with a detailed error report is raised.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, "../schemas/properties-only.json")) as schema:
        properties_schema = json.load(schema)
    try:
        jsonschema.validate(instance=properties_list, schema=properties_schema)
    except jsonschema.exceptions.ValidationError as err:
        raise BaseError(f'"properties" section did not pass validation. The error message is: {err.message}\n'
                        f'The error occurred at {err.json_path}')
    return True


def _row2prop(row: pd.Series, row_count: int, excelfile: str) -> dict[str, Any]:
    """
    Takes a row from a pandas DataFrame, reads its content, and returns a dict object of the property

    Args:
        row: row from a pandas DataFrame that defines a property
        row_count: row number of Excel file
        excelfile: name of the original Excel file

    Returns:
        dict object of the property
    """

    # extract the elements that are necessary to build the property
    name = row["name"]
    supers = [s.strip() for s in row["super"].split(",")]
    _object = row["object"]
    labels = {lang: row[lang] for lang in languages if row.get(lang)}
    comments = {lang: row[f"comment_{lang}"] for lang in languages if row.get(f"comment_{lang}")}
    gui_element = row["gui_element"]
    gui_attributes = dict()
    if row.get("hlist"):
        gui_attributes["hlist"] = row["hlist"]
    if row.get("gui_attributes"):
        pairs = row["gui_attributes"].split(",")
        for pair in pairs:
            if pair.count(":") != 1:
                raise ValueError(f"Row {row_count} of Excel file {excelfile} contains invalid data in column "
                                 f"'gui_attributes'. The expected format is 'attribute: value[, attribute: value]'.")
            attr, val = [x.strip() for x in pair.split(":")]
            if re.search(r"^\d+\.\d+$", val):
                val = float(val)
            elif re.search(r"^\d+$", val):
                val = int(val)
            gui_attributes[attr] = val

    # build the dict structure of this property
    _property = {
        "name": name,
        "super": supers,
        "object": _object,
        "labels": labels
    }
    if comments:
        _property["comments"] = comments
    _property["gui_element"] = gui_element
    if gui_attributes:
        _property["gui_attributes"] = gui_attributes

    return _property


def excel2properties(excelfile: str, path_to_output_file: Optional[str] = None) -> list[dict[str, Any]]:
    """
    Converts properties described in an Excel file into a "properties" section which can be inserted into a JSON
    project file.

    Args:
        excelfile: path to the Excel file containing the properties
        path_to_output_file: if provided, the output is written into this JSON file

    Returns:
        the "properties" section as Python list
    """
    
    # load file
    df: pd.DataFrame = pd.read_excel(excelfile)
    df = prepare_dataframe(
        df=df,
        required_columns=["name"],
        location_of_sheet=f"File '{excelfile}'"
    )

    required = ["super", "object", "gui_element"]
    for index, row in df.iterrows():
        for req in required:
            if not check_notna(row[req]):
                raise BaseError(f"'{excelfile}' has a missing value in row {index + 2}, column '{req}'")

    # transform every row into a property
    props = [_row2prop(row, i, excelfile) for i, row in df.iterrows()]
    _validate_properties_with_schema(props)

    # write final JSON file
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(props, file, indent=4, ensure_ascii=False)
            print('"properties" section was created successfully and written to file:', path_to_output_file)

    return props
