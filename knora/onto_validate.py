import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
import sys
import re

from knora.models.helpers import Actions, BaseError, Context, Cardinality
from knora.models.langstring import Languages, LangStringParam, LangString
from knora.models.connection import Connection, Error
from knora.models.project import Project
from knora.models.listnode import ListNode
from knora.models.group import Group
from knora.models.user import User
from knora.models.ontology import Ontology
from knora.models.propertyclass import PropertyClass
from knora.models.resourceclass import ResourceClass


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

