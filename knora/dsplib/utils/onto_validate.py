import os
import json
from jsonschema import validate


def validate_list(input_file: str) -> None:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # let's read the schema for the data model definition
    with open(os.path.join(current_dir, 'knora-schema-lists.json')) as s:
        schema = json.load(s)
    # read the data model definition
    with open(input_file) as f:
        datamodel = json.load(f)

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)
    print("Data model is syntactically correct and passed validation!")


def validate_ontology(input_file: str) -> None:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(current_dir, 'knora-schema.json')) as s:
        schema = json.load(s)
    # read the data model definition
    with open(input_file) as f:
        datamodel = json.load(f)

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)
    print("Data model is syntactically correct and passed validation!")

