import json
import re
from typing import Any
import jsonschema
import pandas as pd

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.utils.shared_methods import prepare_dataframe

languages = ["en", "de", "fr", "it", "rm"]


def _validate_properties_with_schema(properties_list: list[dict[str, Any]]) -> bool:
    """
    This function checks if the "properties" section of a JSON project file is valid according to the schema.

    Args:
        properties_list: the "properties" section of a JSON project as a list of dicts

    Returns:
        True if the "properties" section passed validation. Otherwise, a BaseError with a detailed error report is raised.
    """
    with open("knora/dsplib/schemas/properties-only.json") as schema:
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


def excel2properties(excelfile: str, outfile: str) -> list[dict[str, Any]]:
    """
    Converts properties described in an Excel file into a "properties" section which can be inserted into a JSON
    project file.

    Args:
        excelfile: path to the Excel file containing the properties
        outfile: path to the JSON file the output is written into

    Returns:
        the "properties" section as Python list
    """
    
    # load file
    df: pd.DataFrame = pd.read_excel(excelfile)
    df = prepare_dataframe(
        df=df,
        required_columns=["name", "super", "object", "gui_element"],
        location_of_sheet=f"File '{excelfile}'")

    # transform every row into a property
    props = [_row2prop(row, i, excelfile) for i, row in df.iterrows()]

    # write final list to JSON file if list passed validation
    _validate_properties_with_schema(props)
    with open(file=outfile, mode="w", encoding="utf-8") as file:
        json.dump({"properties": props}, file, indent=4, ensure_ascii=False)
        print('"properties" section was created successfully and written to file:', outfile)

    return props
