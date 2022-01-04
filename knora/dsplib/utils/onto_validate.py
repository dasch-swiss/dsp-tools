import json
import os
from typing import Dict, Union

import jsonschema
from jsonschema import validate

from ..utils.expand_all_lists import expand_lists_from_excel


def validate_ontology(input_file_or_json: Union[str, Dict, os.PathLike]) -> bool:
    """
    Validates an ontology against the knora schema

    Args:
        input_file_or_json: the ontology to be validated, can either be a file or a json string (dict)

    Returns:
        True if ontology passed validation, False otherwise
    """
    data_model = ''

    if isinstance(input_file_or_json, dict):
        data_model = input_file_or_json
    elif os.path.isfile(input_file_or_json):
        with open(input_file_or_json) as f:
            onto_json_str = f.read()
        data_model = json.loads(onto_json_str)
    else:
        print('Input is not valid.')
        exit(1)

    # expand all lists referenced in the list section of the data model
    new_lists = expand_lists_from_excel(data_model)

    # add the newly created lists from Excel to the ontology
    data_model['project']['lists'] = new_lists

    # validate the data model against the schema
    current_dir = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(current_dir, '../schemas/ontology.json')) as s:
        schema = json.load(s)

    try:
        validate(instance=data_model, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        print('Data model did not pass validation. The error message is:', err.message)
        return False
    print('Data model is syntactically correct and passed validation.')
    return True
