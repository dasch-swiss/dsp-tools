"""This module handles the ontology creation, update and upload to a DSP server. This includes the creation and update
of the project, the creation of groups, users, lists, resource classes, properties and cardinalities."""

from pathlib import Path
from typing import Any
from typing import cast

from dotenv import load_dotenv
from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.clients.group_user_clients_live import GroupClientLive
from dsp_tools.commands.create.communicate_problems import print_problem_collection
from dsp_tools.commands.create.create_on_server.group_users import create_groups
from dsp_tools.commands.create.create_on_server.group_users import create_users
from dsp_tools.commands.create.create_on_server.group_users import get_existing_group_to_iri_lookup
from dsp_tools.commands.create.create_on_server.lists import create_lists
from dsp_tools.commands.create.create_on_server.lists import get_existing_lists_on_server
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.commands.create.parsing.parse_project import parse_project
from dsp_tools.commands.project.create.parse_project import parse_project_json
from dsp_tools.commands.project.create.project_create_default_permissions import create_default_permissions
from dsp_tools.commands.project.create.project_create_ontologies import create_ontologies
from dsp_tools.commands.project.legacy_models.context import Context
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.commands.project.models.permissions_client import PermissionsClient
from dsp_tools.commands.project.models.project_definition import ProjectMetadata
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.legacy_models.langstring import LangString
from dsp_tools.utils.ansi_colors import BOLD
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.json_parsing import parse_json_input

load_dotenv()


def create_project(  # noqa: PLR0915,PLR0912 (too many statements & branches)
    project_file_as_path_or_parsed: str | Path | dict[str, Any],
    creds: ServerCredentials,
    verbose: bool = False,
) -> bool:
    """
    Creates a project from a JSON project file on a DSP server.
    A project must contain at least one ontology,
    and it may contain lists, users, and groups.
    Severe errors lead to a BaseError,
    while other errors are printed without interrupting the process.

    Args:
        project_file_as_path_or_parsed: path to the JSON project definition, or parsed JSON object
        creds: credentials to connect to the DSP server
        verbose: prints more information if set to True

    Raises:
        InputError:
          - if the project cannot be created
          - if the login fails
          - if an ontology cannot be created

        BaseError:
          - if the input is invalid
          - if an Excel file referenced in the "lists" section cannot be expanded
          - if the validation doesn't pass

    Returns:
        True if everything went smoothly, False if a warning or error occurred
    """

    knora_api_prefix = "knora-api:"
    overall_success = True

    # includes validation
    parsed_project = parse_project(project_file_as_path_or_parsed, creds.server)
    if not isinstance(parsed_project, ParsedProject):
        for problem in parsed_project:
            print_problem_collection(problem)
        return False

    # required for the legacy code
    project_json = parse_json_input(project_file_as_path_or_parsed=project_file_as_path_or_parsed)
    context = Context(project_json.get("prefixes", {}))
    legacy_project = parse_project_json(project_json)

    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)
    con = ConnectionLive(creds.server, auth)

    # create project on DSP server
    info_str = f"Create project '{legacy_project.metadata.shortname}' ({legacy_project.metadata.shortcode}):"
    print(BOLD + info_str + RESET_TO_DEFAULT)
    logger.info(info_str)
    project_remote, success = _create_project_on_server(
        project_definition=legacy_project.metadata,
        con=con,
    )
    project_iri = cast(str, project_remote.iri)
    project_iri_lookup = ProjectIriLookup(project_iri)
    if not success:
        overall_success = False

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
        con=con,
        context=context,
        knora_api_prefix=knora_api_prefix,
        list_name_2_iri=list_name_2_iri,
        ontology_definitions=legacy_project.ontologies,
        project_remote=project_remote,
        verbose=verbose,
        parsed_ontologies=parsed_project.ontologies,
        project_iri_lookup=project_iri_lookup,
        auth=auth,
    )
    if not success:
        overall_success = False

    # create the default permissions (DOAPs)
    perm_client = PermissionsClient(auth, str(project_remote.iri))
    success = create_default_permissions(
        perm_client,
        legacy_project.metadata.default_permissions,
        legacy_project.metadata.default_permissions_overrule,
        legacy_project.metadata.shortcode,
    )
    if not success:
        overall_success = False

    # final steps
    if overall_success:
        msg = (
            f"Successfully created project '{legacy_project.metadata.shortname}' "
            f"({legacy_project.metadata.shortcode}) with all its ontologies. "
            f"There were no problems during the creation process."
        )
        print(f"========================================================\n{msg}")
        logger.info(msg)
    else:
        msg = (
            f"The project '{legacy_project.metadata.shortname}' ({legacy_project.metadata.shortcode}) "
            f"with its ontologies could be created, "
            f"but during the creation process, some problems occurred. Please carefully check the console output."
        )
        print(f"========================================================\nWARNING: {msg}")
        logger.warning(msg)

    return overall_success


def _create_project_on_server(
    project_definition: ProjectMetadata,
    con: Connection,
) -> tuple[Project, bool]:
    """
    Create the project on the DSP server.
    If it already exists: update its longname, description, and keywords.

    Args:
        project_definition: object with information about the project
        con: connection to the DSP server

    Raises:
        InputError: if the project cannot be created on the DSP server

    Returns:
        a tuple of the remote project and the success status (True if everything went smoothly, False otherwise)
    """
    all_projects = Project.getAllProjects(con=con)
    if remote_project := next((x for x in all_projects if project_definition.shortcode == x.shortcode), None):
        msg = (
            f"The project with the shortcode '{project_definition.shortcode}' already exists on the server. "
            f"No changes were made to the project metadata. "
            f"Continue with the upload of lists and ontologies ..."
        )
        print(f"WARNING: {msg}")
        logger.warning(msg)
        return remote_project, False

    success = True
    project_local = Project(
        con=con,
        shortcode=project_definition.shortcode,
        shortname=project_definition.shortname,
        longname=project_definition.longname,
        description=LangString(project_definition.descriptions),  # type: ignore[arg-type]
        keywords=set(project_definition.keywords) if project_definition.keywords else None,
        enabled_licenses=set(project_definition.enabled_licenses) if project_definition.enabled_licenses else None,
        selfjoin=False,
        status=True,
    )
    try:
        project_remote = project_local.create()
    except BaseError:
        err_msg = (
            f"Cannot create project '{project_definition.shortname}' ({project_definition.shortcode}) on DSP server."
        )
        logger.exception(err_msg)
        raise InputError(err_msg) from None
    print(f"    Created project '{project_remote.shortname}' ({project_remote.shortcode}).")
    logger.info(f"Created project '{project_remote.shortname}' ({project_remote.shortcode}).")
    return project_remote, success
