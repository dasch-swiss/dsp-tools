from typing import Any
from typing import Optional
from typing import Union

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.commands.project.legacy_models.listnode import ListNode
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.json_parsing import parse_json_input


def create_lists_on_server(
    lists_to_create: list[dict[str, Any]],
    con: Connection,
    project_remote: Project,
) -> tuple[dict[str, Any], bool]:
    """
    Creates the "lists" section of a JSON project definition on a DSP server.
    If a list with the same name is already existing in this project on the DSP server, this list is skipped.
    If a node or an entire list cannot be created, an error message is printed, but the process continues.

    Args:
        lists_to_create: "lists" section of a JSON project definition
        con: connection to the DSP server
        project_remote: representation of the project on the DSP server

    Raises:
        BaseError: if one of the lists to be created already exists on the DSP server, but it has no name

    Returns:
        tuple consisting of the IRIs of the list nodes and the success status (True if everything went well)
    """

    overall_success = True

    # retrieve existing lists
    try:
        existing_lists = ListNode.getAllLists(con=con, project_iri=project_remote.iri)
    except BaseError:
        err_msg = "Unable to retrieve existing lists on DSP server. Cannot check if your lists are already existing."
        print(f"WARNING: {err_msg}")
        logger.exception(err_msg)
        existing_lists = []
        overall_success = False

    current_project_lists: dict[str, Any] = {}
    for new_lst in lists_to_create:
        if existing_lst := [x for x in existing_lists if x.project == project_remote.iri and x.name == new_lst["name"]]:
            existing_list_name = existing_lst[0].name
            if not existing_list_name:
                raise BaseError(f"Node {existing_lst[0]} has no name.")
            current_project_lists[existing_list_name] = {
                "id": existing_lst[0].iri,
                "nodes": new_lst["nodes"],
            }
            print(f"    WARNING: List '{new_lst['name']}' already exists on the DSP server. Skipping...")
            overall_success = False
            continue

        created_list, success = _create_list_node(con=con, project=project_remote, node=new_lst)
        current_project_lists.update(created_list)
        if not success:
            overall_success = False
        print(f"    Created list '{new_lst['name']}'.")

    return current_project_lists, overall_success


def _create_list_node(
    con: Connection,
    project: Project,
    node: dict[str, Any],
    parent_node: Optional[ListNode] = None,
) -> tuple[dict[str, Any], bool]:
    """
    Creates a list node on the DSP server, recursively scanning through all its subnodes, creating them as well.
    If a node cannot be created, an error message is printed, but the process continues.

    Args:
        con: connection to the DSP server
        project: project that holds the list where this node should be added to
        node: the node to be created
        parent_node: parent node of the node to be created (optional)

    Returns:
        Returns a tuple consisting of a dict and a bool.
        The dict contains the IRIs of the created list nodes,
        nested according to their hierarchy structure,
        i.e. ``{nodename: {"id": IRI, "nodes": {...}}}``.
        The bool is True if all nodes could be created,
        False if any node could not be created.

    Raises:
        BaseError: if the created node has no name
    """
    new_node: ListNode = ListNode(
        con=con,
        project=project,
        label=node["labels"],
        comments=node.get("comments"),
        name=node["name"],
        parent=parent_node,
    )
    try:
        new_node = new_node.create()
    except BaseError:
        print(f"WARNING: Cannot create list node '{node['name']}'.")
        logger.exception(f"Cannot create list node '{node['name']}'.")
        return {}, False

    # if node has child nodes, call the method recursively
    if node.get("nodes"):
        overall_success = True
        subnode_list = []
        for subnode in node["nodes"]:
            created_subnode, success = _create_list_node(con=con, project=project, node=subnode, parent_node=new_node)
            subnode_list.append(created_subnode)
            if not success:
                overall_success = False
        if not new_node.name:
            raise BaseError(f"Node {new_node} has no name.")
        return {new_node.name: {"id": new_node.iri, "nodes": subnode_list}}, overall_success
    else:
        if not new_node.name:
            raise BaseError(f"Node {new_node} has no name.")
        return {new_node.name: {"id": new_node.iri}}, True


def create_only_lists(
    project_file_as_path_or_parsed: Union[str, dict[str, Any]],
    creds: ServerCredentials,
) -> tuple[dict[str, Any], bool]:
    """
    This function accepts a JSON project definition,
    connects to a DSP server,
    and uploads the "lists" section to the server.

    The project must already exist on the DSP server.
    If a list with the same name is already existing in this project on the DSP server, this list is skipped.

    Args:
        project_file_as_path_or_parsed: path to the JSON project definition, or parsed JSON object
        creds: credentials to connect to the DSP server

    Raises:
        InputError:
          - if the project cannot be read from the server
          - if the connection to the DSP server cannot be established

        BaseError:
          - if the input is invalid
          - if a problem occurred while trying to expand the Excel files
          - if the JSON file is invalid according to the schema

    Returns:
        Returns a tuple consisting of a dict and a bool.
        The dict contains the IRIs of the created list nodes,
        nested according to their hierarchy structure,
        i.e. ``{nodename: {"id": IRI, "nodes": {...}}}``.
        If there are no lists in the project definition,
        an empty dictionary is returned.
        The bool indicates if everything went smoothly during the process.
        If a warning or error occurred (e.g. one of the lists already exists,
        or one of the nodes could not be created),
        it is False.
    """
    project_definition = parse_json_input(project_file_as_path_or_parsed=project_file_as_path_or_parsed)
    if not project_definition.get("project", {}).get("lists"):
        return {}, True
    validate_project(project_definition)
    print("JSON project file is syntactically correct and passed validation.")

    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)
    con = ConnectionLive(creds.server, auth)

    # retrieve the project
    shortcode = project_definition["project"]["shortcode"]
    project_local = Project(con=con, shortcode=shortcode)
    try:
        project_remote = project_local.read()
    except BaseError:
        err_msg = f"Unable to create the lists: The project {shortcode} cannot be found on the DSP server."
        logger.exception(err_msg)
        raise InputError(err_msg) from None

    # create new lists
    current_project_lists, success = create_lists_on_server(
        lists_to_create=project_definition["project"]["lists"],
        con=con,
        project_remote=project_remote,
    )

    return current_project_lists, success
