import json
from typing import Any, Dict, List

from .expand_all_lists import expand_lists_from_excel
from .onto_validate import validate_ontology
from ..models.connection import Connection
from ..models.listnode import ListNode
from ..models.project import Project


def list_creator(con: Connection, project: Project, parent_node: ListNode, nodes: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
    """
    Creates the list on the DSP server

    Args:
        con: The connection to the DSP server
        project: The project which the lists should be added
        parent_node: The root node of the list
        nodes: List of nodes the list is made of

    Returns:
        The list of all nodes with their names and respective IDs
    """
    nodelist = []
    for node in nodes:
        new_node = ListNode(con=con, project=project, label=node["labels"], comments=node.get("comments"),
                            name=node["name"],
                            parent=parent_node).create()
        if node.get('nodes') is not None:
            subnode_list = list_creator(con, project, new_node, node['nodes'])
            nodelist.append({new_node.name: {"id": new_node.id, 'nodes': subnode_list}})
        else:
            nodelist.append({new_node.name: {"id": new_node.id}})
    return nodelist


def create_lists(input_file: str, lists_file: str, server: str, user: str, password: str, verbose: bool,
                 dump: bool = False) -> Dict[str, Any]:
    """
    Creates the lists on the DSP server

    Args:
        input_file: Path to the json data model file
        lists_file: Output file for the list node names and their respective IRI
        server: URL of the DSP server
        user: Username (e-mail) for the DSP server, has to have the permissions to create an ontology
        password: Password of the user
        verbose: Verbose output if True
        dump: ???

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
    data_model['project']['lists'] = new_lists

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
    project = Project(con=con, shortcode=data_model['project']['shortcode'], ).read()
    assert project is not None

    # create the lists
    if verbose:
        print('Create lists...')

    lists = data_model['project'].get('lists')
    list_root_nodes = {}
    if lists is not None:
        for rootnode in lists:
            if verbose:
                print('  Create list:' + rootnode['name'])
            root_list_node = ListNode(con=con, project=project, label=rootnode['labels'],
                                      comments=rootnode.get('comments'),
                                      name=rootnode['name']).create()
            if rootnode.get('nodes') is not None:
                list_nodes = list_creator(con, project, root_list_node, rootnode['nodes'])
                list_root_nodes[rootnode['name']] = {'id': root_list_node.id, 'nodes': list_nodes}

    with open(lists_file, 'w', encoding='utf-8') as fp:
        json.dump(list_root_nodes, fp, indent=3, sort_keys=True)
        print(f'The IRI for the created nodes can be found in {lists_file}.')

    return list_root_nodes
