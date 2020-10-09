import os
import json
from jsonschema import validate

from ..models.helpers import Actions, BaseError, Context, Cardinality
from ..models.connection import Connection
from ..models.project import Project
from ..models.listnode import ListNode
from .onto_commons import list_creator

def create_lists (input_file: str, output_file: str, server: str, user: str, password: str, verbose: bool) -> bool:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # let's read the schema for the data model definition
    with open(os.path.join(current_dir, 'knora-schema-lists.json')) as s:
        schema = json.load(s)
    # read the data model definition
    with open(input_file) as f:
        datamodel = json.load(f)

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)
    if verbose:
        print("Data model is syntactically correct and passed validation!")

    #
    # Connect to the DaSCH Service Platform API
    #
    con = Connection(server)
    con.login(user, password)

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
                comment=rootnode.get('comments'),
                name=rootnode['name']
            ).create()
            listnodes = list_creator(con, project, root_list_node, rootnode['nodes'])
            listrootnodes[rootnode['name']] = {
                "id": root_list_node.id,
                "nodes": listnodes
            }

    with open(output_file, 'w', encoding="utf-8") as fp:
        json.dump(listrootnodes, fp, indent=3, sort_keys=True)
        print("The definitions of the node-id's can be found in \"{}}\"!".format(output_file))
    return True
