"""This module handles the ontology creation, update and upload to a DSP server. This includes the creation and update
of the project, the creation of groups, users, lists, resource classes, properties and cardinalities."""

from pathlib import Path
from typing import Any

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.commands.project.create.parse_project import parse_project_json
from dsp_tools.commands.project.create.project_create_lists import create_lists_on_server
from dsp_tools.commands.project.create.project_create_ontologies import create_ontologies
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.commands.project.legacy_models.context import Context
from dsp_tools.commands.project.legacy_models.group import Group
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.commands.project.legacy_models.user import User
from dsp_tools.commands.project.models.project_definition import ProjectMetadata
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.legacy_models.langstring import LangString
from dsp_tools.utils.json_parsing import parse_json_input


def create_project(
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

    project_json = parse_json_input(project_file_as_path_or_parsed=project_file_as_path_or_parsed)

    context = Context(project_json.get("prefixes", {}))

    # validate against JSON schema
    validate_project(project_json)
    print("    JSON project file is syntactically correct and passed validation.")
    logger.info("JSON project file is syntactically correct and passed validation.")

    project = parse_project_json(project_json)

    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)
    con = ConnectionLive(creds.server, auth)

    # create project on DSP server
    info_str = f"Create project '{project.metadata.shortname}' ({project.metadata.shortcode})..."
    print(info_str)
    logger.info(info_str)
    project_remote, success = _create_project_on_server(
        project_definition=project.metadata,
        con=con,
    )
    if not success:
        overall_success = False

    # create the lists
    names_and_iris_of_list_nodes: dict[str, Any] = {}
    if project.lists:
        print("Create lists...")
        logger.info("Create lists...")
        names_and_iris_of_list_nodes, success = create_lists_on_server(
            lists_to_create=project.lists,
            con=con,
            project_remote=project_remote,
        )
        if not success:
            overall_success = False

    # create the groups
    current_project_groups: dict[str, Group] = {}
    if project.groups:
        print("Create groups...")
        logger.info("Create groups...")
        current_project_groups, success = _create_groups(
            con=con,
            groups=project.groups,
            project=project_remote,
        )
        if not success:
            overall_success = False

    # create or update the users
    if project.users:
        print("Create users...")
        logger.info("Create users...")
        success = _create_users(
            con=con,
            users_section=project.users,
            current_project_groups=current_project_groups,
            current_project=project_remote,
            verbose=verbose,
        )
        if not success:
            overall_success = False

    # create the ontologies
    success = create_ontologies(
        con=con,
        context=context,
        knora_api_prefix=knora_api_prefix,
        names_and_iris_of_list_nodes=names_and_iris_of_list_nodes,
        ontology_definitions=project.ontologies,
        project_remote=project_remote,
        verbose=verbose,
    )
    if not success:
        overall_success = False

    # final steps
    if overall_success:
        msg = (
            f"Successfully created project '{project.metadata.shortname}' "
            f"({project.metadata.shortcode}) with all its ontologies. "
            f"There were no problems during the creation process."
        )
        print(f"========================================================\n{msg}")
        logger.info(msg)
    else:
        msg = (
            f"The project '{project.metadata.shortname}' ({project.metadata.shortcode}) "
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
    if project_definition.shortcode in [proj.shortcode for proj in all_projects]:
        msg = (
            f"The project with the shortcode '{project_definition.shortcode}' already exists on the server.\n"
            f"No changes were made to the project metadata.\n"
            f"Continue with the upload of lists and ontologies ..."
        )
        print(f"WARNING: {msg}")
        logger.warning(msg)

    success = True
    project_local = Project(
        con=con,
        shortcode=project_definition.shortcode,
        shortname=project_definition.shortname,
        longname=project_definition.longname,
        description=LangString(project_definition.descriptions),  # type: ignore[arg-type]
        keywords=set(project_definition.keywords) if project_definition.keywords else None,
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


def _create_groups(
    con: Connection,
    groups: list[dict[str, str]],
    project: Project,
) -> tuple[dict[str, Group], bool]:
    """
    Creates groups on a DSP server from the "groups" section of a JSON project file. If a group cannot be created, it is
    skipped and a warning is printed, but such a group will still be part of the returned dict.
    Returns a tuple consisting of a dict and a bool. The dict contains the groups that have successfully been created
    (or already exist). The bool indicates if everything went smoothly during the process. If a warning or error
    occurred, it is False.

    Args:
        con: connection instance to connect to the DSP server
        groups: "groups" section of a parsed JSON project file
        project: Project the group(s) should be added to (must exist on DSP server)

    Returns:
        A tuple consisting of a dict and the success status.
        The dict has the form ``{group name: group object}``
        for all groups that have successfully been created (or already exist).
        The dict is empty if no group was created.
    """
    overall_success = True
    current_project_groups: dict[str, Group] = {}
    try:
        remote_groups = Group.getAllGroupsForProject(con=con, proj_iri=str(project.iri))
    except BaseError:
        err_msg = (
            "Unable to check if group names are already existing on DSP server, because it is "
            "not possible to retrieve the remote groups from the DSP server."
        )
        print(f"WARNING: {err_msg}")
        logger.exception(err_msg)
        remote_groups = []
        overall_success = False

    for group in groups:
        group_name = group["name"]

        # if the group already exists, add it to "current_project_groups" (for later usage), then skip it
        if remotely_existing_group := [g for g in remote_groups if g.name == group_name]:
            current_project_groups[group_name] = remotely_existing_group[0]
            err_msg = f"Group name '{group_name}' already exists on the DSP server. Skipping..."
            print(f"    WARNING: {err_msg}")
            logger.warning(err_msg)
            overall_success = False
            continue

        # create the group
        group_local = Group(
            con=con,
            name=group_name,
            descriptions=LangString(group["descriptions"]),
            project=project,
            status=bool(group.get("status", True)),
            selfjoin=bool(group.get("selfjoin", False)),
        )
        try:
            group_remote: Group = group_local.create()
        except BaseError:
            err_msg = "Unable to create group '{group_name}'."
            print(f"    WARNING: {err_msg}")
            logger.exception(err_msg)
            overall_success = False
            continue

        current_project_groups[str(group_remote.name)] = group_remote
        print(f"    Created group '{group_name}'.")
        logger.info(f"Created group '{group_name}'.")

    return current_project_groups, overall_success


def _create_users(
    con: Connection,
    users_section: list[dict[str, str]],
    current_project_groups: dict[str, Group],
    current_project: Project,
    verbose: bool,
) -> bool:
    """
    Creates users on a DSP server from the "users" section of a JSON project file.
    If a user cannot be created, a warning is printed and the user is skipped.

    Args:
        con: connection instance to connect to the DSP server
        users_section: "users" section of a parsed JSON project file
        current_project_groups: groups defined in the current project, in the form ``{group name: group object}``
            (must exist on DSP server)
        current_project: "project" object of the current project (must exist on DSP server)
        verbose: Prints more information if set to True

    Returns:
        True if all users could be created without any problems. False if a warning/error occurred.
    """
    overall_success = True
    for json_user_definition in users_section:
        username = json_user_definition["username"]

        # skip the user if he already exists
        all_users = User.getAllUsers(con)
        if json_user_definition["email"] in [user.email for user in all_users]:
            err_msg = (
                f"User '{username}' already exists on the DSP server.\n"
                f"Please manually add this user to the project in DSP-APP."
            )
            print(f"    WARNING: {err_msg}")
            logger.warning(err_msg)
            overall_success = False
            continue
        # add user to the group(s)
        group_iris, sysadmin, success = _get_group_iris_for_user(
            json_user_definition=json_user_definition,
            current_project=current_project,
            current_project_groups=current_project_groups,
            con=con,
            verbose=verbose,
        )
        if not success:
            overall_success = False

        # add user to the project(s)
        project_info, success = _get_projects_where_user_is_admin(
            json_user_definition=json_user_definition,
            current_project=current_project,
            con=con,
            verbose=verbose,
        )
        if not success:
            overall_success = False

        # create the user
        user_local = User(
            con=con,
            username=json_user_definition["username"],
            email=json_user_definition["email"],
            givenName=json_user_definition["givenName"],
            familyName=json_user_definition["familyName"],
            password=json_user_definition["password"],
            status=bool(json_user_definition.get("status", True)),
            lang=json_user_definition.get("lang", "en"),
            sysadmin=sysadmin,
            in_projects=project_info,
            in_groups=group_iris,
        )
        try:
            user_local.create()
        except BaseError:
            print(f"    WARNING: Unable to create user '{username}'.")
            logger.exception(f"Unable to create user '{username}'.")
            overall_success = False
            continue
        print(f"    Created user '{username}'.")
        logger.info(f"Created user '{username}'.")

    return overall_success


def _get_group_iris_for_user(
    json_user_definition: dict[str, str],
    current_project: Project,
    current_project_groups: dict[str, Group],
    con: Connection,
    verbose: bool,
) -> tuple[set[str], bool, bool]:
    """
    Retrieve the IRIs of the groups that the user belongs to.

    Args:
        json_user_definition: the section of the JSON file that defines a user
        current_project: the Project object
        current_project_groups: dict of the form ``{group name: group object}``
            with the groups that exist on the DSP server
        con: connection to the DSP server
        verbose: verbose switch

    Returns:
        a tuple consisting of the group IRIs,
        the system admin status (True if the user is sysadmin, False otherwise),
        and the success status (True if everything went well)

    Raises:
        BaseError: if no groups can be retrieved from the DSP server, or if the retrieved group has no IRI
    """
    success = True
    username = json_user_definition["username"]
    group_iris: set[str] = set()
    sysadmin = False
    remote_groups: list[Group] = []
    for full_group_name in json_user_definition.get("groups", []):
        # full_group_name has the form '[project_shortname]:group_name' or 'SystemAdmin'
        inexisting_group_msg = (
            f"User {username} cannot be added to group {full_group_name}, because such a group doesn't exist."
        )
        if ":" not in full_group_name and full_group_name != "SystemAdmin":
            print(f"    WARNING: {inexisting_group_msg}")
            logger.warning(inexisting_group_msg)
            success = False
            continue

        if full_group_name == "SystemAdmin":
            sysadmin = True
            if verbose:
                print(f"    Added user '{username}' to group 'SystemAdmin'.")
            logger.info(f"Added user '{username}' to group 'SystemAdmin'.")
            continue

        # all other cases (":" in full_group_name)
        project_shortname, group_name = full_group_name.split(":")
        if not project_shortname:
            # full_group_name refers to a group inside the same project
            if group_name not in current_project_groups:
                print(f"    WARNING: {inexisting_group_msg}")
                logger.warning(inexisting_group_msg)
                success = False
                continue
            group = current_project_groups[group_name]
        else:
            # full_group_name refers to an already existing group on DSP
            try:
                # "remote_groups" might be available from a previous loop cycle
                remote_groups = remote_groups or Group.getAllGroups(con=con)
            except BaseError:
                err_msg = (
                    f"User '{username}' is referring to the group {full_group_name} that "
                    f"exists on the DSP server, but no groups could be retrieved from the DSP server."
                )
                print(f"    WARNING: {err_msg}")
                logger.exception(err_msg)
                success = False
                continue
            existing_group = [g for g in remote_groups if g.project == current_project.iri and g.name == group_name]
            if not existing_group:
                print(f"    WARNING: {inexisting_group_msg}")
                logger.warning(inexisting_group_msg)
                success = False
                continue
            group = existing_group[0]

        if not group.iri:
            raise BaseError(f"Group '{group}' has no IRI.")
        group_iris.add(group.iri)
        if verbose:
            print(f"    Added user '{username}' to group '{full_group_name}'.")
        logger.info(f"Added user '{username}' to group '{full_group_name}'.")

    return group_iris, sysadmin, success


def _get_projects_where_user_is_admin(
    json_user_definition: dict[str, str],
    current_project: Project,
    con: Connection,
    verbose: bool,
) -> tuple[dict[str, bool], bool]:
    """
    Create a dict that tells for every project if the user is administrator in that project or not.

    Args:
        json_user_definition: the section of the JSON file that defines a user
        current_project: the Project object
        con: connection to the DSP server
        verbose: verbose switch

    Returns:
        a tuple consisting of a dict in the form {project IRI: isAdmin}, and the success status
    """
    success = True
    username = json_user_definition["username"]
    project_info: dict[str, bool] = {}
    remote_projects: list[Project] = []
    for full_project_name in json_user_definition.get("projects", []):
        # full_project_name has the form '[project_name]:member' or '[project_name]:admin'
        if ":" not in full_project_name:
            err_msg = "Provided project '{full_project_name}' for user '{username}' is not valid. Skipping..."
            print(f"    WARNING: {err_msg}")
            logger.warning(err_msg)
            success = False
            continue

        project_name, project_role = full_project_name.split(":")
        if not project_name:
            # full_project_name refers to the current project
            in_project = current_project
        else:
            # full_project_name refers to an already existing project on DSP
            try:
                # "remote_projects" might be available from a previous loop cycle
                remote_projects = remote_projects or current_project.getAllProjects(con=con)
            except BaseError:
                err_msg = (
                    f"User '{username}' cannot be added to the projects {json_user_definition['projects']} "
                    f"because the projects cannot be retrieved from the DSP server."
                )
                print(f"    WARNING: {err_msg}")
                logger.exception(err_msg)
                success = False
                continue
            in_project_list = [p for p in remote_projects if p.shortname == project_name]
            if not in_project_list:
                msg = f"Provided project '{full_project_name}' for user '{username}' is not valid. Skipping..."
                print(f"    WARNING: {msg}")
                logger.warning(msg)
                success = False
                continue
            in_project = in_project_list[0]

        is_admin = project_role == "admin"
        match project_info.get(str(in_project.iri)):
            case None:  # user hasn't yet been registered as admin/member of this project
                project_info[str(in_project.iri)] = is_admin
            case True:  # user has already been registered as **admin** of this project
                pass  # leave previous admin/member status untouched
            case False:  # user has already been registered as **member** of this project
                project_info[str(in_project.iri)] = is_admin  # overwrite previous admin/member status
        if verbose:
            print(f"    Added user '{username}' as {project_role} to project '{in_project.shortname}'.")
        logger.info(f"Added user '{username}' as {project_role} to project '{in_project.shortname}'.")

    return project_info, success
