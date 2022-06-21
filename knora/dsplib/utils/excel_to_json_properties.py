import json
import os
import re
from typing import Any

import jsonschema
import pandas as pd

from knora.dsplib.utils.excel_to_json_resources import _prepare_dataframe


def _validate_properties_with_schema(json_file: str) -> bool:
    """
    This function checks if the json properties are valid according to the schema.

    Args:
        json_file: the json with the properties to be validated

    Returns:
        True if the data passed validation, False otherwise

    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, '../schemas/properties-only.json')) as schema:
        properties_schema = json.load(schema)

    try:
        jsonschema.validate(instance=json_file, schema=properties_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    print('Properties data passed schema validation.')
    return True


def _row2prop(row: pd.Series, row_count: int, excelfile: str) -> dict[str, Any]:
    """
    Method that takes a row from a pandas DataFrame, reads its content, and returns a dict object of the property

    Args:
        row: row from a pandas DataFrame that defines a property
        row_count: row number of Excel file
        excelfile: name of the original excel file

    Returns:
        dict object of the property
    """

    name = row["name"]
    supers = [s.strip() for s in row["super"].split(",")]
    object = row["object"]

    labels = {}
    if row.get("en"):
        labels["en"] = row["en"]
    if row.get("de"):
        labels["de"] = row["de"]
    if row.get("fr"):
        labels["fr"] = row["fr"]
    if row.get("it"):
        labels["it"] = row["it"]
    if row.get("rm"):
        labels["rm"] = row["rm"]

    comments = {}
    if row.get("comment_en"):
        comments["en"] = row["comment_en"]
    if row.get("comment_de"):
        comments["de"] = row["comment_de"]
    if row.get("comment_fr"):
        comments["fr"] = row["comment_fr"]
    if row.get("comment_it"):
        comments["it"] = row["comment_it"]
    if row.get("comment_rm"):
        comments["rm"] = row["comment_rm"]

    gui_element = row["gui_element"]

    gui_attributes = dict()
    if row.get("hlist"):
        gui_attributes["hlist"] = row["hlist"]
    if row.get("gui_attributes"):
        pairs = row["gui_attributes"].split(",")
        for pair in pairs:
            if pair.count(":") != 1:
                raise ValueError(f'Row {row_count} of Excel file {excelfile} contains invalid data in column '
                                 f'"gui_attributes". The expected format is "attribute: value[, attribute: value]".')
            attr, val = [x.strip() for x in pair.split(':')]
            if re.search(r'^\d+\.\d+$', val):
                val = float(val)
            elif re.search(r'^\d+$', val):
                val = int(val)
            gui_attributes[attr] = val

    # build the dict structure of this property and append it to the list of properties
    property = {
        "name": name,
        "super": supers,
        "object": object,
        "labels": labels}
    if comments:
        property["comments"] = comments
    property["gui_element"] = gui_element
    if gui_attributes:
        property["gui_attributes"] = gui_attributes

    return property


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
    df = _prepare_dataframe(
        df=df,
        required_columns=["name", "super", "object", "gui_element"],
        location_of_sheet=f"File '{excelfile}'")

    # transform every row into a property
    props: list[dict[str, Any]] = list()
    for i, row in df.iterrows():
        prop = _row2prop(row, i, excelfile)
        props.append(prop)

    # write final list to JSON file if list passed validation
    if _validate_properties_with_schema(json.loads(json.dumps(props, indent=4))):
        with open(file=outfile, mode='w+', encoding='utf-8') as file:
            file.write('"properties": ')
            json.dump(props, file, indent=4)
            print('Properties file was created successfully and written to file: ', outfile)
    else:
        print('Properties data is not valid according to schema.')
