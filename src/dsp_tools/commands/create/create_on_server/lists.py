import warnings
from typing import Any

from loguru import logger
from tqdm import tqdm

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.list_client import ListCreateClient
from dsp_tools.clients.list_client_live import ListCreateClientLive
from dsp_tools.clients.list_client_live import ListGetClientLive
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import CreateProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.input_problems import UploadProblem
from dsp_tools.commands.create.models.input_problems import UserInformation
from dsp_tools.commands.create.models.input_problems import UserInformationMessage
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedListNode
from dsp_tools.commands.create.models.parsed_project import ParsedNodeInfo
from dsp_tools.commands.create.models.server_project_info import ListNameToIriLookup
from dsp_tools.error.custom_warnings import DspToolsUnexpectedStatusCodeWarning
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode
from dsp_tools.utils.ansi_colors import BOLD
from dsp_tools.utils.ansi_colors import BOLD_CYAN
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT


def create_lists(
    parsed_lists: list[ParsedList], shortcode: str, auth: AuthenticationClient, project_iri: str
) -> tuple[ListNameToIriLookup, CollectedProblems | None]:
    print(BOLD + "Processing list section:" + RESET_TO_DEFAULT)
    name2iri = get_existing_lists_on_server(shortcode, auth)
    if not parsed_lists:
        return name2iri, None
    lists_to_create, existing_info = _filter_out_existing_lists(parsed_lists, name2iri)
    if existing_info:
        _print_existing_list_info(existing_info)
    if not lists_to_create:
        msg = "    All lists defined in the project are already on the server, no list was uploaded."
        logger.warning(msg)
        print(BOLD_CYAN + msg + RESET_TO_DEFAULT)
        return name2iri, None

    create_client = ListCreateClientLive(auth.server, auth, project_iri)

    all_problems: list[CreateProblem] = []
    progress_bar = tqdm(lists_to_create, desc="    Creating lists", dynamic_ncols=True)
    for new_lst in progress_bar:
        list_iri, problems = _create_new_list(new_lst, create_client, project_iri)
        if list_iri is None:
            problems.extend(problems)
        else:
            name2iri.add_iri(new_lst.list_info.name, list_iri)

    create_problems = None
    if all_problems:
        create_problems = CollectedProblems("The following problems occurred during list creation:", all_problems)
    return name2iri, create_problems


def _print_existing_list_info(existing_lists: list[UserInformation]) -> None:
    lists = ", ".join([x.focus_object for x in existing_lists])
    msg = f"    The following lists already exist on the server and will be skipped: {lists}"
    logger.info(msg)
    print(BOLD_CYAN + msg + RESET_TO_DEFAULT)


def get_existing_lists_on_server(shortcode: str, auth: AuthenticationClient) -> ListNameToIriLookup:
    client = ListGetClientLive(auth.server, shortcode)
    try:
        name2iri_dict = client.get_all_list_iris_and_names()
        return ListNameToIriLookup(name2iri_dict)
    except FatalNonOkApiResponseCode as e:
        logger.exception(e)
        warnings.warn(
            DspToolsUnexpectedStatusCodeWarning(
                "Could not retrieve existing lists on server. "
                "We will not be able to create any properties that require a list that is not defined in the JSON."
            )
        )
        return ListNameToIriLookup({})


def _filter_out_existing_lists(
    parsed_lists: list[ParsedList], name2iri: ListNameToIriLookup
) -> tuple[list[ParsedList], list[UserInformation]]:
    lists_to_create: list[ParsedList] = []
    existing_info: list[UserInformation] = []

    for parsed_list in parsed_lists:
        if name2iri.check_list_exists(parsed_list.list_info.name):
            existing_info.append(
                UserInformation(parsed_list.list_info.name, UserInformationMessage.LIST_EXISTS_ON_SERVER)
            )
        else:
            lists_to_create.append(parsed_list)

    return lists_to_create, existing_info


def _create_new_list(
    parsed_list: ParsedList, create_client: ListCreateClient, project_iri: str
) -> tuple[str | None, list[UploadProblem]]:
    serialised = _serialise_list(parsed_list.list_info, project_iri)
    new_iri = create_client.create_new_list(serialised)

    if new_iri is None:
        problems: list[UploadProblem] = [
            UploadProblem(parsed_list.list_info.name, ProblemType.LIST_COULD_NOT_BE_CREATED)
        ]
        return None, problems

    node_problems = []
    if parsed_list.children:
        node_problems = _create_node_tree(parsed_list.children, new_iri, create_client, project_iri)

    return new_iri, node_problems


def _serialise_list(parsed_list_info: ParsedNodeInfo, project_iri: str) -> dict[str, Any]:
    node_dict = {
        "projectIri": project_iri,
        "name": parsed_list_info.name,
        "labels": _convert_to_api_format(parsed_list_info.labels),
    }
    if parsed_list_info.comments:
        node_dict["comments"] = _convert_to_api_format(parsed_list_info.comments)
    return node_dict


def _create_node_tree(
    nodes: list[ParsedListNode], parent_iri: str, create_client: ListCreateClient, project_iri: str
) -> list[UploadProblem]:
    problems: list[UploadProblem] = []

    for node in nodes:
        serialised = _serialise_node(node.node_info, parent_iri, project_iri)
        node_iri = create_client.add_list_node(serialised, parent_iri)
        if node_iri is None:
            problems.append(UploadProblem(node.node_info.name, ProblemType.LIST_NODE_COULD_NOT_BE_CREATED))
            continue

        if node.children:
            child_problems = _create_node_tree(node.children, node_iri, create_client, project_iri)
            problems.extend(child_problems)

    return problems


def _serialise_node(node_info: ParsedNodeInfo, parent_iri: str, project_iri: str) -> dict[str, Any]:
    node_dict = {
        "parentNodeIri": parent_iri,
        "projectIri": project_iri,
        "name": node_info.name,
        "labels": _convert_to_api_format(node_info.labels),
    }
    if node_info.comments:
        node_dict["comments"] = _convert_to_api_format(node_info.comments)
    return node_dict


def _convert_to_api_format(lang_dict: dict[str, str]) -> list[dict[str, str]]:
    return [{"value": value, "language": lang} for lang, value in lang_dict.items()]
