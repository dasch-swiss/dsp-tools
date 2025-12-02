from pathlib import Path
from typing import Any

from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.group_user_clients_live import GroupClientLive
from dsp_tools.commands.create.communicate_problems import print_problem_collection
from dsp_tools.commands.create.create_on_server.complete_ontologies import create_ontologies
from dsp_tools.commands.create.create_on_server.group_users import create_groups
from dsp_tools.commands.create.create_on_server.group_users import create_users
from dsp_tools.commands.create.create_on_server.group_users import get_existing_group_to_iri_lookup
from dsp_tools.commands.create.create_on_server.lists import create_lists
from dsp_tools.commands.create.create_on_server.lists import get_existing_lists_on_server
from dsp_tools.commands.create.create_on_server.project import create_project
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.parsing.parse_project import parse_project
from dsp_tools.commands.project.create.project_create_default_permissions import create_default_permissions
from dsp_tools.commands.project.models.permissions_client import PermissionsClient

load_dotenv(dotenv_path=find_dotenv(usecwd=True))


def create(  # noqa: PLR0912 (Too many branches)
    project_file_as_path_or_parsed: str | Path | dict[str, Any],
    creds: ServerCredentials,
) -> bool:
    overall_success = True

    # includes validation
    parsed_project = parse_project(project_file_as_path_or_parsed, creds.server)
    if not isinstance(parsed_project, ParsedProject):
        for problem in parsed_project:
            print_problem_collection(problem)
        return False

    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)

    # create project
    project_iri = create_project(parsed_project.project_metadata, auth)

    # create the lists
    if parsed_project.lists:
        list_name_2_iri, list_problems = create_lists(
            parsed_lists=parsed_project.lists,
            shortcode=parsed_project.project_metadata.shortcode,
            auth=auth,
            project_iri=project_iri,
        )
        if list_problems:
            overall_success = False
            print_problem_collection(list_problems)
    else:
        list_name_2_iri = get_existing_lists_on_server(parsed_project.project_metadata.shortcode, auth)

    # create the groups
    group_client = GroupClientLive(creds.server, auth)
    group_lookup = get_existing_group_to_iri_lookup(
        group_client, project_iri, parsed_project.project_metadata.shortname
    )
    if parsed_project.groups:
        group_lookup, group_problems = create_groups(
            groups=parsed_project.groups,
            group_client=group_client,
            project_iri=project_iri,
            group_lookup=group_lookup,
        )
        if group_problems:
            print_problem_collection(group_problems)
            overall_success = False

    if parsed_project.users:
        user_problems = create_users(
            users=parsed_project.users,
            user_memberships=parsed_project.user_memberships,
            group_lookup=group_lookup,
            auth=auth,
            project_iri=project_iri,
        )
        if user_problems:
            print_problem_collection(user_problems)
            overall_success = False

    # create the ontologies
    success = create_ontologies(
        parsed_ontologies=parsed_project.ontologies,
        list_name_2_iri=list_name_2_iri,
        project_iri=project_iri,
        shortcode=parsed_project.project_metadata.shortcode,
        auth=auth,
    )
    if not success:
        overall_success = False

    # create the default permissions (DOAPs)
    perm_client = PermissionsClient(auth, project_iri)
    success = create_default_permissions(
        perm_client=perm_client,
        default_permissions=parsed_project.permissions.default_permissions,
        default_permissions_overrule=parsed_project.permissions.default_permissions_overrule,
        shortcode=parsed_project.project_metadata.shortcode,
    )
    if not success:
        overall_success = False

    # final steps
    if overall_success:
        msg = (
            f"Successfully created project '{parsed_project.project_metadata.shortname}' "
            f"({parsed_project.project_metadata.shortcode}) with all its ontologies. "
            f"There were no problems during the creation process."
        )
        print(f"========================================================\n{msg}")
        logger.info(msg)
    else:
        msg = (
            f"The project '{parsed_project.project_metadata.shortname}' ({parsed_project.project_metadata.shortcode}) "
            f"with its ontologies could be created, "
            f"but during the creation process, some problems occurred. Please carefully check the console output."
        )
        print(f"========================================================\nWARNING: {msg}")
        logger.warning(msg)

    return overall_success
