import json
from typing import Any, Optional, Tuple

from .excel_to_json_lists import expand_lists_from_excel
from .onto_validate import validate_project
from ..models.connection import Connection
from ..models.helpers import BaseError
from ..models.listnode import ListNode
from ..models.project import Project
from .shared_methods import login, try_network_action


def _create_list_node(
    con: Connection,
    project: Project,
    node: dict[str, Any],
    parent_node: Optional[ListNode] = None
) -> Tuple[dict[str, Any], bool]:
    """
    Creates a list node on the DSP server, recursively scanning through all its subnodes, creating them as well.
    Returns a tuple consisting of a dict and a bool. The dict contains the IRIs of the created list nodes. The bool
    indicates if all nodes could be created or not.

    Args:
        con: connection to the DSP server
        project: project that holds the list where this node should be added to
        node: the node to be created
        parent_node: parent node of the node to be created (optional)

    Returns:
        dict of the form ``{nodename: {"id": node IRI, "nodes": {...}}}`` with the created list nodes, nested according to their hierarchy structure
        True if all nodes could be created, False if any node could not be created
    """
    new_node = ListNode(
        con=con,
        project=project,
        label=node["labels"],
        comments=node.get("comments"),
        name=node["name"],
        parent=parent_node
    )
    try:
        new_node = try_network_action(
            action=lambda: new_node.create(),
            failure_msg=f"ERROR while trying to create list node '{node['name']}'."
        )
    except BaseError as err:
        print(err.message)
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
        return {new_node.name: {"id": new_node.id, "nodes": subnode_list}}, overall_success
    else:
        return {new_node.name: {"id": new_node.id}}, True


def create_lists(
    server: str,
    user: str,
    password: str,
    project_definition: Optional[dict[str, Any]] = None,
    input_file: Optional[str] = None,
    dump: bool = False
) -> Tuple[dict[str, Any], bool]:
    """
    This method uploads the "lists" section of a JSON project definition file to a DSP server. If the JSON project file
    is still unparsed, this method parses it, expands the Excel sheets that are referenced, and validates it.
    The "lists" section of the parsed project definition is then uploaded to the DSP server. If a list with the same
    name is already existing in this project on the DSP server, this list is skipped.
    Returns a tuple consisting of a dict and a bool. The dict contains the IRIs of the created list nodes. If there are
    no lists in the project definition, an empty dictionary is returned. The bool indicates if everything went smoothly
    during the process. If a warning or error occurred (e.g. one of the lists already exists, or one of the nodes could
    not be created), it is False.

    Args:
        input_file: path to the JSON project file (will be validated, and Excel file references will be expanded)
        project_definition: parsed JSON project file (must be valid, and the Excel file references must be expanded already)
        server: URL of the DSP server
        user: Username (e-mail) for the DSP server, must have the permissions to create a project
        password: Password of the user
        dump: if True, the request is dumped as JSON (used for testing)

    Returns:
        dict of the form ``{nodename: {"id": IRI, "nodes": {...}}}`` with the created list nodes, nested according to their hierarchy structure
        True if everything went smoothly, False if a warning or error occurred
    """
    overall_success = True

    if project_definition and not input_file:
        # the "lists_to_create" can directly be taken from the "lists" section
        lists_to_create = project_definition["project"].get("lists")
        if not lists_to_create:
            return {}, True
    elif input_file and not project_definition:
        # the file must be parsed, potential Excel file references expanded, and then, the file must be validated.
        # Only then, the "lists_to_create" are in a safe state
        with open(input_file) as f:
            project_json_str = f.read()
        project_definition = json.loads(project_json_str)
        if not project_definition["project"].get("lists"):
            return {}, True
        lists_to_create, success = expand_lists_from_excel(project_definition["project"]["lists"])
        if not success:
            overall_success = False
        project_definition["project"]["lists"] = lists_to_create
        if validate_project(project_definition, expand_lists=False):
            print('JSON project file is syntactically correct and passed validation.')
    else:
        raise BaseError(f"ERROR: Must provide either project_definition or input_file. It's not possible to provide "
                        f"neither of them or both of them.")

    # connect to the DSP server
    con = login(server, user, password)
    if dump:
        con.start_logging()

    # retrieve the project
    project_local = Project(con=con, shortcode=project_definition["project"]["shortcode"])
    project_remote = try_network_action(
        action=lambda: project_local.read(),
        failure_msg="ERROR while trying to create the lists: Project couldn't be read from the DSP server."
    )

    # retrieve existing lists
    try:
        existing_lists: list[ListNode] = try_network_action(
            action=lambda: ListNode.getAllLists(con=con, project_iri=project_remote.id),
            failure_msg="WARNING: Unable to retrieve existing lists on DSP server. Cannot check if your lists are "
                        "already existing."
        )
    except BaseError as err:
        print(err.message)
        existing_lists = []
        overall_success = False

    # create new lists
    current_project_lists = {}
    for new_list in lists_to_create:
        # if list exists already, add it to "current_project_lists" (for later usage), then skip it
        existing_list = [x for x in existing_lists if x.project == project_remote.id and x.name == new_list["name"]]
        if existing_list:
            current_project_lists[existing_list[0].name] = {"id": existing_list[0].id, "nodes": new_list["nodes"]}
            print(f"\tWARNING: List '{new_list['name']}' already exists on the DSP server. Skipping...")
            overall_success = False
            continue

        created_list, success = _create_list_node(con=con, project=project_remote, node=new_list)
        current_project_lists.update(created_list)
        if not success:
            overall_success = False
        print(f"\tCreated list '{new_list['name']}'.")

    return current_project_lists, overall_success
