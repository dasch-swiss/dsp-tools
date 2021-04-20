import os
from typing import List, Set, Dict, Tuple, Optional
import json
from jsonschema import validate

from ..models.helpers import Actions, BaseError, Context, Cardinality
from .onto_commons import list_creator, validate_list_from_excel, json_list_from_excel


def list_excel2json(excelpath: str,
                    sheetname: str,
                    shortcode: str,
                    listname: str,
                    label: str,
                    lang: str,
                    outfile: str,
                    verbose: bool):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    langs = ["en", "de", "fr", "it"]

    if lang not in langs:
        raise BaseError(f"Language '{lang}' not supported!")

    rootnode = {
        "name": listname,
        "labels": {
            lang: label
        }
    }

    json_list_from_excel(rootnode, excelpath, sheetname)
    jsonobj = {
        "project": {
            "shortcode": shortcode,
            "lists": [
                rootnode
            ]
        }
    }
    with open(os.path.join(current_dir, 'knora-schema-lists.json')) as s:
        schema = json.load(s)
    validate(jsonobj, schema)
    with open(outfile, "w") as outfile:
        json.dump(jsonobj, outfile, indent=4)
