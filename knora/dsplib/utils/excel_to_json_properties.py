import json
import os

import jsonschema
from openpyxl import load_workbook


def validate_properties_with_schema(json_file: str) -> bool:
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


def properties_excel2json(excelfile: str, outfile: str):
    """
        Converts properties described in an Excel file into a properties section which can be integrated into a DSP ontology

        Args:
            excelfile: path to the Excel file containing the properties
            outfile: path to the output JSON file containing the properties section for the ontology

        Returns:
            None
    """
    # load file
    wb = load_workbook(filename=excelfile, read_only=True)
    sheet = wb.worksheets[0]
    props = [row_to_prop(row) for row in sheet.iter_rows(min_row=2, values_only=True, max_col=9)]

    prefix = '"properties":'

    if validate_properties_with_schema(json.loads(json.dumps(props, indent=4))):
        # write final list to JSON file if list passed validation
        with open(file=outfile, mode='w+', encoding='utf-8') as file:
            file.write(prefix)
            json.dump(props, file, indent=4)
            print('Properties file was created successfully and written to file:', outfile)
    else:
        print('Properties data is not valid according to schema.')

    return props


def row_to_prop(row):
    """
    Parses the row of an Excel sheet and makes a property from it

    Args:
        row: the row of an Excel sheet

    Returns:
        prop (JSON): the property in JSON format
    """
    name, super_, object_, en, de, fr, it, gui_element, hlist = row
    labels = {}
    if en:
        labels['en'] = en
    if de:
        labels['de'] = de
    if fr:
        labels['fr'] = fr
    if it:
        labels['it'] = it
    if not labels:
        raise Exception(f"No label given in any of the four languages: {name}")
    prop = {
        'name': name,
        'super': [super_],
        'object': object_,
        'labels': labels,
        'gui_element': gui_element
    }
    if hlist:
        prop['gui_attributes'] = {'hlist': hlist}
    return prop
