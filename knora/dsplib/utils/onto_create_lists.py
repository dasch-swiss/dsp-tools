import json
from typing import Any, Optional

from .expand_all_lists import expand_lists_from_excel
from .onto_validate import validate_ontology
from ..models.connection import Connection
from ..models.helpers import BaseError
from ..models.listnode import ListNode
from ..models.project import Project


def create_list_node(con: Connection, project: Project, parent_node: ListNode, nodes: list[dict[str, Any]]) -> list[
    dict[str, Any]]:
    """
    Creates the list on the DSP server

    Args:
        con: Connection to the DSP server
        project: Project which the lists should be added to
        parent_node: Root node of the list
        nodes: List of nodes the list is made of

    Returns:
        The list of all nodes with their names and respective IDs
    """
    nodelist = []
    for node in nodes:
        new_node = None
        try:
            new_node = ListNode(con=con, project=project, label=node["labels"], comments=node.get("comments"),
                                name=node["name"],
                                parent=parent_node).create()
        except BaseError as err:
            print(f"ERROR while trying to create list node '{node['name']}'. The error message was {err.message}")
            exit(1)
        if new_node:
            # if node has child nodes, call the method recursively
            if node.get("nodes"):
                subnode_list = create_list_node(con, project, new_node, node["nodes"])
                nodelist.append({new_node.name: {"id": new_node.id, "nodes": subnode_list}})
            else:
                nodelist.append({new_node.name: {"id": new_node.id}})
    return nodelist


def create_lists(input_file: str, lists_file: str, server: str, user: str, password: str, verbose: bool,
                 dump: bool = False) -> dict[str, Any]:
    """
    Handles the list creation

    Args:
        input_file: Path to the json data model file
        lists_file: Output file for the list node names and their respective IRI
        server: URL of the DSP server
        user: Username (e-mail) for the DSP server, has to have the permissions to create an ontology
        password: Password of the user
        verbose: Verbose output if True
        dump: dumps the request as JSON (used for testing)

    Returns:
        list_root_nodes: Dictionary of node names and their respective IRI
    """
    # read the ontology from the input file
    with open(input_file) as f:
        onto_json_str = f.read()

    data_model = json.loads(onto_json_str)

    # expand all lists referenced in the list section of the data model
    new_lists = expand_lists_from_excel(data_model)

    # add the newly created lists from Excel to the ontology
    data_model["project"]["lists"] = new_lists

    # validate the ontology
    if validate_ontology(data_model):
        pass
    else:
        exit(1)

    # Connect to the DaSCH Service Platform API
    con = Connection(server)
    con.login(user, password)

    if dump:
        con.start_logging()

    # get the project which must exist
    project: Optional[Project] = None
    try:
        project = Project(con=con, shortcode=data_model["project"]["shortcode"]).read()
    except BaseError as err:
        print(
            f"ERROR while trying to create the lists. Referenced project couldn't be read from the server. The error message was: {err.message}")
        exit(1)

    # create the lists
    if verbose:
        print("Create lists...")

    all_lists: Optional[list[ListNode]] = ListNode.getAllLists(con, project.id)
    lists = data_model["project"].get("lists")
    list_root_nodes = {}
    if lists:
        for rootnode in lists:
            rootnode_name = rootnode["name"]
            # check if list already exists
            list_exists: bool = False
            if all_lists:
                for list_item in all_lists:
                    if list_item.project == project.id and list_item.name == rootnode_name:
                        list_root_nodes[list_item.name] = {"id": list_item.id, "nodes": rootnode["nodes"]}
                        list_exists = True
            if list_exists:
                print(f"WARN List '{rootnode_name}' already exists. Skipping...")
                continue

            if verbose:
                print(f"Creating list '{rootnode_name}'.")

            root_list_node = None
            try:
                root_list_node = ListNode(con=con, project=project, label=rootnode["labels"],
                                          comments=rootnode.get("comments"),
                                          name=rootnode_name).create()
            except BaseError as err:
                print(f"ERROR while trying to create the list '{rootnode_name}'. The error message was: {err.message}")
                exit(1)
            except Exception as exception:
                print(
                    f"ERROR while trying to create the list '{rootnode_name}'. The error message was: {exception}")
                exit(1)
            if rootnode.get("nodes") and root_list_node and project:
                list_nodes = create_list_node(con, project, root_list_node, rootnode["nodes"])
                list_root_nodes[rootnode["name"]] = {"id": root_list_node.id, "nodes": list_nodes}

    with open(lists_file, "w", encoding="utf-8") as fp:
        json.dump(list_root_nodes, fp, indent=4, sort_keys=True)
        print(f"The IRI for the created nodes can be found in '{lists_file}'.")

    return list_root_nodes
