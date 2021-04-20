import os
import json
from jsonschema import validate

from ..models.helpers import Actions, BaseError, Context, Cardinality
from ..models.connection import Connection
from ..models.project import Project
from ..models.listnode import ListNode
from .onto_commons import list_creator, validate_list_from_excel, json_list_from_excel


def create_lists(input_file: str, lists_file: str, server: str, user: str, password: str, verbose: bool, dump: bool = False) -> bool:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # let's read the schema for the data model definition
    with open(os.path.join(current_dir, 'knora-schema-lists.json')) as s:
        schema = json.load(s)
    # read the data model definition
    with open(input_file) as f:
        datamodel = json.load(f)

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
                    "labels": rootnode.get("labels"),
                    "comments": rootnode.get("comments")
                }
                startrow = 1 if rootnode["nodes"].get("startrow") is None else rootnode["nodes"]["startrow"]
                startcol = 1 if rootnode["nodes"].get("startcol") is None else rootnode["nodes"]["startcol"]
                json_list_from_excel(rootnode=newroot,
                                     filepath=rootnode["nodes"]["file"],
                                     sheetname=rootnode["nodes"]["worksheet"],
                                     startrow=startrow,
                                     startcol=startcol)
                newlists.append(newroot)
            else:
                newlists.append(rootnode)
        datamodel["project"]["lists"] = newlists

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)

    if verbose:
        print("Data model is syntactically correct and passed validation!")

    #
    # Connect to the DaSCH Service Platform API
    #
    con = Connection(server)
    con.login(user, password)

    if dump:
        con.start_logging()

    # --------------------------------------------------------------------------
    # let's read the prefixes of external ontologies that may be used
    #
    context = Context(datamodel["prefixes"])

    # --------------------------------------------------------------------------
    # Let's get the project which must exist
    #
    project = Project(
        con=con,
        shortcode=datamodel["project"]["shortcode"],
    ).read()
    assert project is not None

    # --------------------------------------------------------------------------
    # now let's create the lists
    #
    if verbose:
        print("Creating lists...")
    lists = datamodel["project"].get('lists')
    listrootnodes = {}
    if lists is not None:
        for rootnode in lists:
            if verbose is not None:
                print("  Creating list:" + rootnode['name'])
            root_list_node = ListNode(
                con=con,
                project=project,
                label=rootnode['labels'],
                #comment=rootnode.get('comments'),
                name=rootnode['name']
            ).create()
            if rootnode.get('nodes') is not None:
                listnodes = list_creator(con, project, root_list_node, rootnode['nodes'])
                listrootnodes[rootnode['name']] = {
                    "id": root_list_node.id,
                    "nodes": listnodes
                }

    with open(lists_file, 'w', encoding="utf-8") as fp:
        json.dump(listrootnodes, fp, indent=3, sort_keys=True)
        print(f"The definitions of the node-id's can be found in \"{lists_file}\"!")
    return True
