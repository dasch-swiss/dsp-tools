import json
import os
import re
from typing import Any

import jsonschema
import pandas as pd

languages = ["en", "de", "fr", "it", "rm"]


def _validate_resources_with_schema(json_file: str) -> bool:
    """
    This function checks if the json resources are valid according to the schema.

    Args:
        json_file: the json with the resources to be validated

    Returns:
        True if the data passed validation, False otherwise
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, "../schemas/resources-only.json")) as schema:
        resources_schema = json.load(schema)

    try:
        jsonschema.validate(instance=json_file, schema=resources_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    print("Resource data passed schema validation.")
    return True


def prepare_dataframe(df: pd.DataFrame, required_columns: list[str], location_of_sheet: str) -> pd.DataFrame:
    """
    Takes a pandas DataFrame, strips the column headers from whitespaces and transforms them to lowercase,
    strips every cell from whitespaces and inserts "" if there is no string in it, and deletes the rows that don't have
    a value in one of the required cells.

    Args:
        df: pandas DataFrame
        required_columns: headers of the columns where a value is required
        location_of_sheet: for better error messages, provide this information of the caller

    Returns:
        prepared DataFrame
    """

    any_char_regex = r"[\wäàçëéèêïöôòüÄÀÇËÉÊÏÖÔÒÜ]"

    # strip column headers and transform to lowercase, so that the script doesn't break when the headers vary a bit
    new_df = df.rename(columns=lambda x: x.strip().lower())
    required_columns = [x.strip().lower() for x in required_columns]
    # strip every cell, and insert "" if there is no valid word in it
    new_df = new_df.applymap(lambda x: str(x).strip() if pd.notna(x) and re.search(any_char_regex, str(x), flags=re.IGNORECASE) else "")
    # delete rows that don't have the required columns
    for req in required_columns:
        if req not in new_df:
            raise ValueError(f"{location_of_sheet} requires a column named '{req}'")
        new_df = new_df[pd.notna(new_df[req])]
        new_df = new_df[[bool(re.search(any_char_regex, x, flags=re.IGNORECASE)) for x in new_df[req]]]
    if len(new_df) < 1:
        raise ValueError(f"{location_of_sheet} requires at least one row")
    return new_df


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


def resources_excel2json(excelfile: str, outfile: str) -> None:
    """
    Converts properties described in an Excel file into a properties section which can be integrated into a DSP ontology

    Args:
        excelfile: path to the Excel file containing the properties
        outfile: path to the output JSON file containing the properties section for the ontology

    Returns:
        None
    """

    # load file
    all_classes_df: pd.DataFrame = pd.read_excel(excelfile)
    all_classes_df = prepare_dataframe(
        df=all_classes_df,
        required_columns=["name", "super"],
        location_of_sheet=f"Sheet 'classes' in file '{excelfile}'")

    # transform every row into a resource
    resources = [_row2resource(row, excelfile) for i, row in all_classes_df.iterrows()]

    # write final list of all resources to JSON file, if list passed validation
    if _validate_resources_with_schema(json.loads(json.dumps(resources, indent=4))):
        with open(file=outfile, mode="w+", encoding="utf-8") as file:
            file.write('"resources": ')
            json.dump(resources, file, indent=4)
            print("Resource file was created successfully and written to file ", outfile)
    else:
        print("Resource data is not valid according to schema.")
