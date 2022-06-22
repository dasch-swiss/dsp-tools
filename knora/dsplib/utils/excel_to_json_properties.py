import json
import os
import re
from typing import Any

import jsonschema
import pandas as pd

from knora.dsplib.utils.excel_to_json_resources import prepare_dataframe

languages = ["en", "de", "fr", "it", "rm"]


def _validate_properties_with_schema(json_file: str) -> bool:
    """
    This function checks if the json properties are valid according to the schema.

    Args:
        json_file: the json with the properties to be validated

    Returns:
        True if the data passed validation, False otherwise

    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, "../schemas/properties-only.json")) as schema:
        properties_schema = json.load(schema)

    try:
        jsonschema.validate(instance=json_file, schema=properties_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    print("Properties data passed schema validation.")
    return True


def _row2prop(row: pd.Series, row_count: int, excelfile: str) -> dict[str, Any]:
    """
    Takes a row from a pandas DataFrame, reads its content, and returns a dict object of the property

    Args:
        row: row from a pandas DataFrame that defines a property
        row_count: row number of Excel file
        excelfile: name of the original excel file

    Returns:
        dict object of the property
    """

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

    # build the dict structure of this property and append it to the list of properties
    _property = {
        "name": name,
        "super": supers,
        "object": _object,
        "labels": labels}
    if comments:
        _property["comments"] = comments
    _property["gui_element"] = gui_element
    if gui_attributes:
        _property["gui_attributes"] = gui_attributes

    return _property


def properties_excel2json(excelfile: str, outfile: str) -> None:
    """
    Converts properties described in an Excel file into a properties section which can be integrated into a DSP ontology

    Args:
        excelfile: path to the Excel file containing the properties
        outfile: path to the output JSON file containing the properties section for the ontology

    Returns:
        None
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
    if _validate_properties_with_schema(json.loads(json.dumps(props, indent=4))):
        with open(file=outfile, mode="w+", encoding="utf-8") as file:
            file.write('"properties": ')
            json.dump(props, file, indent=4)
            print("Properties file was created successfully and written to file: ", outfile)
    else:
        print("Properties data is not valid according to schema.")
