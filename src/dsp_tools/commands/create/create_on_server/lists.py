from typing import Any

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.list_client import ListCreateClient
from dsp_tools.clients.list_client_live import ListCreateClientLive
from dsp_tools.clients.list_client_live import ListGetClientLive
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.input_problems import UploadProblem
from dsp_tools.commands.create.models.input_problems import UserInformation
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedListNode
from dsp_tools.commands.create.models.parsed_project import ParsedNodeInfo
from dsp_tools.commands.create.models.server_project_info import ListNameToIriLookup


def create_lists(
    parsed_lists: list[ParsedList], shortcode: str, auth: AuthenticationClient
) -> tuple[ListNameToIriLookup, CollectedProblems | None]:
    name2iri = _get_existing_lists_on_server(shortcode, auth)
    lists_to_create, existing_info = _filter_out_existing_lists(parsed_lists, name2iri)
    # todo: print out information
    problems = []
    create_client = ListCreateClientLive(
        auth.server,
        auth,
    )  # TODO: get project IRI
    for new_lst in lists_to_create:
        result = _create_new_list(new_lst, create_client)
        if isinstance(result, UploadProblem):
            problems.append(result)
        else:
            name2iri.add_iri(new_lst.list_info.name, result)
    create_problems = None
    if problems:
        create_problems = CollectedProblems("The following lists could not be created:", problems)
    return name2iri, create_problems


def _get_existing_lists_on_server(shortcode: str, auth: AuthenticationClient) -> ListNameToIriLookup:
    client = ListGetClientLive(auth.server, shortcode)
    # TODO: modify client route to get list names and iris for model


def _filter_out_existing_lists(
    parsed_lists: list[ParsedList], name2iri: ListNameToIriLookup
) -> tuple[list[ParsedList], list[UserInformation]]:
    pass
    # TODO: remove lists that exist


def _create_new_list(parsed_list: ParsedList, create_client: ListCreateClient) -> str | UploadProblem:
    """

    Required permission: SystemAdmin / ProjectAdmin
    Required fields: projectIri, labels, comments
    POST: /admin/lists
    BODY:

    {
        "projectIri": "someprojectiri",
        "labels": [{ "value": "New list", "language": "en"}],
        "comments": []
    }
    """
    # TODO: make serialisation function
    serialised = _serialise_list(parsed_list)
    new_iri = create_client.create_new_list(serialised)
    if not new_iri:
        return UploadProblem(parsed_list.list_info.name, ProblemType.LIST_COULD_NOT_BE_CREATED)
    _create_all_children(parsed_list.children, new_iri, create_client)
    return new_iri


def _serialise_list(parsed_list: ParsedList) -> dict[str, Any]:
    # TODO: implement code
    """{
        "labels": [{ "value": "New list", "language": "en"}],
        "comments": []
    }"""
    return {}


def _create_all_children(parsed_nodes: list[ParsedListNode], parent_iri: str, create_client: ListCreateClient) -> None:
    result = _create_child_nodes(parsed_nodes, parent_iri, create_client)
    if isinstance(result, UploadProblem):
        pass  # TODO: print info


def _create_child_nodes(
    parsed_nodes: list[ParsedListNode], parent_iri: str, create_client: ListCreateClient
) -> str | UploadProblem:
    for node in parsed_nodes:
        result = _add_one_child(node.node_info, parent_iri, create_client)
        if isinstance(result, UploadProblem):
            return result
        if node.children:
            _create_child_nodes(node.children, result, create_client)  # TODO: check if recursiveness works


def _add_one_child(node_info: ParsedNodeInfo, parent_iri: str, create_client: ListCreateClient) -> str | UploadProblem:
    serialised = _serialise_node(node_info, parent_iri)
    result = create_client.add_list_node(serialised)
    if not result:
        return UploadProblem(node_info.name, ProblemType.LIST_NODE_COULD_NOT_BE_CREATED)
    return result


def _serialise_node(node_info: ParsedNodeInfo, parent_iri: str) -> dict[str, Any]:
    """
        Required fields: parentNodeIri, projectIri, labels,
    Appends a new child node under the supplied nodeIri. If the supplied nodeIri is the listIri, then a new child node is appended to the top level. If a position is given for the new child node, the node will be created and inserted in the specified position, otherwise the node is appended to the end of parent's children.
    POST: /admin/lists/<parentNodeIri>
    BODY:

     {
     # parentNodeIri can be list IRI or node IRI
         "parentNodeIri": "http://rdfh.ch/lists/0001/yWQEGXl53Z4C4DYJ-S2c5A",
         "projectIri": "http://rdfh.ch/projects/0001",
         "name": "a child",
         "labels": [{ "value": "New List Node", "language": "en"}]
    }
    """
    return {}
