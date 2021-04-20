import os
import json
from jsonschema import validate
from typing import List, Set, Dict, Tuple, Optional, Any, Union, NewType

from .onto_commons import validate_list_from_excel, json_list_from_excel

from pprint import pprint

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
    with open(input_file) as f:
        jsonstr = f.read()
    datapath = os.path.dirname(input_file)
    validate_ontology_from_string(jsonstr, datapath)


def validate_ontology_from_string(jsonstr: str, exceldir: Optional[str] = None) -> None:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(current_dir, 'knora-schema.json')) as s:
        schema = json.load(s)
    datamodel = json.loads(jsonstr)

    #
    # now let's see if there are any lists defined as reference to excel files
    #
    lists = datamodel["project"].get('lists')
    if lists is not None:
        newlists: [] = []
        for rootnode in lists:
            if rootnode.get("nodes") is not None and isinstance(rootnode["nodes"], dict) and rootnode["nodes"].get("file") is not None:
                newroot = {
                    "name": rootnode.get("name"),
                    "labels": rootnode.get("labels")
                }
                if rootnode.get("comments") is not None:
                    newroot["comments"] = rootnode["comments"]
                startrow = 1 if rootnode["nodes"].get("startrow") is None else rootnode["nodes"]["startrow"]
                startcol = 1 if rootnode["nodes"].get("startcol") is None else rootnode["nodes"]["startcol"]
                #
                # determine where to find the excel file...
                #
                excelpath = rootnode["nodes"]["file"]
                if excelpath[0] != '/' and exceldir is not None:
                    excelpath = os.path.join(exceldir, excelpath)
                json_list_from_excel(rootnode=newroot,
                                     filepath=excelpath,
                                     sheetname=rootnode["nodes"]["worksheet"],
                                     startrow=startrow,
                                     startcol=startcol)
                newlists.append(newroot)
            else:
                newlists.append(rootnode)
        datamodel["project"]["lists"] = newlists

    with open("gaga.json", "w") as outfile:
        json.dump(datamodel, outfile, indent=4)

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)

    print("Data model is syntactically correct and passed validation!")


