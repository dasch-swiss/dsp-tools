"""This module handles the ontology creation, update and upload to a DSP server. This includes the creation and update
of the project, the creation of groups, users, lists, resource classes, properties and cardinalities."""

import contextlib
from pathlib import Path
from typing import Any, Optional, Union, cast

import regex

from dsp_tools.commands.excel2json.lists import expand_lists_from_excel
from dsp_tools.commands.project.create.project_create_lists import create_lists_on_server
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.commands.project.models.group import Group
from dsp_tools.commands.project.models.ontology import Ontology
from dsp_tools.commands.project.models.project import Project
from dsp_tools.commands.project.models.propertyclass import PropertyClass
from dsp_tools.commands.project.models.resourceclass import ResourceClass
from dsp_tools.commands.project.models.user import User
from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.models.helpers import Cardinality, Context, DateTimeStamp
from dsp_tools.models.langstring import LangString
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import login, parse_json_input, try_network_action

logger = get_logger(__name__)


def _create_project_on_server(
    shortcode: str,
    shortname: str,
    longname: str,
    descriptions: Optional[dict[str, str]],
    keywords: Optional[list[str]],
    con: Connection,
    verbose: bool,
) -> tuple[Project, bool]:
    """
    Create the project on the DSP server.
    If it already exists: update its longname, description and keywords.

    Args:
        shortcode: shortcode of the project
        shortname: shortname of the project
        longname: longname of the project
        descriptions: descriptions of the project in different languages
        keywords: keywords of the project
        con: connection to the DSP server
        verbose: verbose switch

    Raises:
        UserError: if the project cannot be created on the DSP server

    Returns:
        a tuple of the remote project and the success status (True if everything went smoothly, False otherwise)
    """
    with contextlib.suppress(BaseError):
        # the normal, expected case is that this block fails
        project_local = Project(con=con, shortcode=shortcode)
        project_remote: Project = try_network_action(project_local.read)
        proj_designation = f"'{project_remote.shortname}' ({project_remote.shortcode})"
        msg = f"Project {proj_designation} already exists on the DSP server. Updating it..."
        print(f"\tWARNING: {msg}")
        logger.warning(msg)
        # try to update the basic info
        project_remote, _ = _update_basic_info_of_project(
            project=project_remote,
            shortcode=shortcode,
            shortname=shortname,
            longname=longname,
            descriptions=descriptions,
            keywords=keywords,
            verbose=verbose,
        )
        # It doesn't matter if the update is successful or not: continue anyway, because success is anyways false.
        # There are other things from this file that can be created on the server,
        # e.g. the groups and users, so the process must continue.
        return project_remote, False

    success = True
    project_local = Project(
        con=con,
        shortcode=shortcode,
        shortname=shortname,
        longname=longname,
        description=LangString(descriptions),  # type: ignore[arg-type]
        keywords=set(keywords) if keywords else None,
        selfjoin=False,
        status=True,
    )
    try:
        project_remote = try_network_action(project_local.create)
    except BaseError:
        err_msg = f"Cannot create project '{shortname}' ({shortcode}) on DSP server."
        logger.error(err_msg, exc_info=True)
        raise UserError(err_msg) from None
    print(f"\tCreated project '{project_remote.shortname}' ({project_remote.shortcode}).")
    logger.info(f"Created project '{project_remote.shortname}' ({project_remote.shortcode}).")
    return project_remote, success


def _update_basic_info_of_project(
    project: Project,
    shortcode: str,
    shortname: str,
    longname: str,
    descriptions: Optional[dict[str, str]],
    keywords: Optional[list[str]],
    verbose: bool,
) -> tuple[Project, bool]:
    """
    Updates the longname, description and keywords of a project on a DSP server.
    Returns the updated project (or the unchanged project if not successful)
    and a boolean saying if the update was successful or not.
    If the update was not successful, an error message is printed to stdout.

    Args:
        project: the project to be updated (must exist on the DSP server)
        shortcode: shortcode of the project (must be the same as in the existing project)
        shortname: shortname of the project (must be the same as in the existing project)
        longname: longname of the project
        descriptions: descriptions of the project in different languages
        keywords: keywords of the project
        verbose: verbose switch

    Returns:
        tuple of (updated project, success status)
    """

    # update the local "project" object
    project.longname = longname
    project.description = LangString(descriptions)  # type: ignore[arg-type]
    project.keywords = set(keywords) if keywords else set()

    # make the call to DSP-API
    try:
        project_remote: Project = try_network_action(project.update)
        if verbose:
            print(f"\tUpdated project '{shortname}' ({shortcode}).")
        logger.info(f"Updated project '{shortname}' ({shortcode}).")
        return project_remote, True
    except BaseError:
        print(f"WARNING: Could not update project '{shortname}' ({shortcode}).")
        logger.warning(f"Could not update project '{shortname}' ({shortcode}).", exc_info=True)
        return project, False


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
        remote_groups: list[Group] = try_network_action(
            lambda: Group.getAllGroupsForProject(con=con, proj_iri=str(project.iri))
        )
    except BaseError:
        err_msg = (
            "Unable to check if group names are already existing on DSP server, because it is "
            "not possible to retrieve the remote groups from the DSP server."
        )
        print(f"WARNING: {err_msg}")
        logger.warning(err_msg, exc_info=True)
        remote_groups = []
        overall_success = False

    for group in groups:
        group_name = group["name"]

        # if the group already exists, add it to "current_project_groups" (for later usage), then skip it
        if remotely_existing_group := [g for g in remote_groups if g.name == group_name]:
            current_project_groups[group_name] = remotely_existing_group[0]
            print(f"\tWARNING: Group name '{group_name}' already exists on the DSP server. Skipping...")
            logger.warning(f"Group name '{group_name}' already exists on the DSP server. Skipping...")
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
            group_remote: Group = try_network_action(group_local.create)
        except BaseError:
            print(f"\tWARNING: Unable to create group '{group_name}'.")
            logger.warning(f"Unable to create group '{group_name}'.", exc_info=True)
            overall_success = False
            continue

        current_project_groups[str(group_remote.name)] = group_remote
        print(f"\tCreated group '{group_name}'.")
        logger.info(f"Created group '{group_name}'.")

    return current_project_groups, overall_success


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
            print(f"\tWARNING: {inexisting_group_msg}")
            logger.warning(inexisting_group_msg)
            success = False
            continue

        if full_group_name == "SystemAdmin":
            sysadmin = True
            if verbose:
                print(f"\tAdded user '{username}' to group 'SystemAdmin'.")
            logger.info(f"Added user '{username}' to group 'SystemAdmin'.")
            continue

        # all other cases (":" in full_group_name)
        project_shortname, group_name = full_group_name.split(":")
        if not project_shortname:
            # full_group_name refers to a group inside the same project
            if group_name not in current_project_groups:
                print(f"\tWARNING: {inexisting_group_msg}")
                logger.warning(inexisting_group_msg)
                success = False
                continue
            group = current_project_groups[group_name]
        else:
            # full_group_name refers to an already existing group on DSP
            try:
                # "remote_groups" might be available from a previous loop cycle
                remote_groups = remote_groups or try_network_action(lambda: Group.getAllGroups(con=con))
            except BaseError:
                err_msg = (
                    f"User '{username}' is referring to the group {full_group_name} that "
                    f"exists on the DSP server, but no groups could be retrieved from the DSP server."
                )
                print(f"\tWARNING: {err_msg}")
                logger.warning(err_msg, exc_info=True)
                success = False
                continue
            existing_group = [g for g in remote_groups if g.project == current_project.iri and g.name == group_name]
            if not existing_group:
                print(f"\tWARNING: {inexisting_group_msg}")
                logger.warning(inexisting_group_msg)
                success = False
                continue
            group = existing_group[0]

        if not group.iri:
            raise BaseError(f"Group '{group}' has no IRI.")
        group_iris.add(group.iri)
        if verbose:
            print(f"\tAdded user '{username}' to group '{full_group_name}'.")
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
            print(f"\tWARNING: Provided project '{full_project_name}' for user '{username}' is not valid. Skipping...")
            logger.warning(f"Provided project '{full_project_name}' for user '{username}' is not valid. Skipping...")
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
                remote_projects = remote_projects or try_network_action(lambda: current_project.getAllProjects(con=con))
            except BaseError:
                err_msg = (
                    f"User '{username}' cannot be added to the projects {json_user_definition['projects']} "
                    f"because the projects cannot be retrieved from the DSP server."
                )
                print(f"\tWARNING: {err_msg}")
                logger.warning(err_msg, exc_info=True)
                success = False
                continue
            in_project_list = [p for p in remote_projects if p.shortname == project_name]
            if not in_project_list:
                msg = f"Provided project '{full_project_name}' for user '{username}' is not valid. Skipping..."
                print(f"\tWARNING: {msg}")
                logger.warning(msg)
                success = False
                continue
            in_project = in_project_list[0]

        is_admin = project_role == "admin"
        project_info[str(in_project.iri)] = is_admin
        if verbose:
            print(f"\tAdded user '{username}' as {project_role} to project '{in_project.shortname}'.")
        logger.info(f"Added user '{username}' as {project_role} to project '{in_project.shortname}'.")

    return project_info, success


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
        with contextlib.suppress(BaseError):
            # the normal case is that this block fails
            try_network_action(User(con, email=json_user_definition["email"]).read)
            print(f"\tWARNING: User '{username}' already exists on the DSP server. Skipping...")
            logger.warning(f"User '{username}' already exists on the DSP server. Skipping...")
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
            try_network_action(user_local.create)
        except BaseError:
            print(f"\tWARNING: Unable to create user '{username}'.")
            logger.warning(f"Unable to create user '{username}'.", exc_info=True)
            overall_success = False
            continue
        print(f"\tCreated user '{username}'.")
        logger.info(f"Created user '{username}'.")

    return overall_success


def _sort_resources(
    unsorted_resources: list[dict[str, Any]],
    onto_name: str,
) -> list[dict[str, Any]]:
    """
    This method sorts the resource classes in an ontology according to their inheritance order (parent classes first).

    Args:
        unsorted_resources: list of resources from a parsed JSON project file
        onto_name: name of the onto

    Returns:
        sorted list of resource classes
    """

    # do not modify the original unsorted_resources, which points to the original JSON project file
    resources_to_sort = unsorted_resources.copy()
    sorted_resources: list[dict[str, Any]] = []
    ok_resource_names: list[str] = []
    while resources_to_sort:
        # inside the for loop, resources_to_sort is modified, so a copy must be made to iterate over
        for res in resources_to_sort.copy():
            parent_classes = res["super"]
            if isinstance(parent_classes, str):
                parent_classes = [parent_classes]
            parent_classes = [regex.sub(r"^:([^:]+)$", f"{onto_name}:\\1", elem) for elem in parent_classes]
            parent_classes_ok = [not p.startswith(onto_name) or p in ok_resource_names for p in parent_classes]
            if all(parent_classes_ok):
                sorted_resources.append(res)
                res_name = f'{onto_name}:{res["name"]}'
                ok_resource_names.append(res_name)
                resources_to_sort.remove(res)
    return sorted_resources


def _sort_prop_classes(
    unsorted_prop_classes: list[dict[str, Any]],
    onto_name: str,
) -> list[dict[str, Any]]:
    """
    In case of inheritance, parent properties must be uploaded before their children. This method sorts the
    properties.

    Args:
        unsorted_prop_classes: list of properties from a parsed JSON project file
        onto_name: name of the onto

    Returns:
        sorted list of properties
    """

    # do not modify the original unsorted_prop_classes, which points to the original JSON project file
    prop_classes_to_sort = unsorted_prop_classes.copy()
    sorted_prop_classes: list[dict[str, Any]] = []
    ok_propclass_names: list[str] = []
    while prop_classes_to_sort:
        # inside the for loop, resources_to_sort is modified, so a copy must be made to iterate over
        for prop in prop_classes_to_sort.copy():
            prop_name = f'{onto_name}:{prop["name"]}'
            parent_classes = prop.get("super", "hasValue")
            if isinstance(parent_classes, str):
                parent_classes = [parent_classes]
            parent_classes = [regex.sub(r"^:([^:]+)$", f"{onto_name}:\\1", elem) for elem in parent_classes]
            parent_classes_ok = [not p.startswith(onto_name) or p in ok_propclass_names for p in parent_classes]
            if all(parent_classes_ok):
                sorted_prop_classes.append(prop)
                ok_propclass_names.append(prop_name)
                prop_classes_to_sort.remove(prop)
    return sorted_prop_classes


def _create_ontology(
    onto_name: str,
    onto_label: str,
    onto_comment: Optional[str],
    project_ontologies: list[Ontology],
    con: Connection,
    project_remote: Project,
    context: Context,
    verbose: bool,
) -> Optional[Ontology]:
    """
    Create an ontology on the DSP server,
    and add the prefixes defined in the JSON file to its context.
    If the ontology already exists on the DSP server, it is skipped.

    Args:
        onto_name: name of the ontology
        onto_label: label of the ontology
        onto_comment: comment of the ontology
        project_ontologies: ontologies existing on the DSP server
        con: Connection to the DSP server
        project_remote: representation of the project on the DSP server
        context: prefixes and the ontology IRIs they stand for
        verbose: verbose switch

    Raises:
        UserError: if the ontology cannot be created on the DSP server

    Returns:
        representation of the created ontology on the DSP server, or None if it already existed
    """
    # skip if it already exists on the DSP server
    if onto_name in [onto.name for onto in project_ontologies]:
        print(f"\tWARNING: Ontology '{onto_name}' already exists on the DSP server. Skipping...")
        logger.warning(f"Ontology '{onto_name}' already exists on the DSP server. Skipping...")
        return None

    print(f"Create ontology '{onto_name}'...")
    logger.info(f"Create ontology '{onto_name}'...")
    ontology_local = Ontology(
        con=con,
        project=project_remote,
        label=onto_label,
        name=onto_name,
        comment=onto_comment,
    )
    try:
        ontology_remote: Ontology = try_network_action(ontology_local.create)
    except BaseError:
        # if ontology cannot be created, let the error escalate
        logger.error(f"ERROR while trying to create ontology '{onto_name}'.", exc_info=True)
        raise UserError(f"ERROR while trying to create ontology '{onto_name}'.") from None

    if verbose:
        print(f"\tCreated ontology '{onto_name}'.")
    logger.info(f"Created ontology '{onto_name}'.")

    context.add_context(
        ontology_remote.name,
        ontology_remote.iri + ("" if ontology_remote.iri.endswith("#") else "#"),
    )

    # add the prefixes defined in the JSON file
    for onto_prefix, onto_info in context:
        if onto_info and str(onto_prefix) not in ontology_remote.context:
            onto_iri = onto_info.iri + ("#" if onto_info.hashtag else "")
            ontology_remote.context.add_context(prefix=str(onto_prefix), iri=onto_iri)

    return ontology_remote


def _create_ontologies(
    con: Connection,
    context: Context,
    knora_api_prefix: str,
    names_and_iris_of_list_nodes: dict[str, Any],
    ontology_definitions: list[dict[str, Any]],
    project_remote: Project,
    verbose: bool,
) -> bool:
    """
    Iterates over the ontologies in a JSON project file and creates the ontologies that don't exist on the DSP server
    yet. For every ontology, it first creates the resource classes, then the properties, and then adds the cardinalities
    to the resource classes.

    Args:
        con: Connection to the DSP server
        context: prefixes and the ontology IRIs they stand for
        knora_api_prefix: the prefix that stands for the knora-api ontology
        names_and_iris_of_list_nodes: IRIs of list nodes that were already created and are available on the DSP server
        ontology_definitions: the "ontologies" section of the parsed JSON project file
        project_remote: representation of the project on the DSP server
        verbose: verbose switch

    Raises:
        UserError if an error occurs during the creation of an ontology.
        All other errors are printed, the process continues, but the success status will be false.

    Returns:
        True if everything went smoothly, False otherwise
    """

    overall_success = True

    print("Create ontologies...")
    logger.info("Create ontologies...")
    try:
        project_ontologies: list[Ontology] = try_network_action(
            lambda: Ontology.getProjectOntologies(con=con, project_id=str(project_remote.iri))
        )
    except BaseError:
        err_msg = "Unable to retrieve remote ontologies. Cannot check if your ontology already exists."
        print("WARNING: {err_msg}")
        logger.warning(err_msg, exc_info=True)
        project_ontologies = []

    for ontology_definition in ontology_definitions:
        ontology_remote = _create_ontology(
            onto_name=ontology_definition["name"],
            onto_label=ontology_definition["label"],
            onto_comment=ontology_definition.get("comment"),
            project_ontologies=project_ontologies,
            con=con,
            project_remote=project_remote,
            context=context,
            verbose=verbose,
        )
        if not ontology_remote:
            overall_success = False
            continue

        # add the empty resource classes to the remote ontology
        last_modification_date, remote_res_classes, success = _add_resource_classes_to_remote_ontology(
            onto_name=ontology_definition["name"],
            resclass_definitions=ontology_definition.get("resources", []),
            ontology_remote=ontology_remote,
            con=con,
            last_modification_date=ontology_remote.lastModificationDate,
            verbose=verbose,
        )
        if not success:
            overall_success = False

        # add the property classes to the remote ontology
        last_modification_date, success = _add_property_classes_to_remote_ontology(
            onto_name=ontology_definition["name"],
            property_definitions=ontology_definition.get("properties", []),
            ontology_remote=ontology_remote,
            names_and_iris_of_list_nodes=names_and_iris_of_list_nodes,
            con=con,
            last_modification_date=last_modification_date,
            knora_api_prefix=knora_api_prefix,
            verbose=verbose,
        )
        if not success:
            overall_success = False

        # Add cardinalities to class
        success = _add_cardinalities_to_resource_classes(
            resclass_definitions=ontology_definition.get("resources", []),
            ontology_remote=ontology_remote,
            remote_res_classes=remote_res_classes,
            last_modification_date=last_modification_date,
            knora_api_prefix=knora_api_prefix,
            verbose=verbose,
        )
        if not success:
            overall_success = False

    return overall_success


def _add_resource_classes_to_remote_ontology(
    onto_name: str,
    resclass_definitions: list[dict[str, Any]],
    ontology_remote: Ontology,
    con: Connection,
    last_modification_date: DateTimeStamp,
    verbose: bool,
) -> tuple[DateTimeStamp, dict[str, ResourceClass], bool]:
    """
    Creates the resource classes (without cardinalities) defined in the "resources" section of an ontology. The
    containing project and the containing ontology must already be existing on the DSP server.
    If an error occurs during creation of a resource class, it is printed out, the process continues, but the success
    status will be false.

    Args:
        onto_name: name of the current ontology
        resclass_definitions: the part of the parsed JSON project file that contains the resources of the current onto
        ontology_remote: representation of the current ontology on the DSP server
        con: connection to the DSP server
        last_modification_date: last modification date of the ontology on the DSP server
        verbose: verbose switch

    Returns:
        last modification date of the ontology,
        new resource classes,
        success status
    """

    overall_success = True
    print("\tCreate resource classes...")
    logger.info("Create resource classes...")
    new_res_classes: dict[str, ResourceClass] = {}
    sorted_resources = _sort_resources(resclass_definitions, onto_name)
    for res_class in sorted_resources:
        super_classes = res_class["super"]
        if isinstance(super_classes, str):
            super_classes = [super_classes]
        res_class_local = ResourceClass(
            con=con,
            context=ontology_remote.context,
            ontology_id=ontology_remote.iri,
            name=res_class["name"],
            superclasses=super_classes,
            label=LangString(res_class.get("labels")),
            comment=LangString(res_class.get("comments")) if res_class.get("comments") else None,
        )
        try:
            last_modification_date, res_class_remote = try_network_action(
                res_class_local.create, last_modification_date
            )
            res_class_remote = cast(ResourceClass, res_class_remote)
            new_res_classes[str(res_class_remote.iri)] = res_class_remote
            ontology_remote.lastModificationDate = last_modification_date
            if verbose:
                print(f"\tCreated resource class '{res_class['name']}'")
            logger.info(f"Created resource class '{res_class['name']}'")
        except BaseError:
            print(f"WARNING: Unable to create resource class '{res_class['name']}'.")
            logger.warning(f"Unable to create resource class '{res_class['name']}'.", exc_info=True)
            overall_success = False

    return last_modification_date, new_res_classes, overall_success


def _add_property_classes_to_remote_ontology(
    onto_name: str,
    property_definitions: list[dict[str, Any]],
    ontology_remote: Ontology,
    names_and_iris_of_list_nodes: dict[str, Any],
    con: Connection,
    last_modification_date: DateTimeStamp,
    knora_api_prefix: str,
    verbose: bool,
) -> tuple[DateTimeStamp, bool]:
    """
    Creates the property classes defined in the "properties" section of an ontology. The
    containing project and the containing ontology must already be existing on the DSP server.
    If an error occurs during creation of a property class, it is printed out, the process continues, but the success
    status will be false.

    Args:
        onto_name: name of the current ontology
        property_definitions: the part of the parsed JSON project file that contains the properties of the current onto
        ontology_remote: representation of the current ontology on the DSP server
        names_and_iris_of_list_nodes: IRIs of list nodes that were already created and are available on the DSP server
        con: connection to the DSP server
        last_modification_date: last modification date of the ontology on the DSP server
        knora_api_prefix: the prefix that stands for the knora-api ontology
        verbose: verbose switch

    Returns:
        a tuple consisting of the last modification date of the ontology, and the success status
    """
    overall_success = True
    print("\tCreate property classes...")
    logger.info("Create property classes...")
    sorted_prop_classes = _sort_prop_classes(property_definitions, onto_name)
    for prop_class in sorted_prop_classes:
        # get the super-property/ies, valid forms are:
        #   - "prefix:super-property" : fully qualified name of property in another ontology. The prefix has to be
        #     defined in the prefixes part.
        #   - ":super-property" : super-property defined in current ontology
        #   - "super-property" : super-property defined in the knora-api ontology
        #   - if omitted, "knora-api:hasValue" is assumed
        if prop_class.get("super"):
            super_props = []
            for super_class in prop_class["super"]:
                if ":" in super_class:
                    prefix, _class = super_class.split(":")
                    super_props.append(super_class if prefix else f"{ontology_remote.name}:{_class}")
                else:
                    super_props.append(knora_api_prefix + super_class)
        else:
            super_props = ["knora-api:hasValue"]

        # get the "object", valid forms are:
        #   - "prefix:object_name" : fully qualified object. The prefix has to be defined in the prefixes part.
        #   - ":object_name" : The object is defined in the current ontology.
        #   - "object_name" : The object is defined in "knora-api"
        if ":" in prop_class["object"]:
            prefix, _object = prop_class["object"].split(":")
            prop_object = f"{prefix}:{_object}" if prefix else f"{ontology_remote.name}:{_object}"
        else:
            prop_object = knora_api_prefix + prop_class["object"]

        # get the gui_attributes
        gui_attributes = prop_class.get("gui_attributes")
        if gui_attributes and gui_attributes.get("hlist"):
            list_iri = names_and_iris_of_list_nodes[gui_attributes["hlist"]]["id"]
            gui_attributes["hlist"] = f"<{list_iri}>"

        # create the property class
        prop_class_local = PropertyClass(
            con=con,
            context=ontology_remote.context,
            label=LangString(prop_class.get("labels")),
            name=prop_class["name"],
            ontology_id=ontology_remote.iri,
            superproperties=super_props,
            rdf_object=prop_object,
            rdf_subject=prop_class.get("subject"),
            gui_element="salsah-gui:" + prop_class["gui_element"],
            gui_attributes=gui_attributes,
            comment=LangString(prop_class["comments"]) if prop_class.get("comments") else None,
        )
        try:
            last_modification_date, _ = try_network_action(prop_class_local.create, last_modification_date)
            ontology_remote.lastModificationDate = last_modification_date
            if verbose:
                print(f"\tCreated property class '{prop_class['name']}'")
            logger.info(f"Created property class '{prop_class['name']}'")
        except BaseError:
            print(f"WARNING: Unable to create property class '{prop_class['name']}'.")
            logger.warning(f"Unable to create property class '{prop_class['name']}'.", exc_info=True)
            overall_success = False

    return last_modification_date, overall_success


def _add_cardinalities_to_resource_classes(
    resclass_definitions: list[dict[str, Any]],
    ontology_remote: Ontology,
    remote_res_classes: dict[str, ResourceClass],
    last_modification_date: DateTimeStamp,
    knora_api_prefix: str,
    verbose: bool,
) -> bool:
    """
    Iterates over the resource classes of an ontology of a JSON project definition, and adds the cardinalities to each
    resource class. The resource classes and the properties must already be existing on the DSP server.
    If an error occurs during creation of a cardinality, it is printed out, the process continues, but the success
    status will be false.

    Args:
        resclass_definitions: the part of the parsed JSON project file that contains the resources of the current onto
        ontology_remote: representation of the current ontology on the DSP server
        remote_res_classes: representations of the resource classes on the DSP server
        last_modification_date: last modification date of the ontology on the DSP server
        knora_api_prefix: the prefix that stands for the knora-api ontology
        verbose: verbose switch

    Returns:
        success status
    """
    overall_success = True
    print("\tAdd cardinalities to resource classes...")
    logger.info("Add cardinalities to resource classes...")
    switcher = {
        "1": Cardinality.C_1,
        "0-1": Cardinality.C_0_1,
        "0-n": Cardinality.C_0_n,
        "1-n": Cardinality.C_1_n,
    }
    for res_class in resclass_definitions:
        res_class_remote = remote_res_classes.get(f"{ontology_remote.iri}#{res_class['name']}")
        if not res_class_remote:
            msg = (
                f"Unable to add cardinalities to resource class '{res_class['name']}': "
                f"This class doesn't exist on the DSP server."
            )
            print(f"WARNINIG: {msg}")
            logger.warning(msg)
            overall_success = False
            continue
        for card_info in res_class.get("cardinalities", []):
            if ":" in card_info["propname"]:
                prefix, prop = card_info["propname"].split(":")
                qualified_propname = card_info["propname"] if prefix else f"{ontology_remote.name}:{prop}"
            else:
                qualified_propname = knora_api_prefix + card_info["propname"]

            try:
                last_modification_date = try_network_action(
                    res_class_remote.addProperty,
                    property_id=qualified_propname,
                    cardinality=switcher[card_info["cardinality"]],
                    gui_order=card_info.get("gui_order"),
                    last_modification_date=last_modification_date,
                )
                if verbose:
                    print(f"\tAdded cardinality '{card_info['propname']}' to resource class '{res_class['name']}'")
                logger.info(f"Added cardinality '{card_info['propname']}' to resource class '{res_class['name']}'")
            except BaseError:
                err_msg = f"Unable to add cardinality '{qualified_propname}' to resource class {res_class['name']}."
                print(f"WARNING: {err_msg}")
                logger.warning(err_msg, exc_info=True)
                overall_success = False

            ontology_remote.lastModificationDate = last_modification_date

    return overall_success


def _rectify_hlist_of_properties(
    lists: list[dict[str, Any]],
    properties: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Check the "hlist" of the "gui_attributes" of the properties.
    If they don't refer to an existing list name,
    check if there is a label of a list that corresponds to the "hlist".
    If so, rectify the "hlist" to refer to the name of the list instead of the label.

    Args:
        lists: "lists" section of the JSON project definition
        properties: "properties" section of one of the ontologies of the JSON project definition

    Raises:
        UserError: if the "hlist" refers to no existing list name or label

    Returns:
        the rectified "properties" section
    """

    if not lists or not properties:
        return properties

    existing_list_names = [l["name"] for l in lists]

    for prop in properties:
        if not prop.get("gui_attributes"):
            continue
        if not prop["gui_attributes"].get("hlist"):
            continue
        list_name = prop["gui_attributes"]["hlist"] if prop["gui_attributes"]["hlist"] in existing_list_names else None
        if list_name:
            continue

        deduced_list_name = None
        for root_node in lists:
            if prop["gui_attributes"]["hlist"] in root_node["labels"].values():
                deduced_list_name = cast(str, root_node["name"])
        if deduced_list_name:
            msg = (
                f"INFO: Property '{prop['name']}' references the list '{prop['gui_attributes']['hlist']}' "
                f"which is not a valid list name. "
                f"Assuming that you meant '{deduced_list_name}' instead."
            )
            logger.warning(msg)
            print(msg)
        else:
            msg = f"Property '{prop['name']}' references an unknown list: '{prop['gui_attributes']['hlist']}'"
            logger.error(msg)
            raise UserError(f"ERROR: {msg}")
        prop["gui_attributes"]["hlist"] = deduced_list_name

    return properties


def create_project(
    project_file_as_path_or_parsed: Union[str, Path, dict[str, Any]],
    server: str,
    user_mail: str,
    password: str,
    verbose: bool = False,
    dump: bool = False,
) -> bool:
    """
    Creates a project from a JSON project file on a DSP server.
    A project must contain at least one ontology,
    and it may contain lists, users, and groups.
    Severe errors lead to a BaseError,
    while other errors are printed without interrupting the process.

    Args:
        project_file_as_path_or_parsed: path to the JSON project definition, or parsed JSON object
        server: the URL of the DSP server on which the project should be created
        user_mail: a username (e-mail) who has the permission to create a project
        password: the user's password
        verbose: prints more information if set to True
        dump: if True, write every request to DSP-API into a file

    Raises:
        UserError:
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

    project_definition = parse_json_input(project_file_as_path_or_parsed=project_file_as_path_or_parsed)
    proj_shortname = project_definition["project"]["shortname"]
    proj_shortcode = project_definition["project"]["shortcode"]
    context = Context(project_definition.get("prefixes", {}))

    # expand the Excel files referenced in the "lists" section of the project (if any), and add them to the project
    if new_lists := expand_lists_from_excel(project_definition.get("project", {}).get("lists", [])):
        project_definition["project"]["lists"] = new_lists

    # validate against JSON schema
    validate_project(project_definition, expand_lists=False)
    print("\tJSON project file is syntactically correct and passed validation.")
    logger.info("JSON project file is syntactically correct and passed validation.")

    # rectify the "hlist" of the "gui_attributes" of the properties
    for onto in project_definition["project"]["ontologies"]:
        if onto.get("properties"):
            onto["properties"] = _rectify_hlist_of_properties(
                lists=project_definition["project"].get("lists", []),
                properties=onto["properties"],
            )

    # establish connection to DSP server
    con = login(server=server, user=user_mail, password=password, dump=dump)

    # create project on DSP server
    print(f"Create project '{proj_shortname}' ({proj_shortcode})...")
    logger.info(f"Create project '{proj_shortname}' ({proj_shortcode})...")
    project_remote, success = _create_project_on_server(
        shortcode=project_definition["project"]["shortcode"],
        shortname=project_definition["project"]["shortname"],
        longname=project_definition["project"]["longname"],
        descriptions=project_definition["project"].get("descriptions"),
        keywords=project_definition["project"].get("keywords"),
        con=con,
        verbose=verbose,
    )
    if not success:
        overall_success = False

    # create the lists
    names_and_iris_of_list_nodes: dict[str, Any] = {}
    if project_definition["project"].get("lists"):
        print("Create lists...")
        logger.info("Create lists...")
        names_and_iris_of_list_nodes, success = create_lists_on_server(
            lists_to_create=project_definition["project"]["lists"],
            con=con,
            project_remote=project_remote,
        )
        if not success:
            overall_success = False

    # create the groups
    current_project_groups: dict[str, Group] = {}
    if project_definition["project"].get("groups"):
        print("Create groups...")
        logger.info("Create groups...")
        current_project_groups, success = _create_groups(
            con=con,
            groups=project_definition["project"]["groups"],
            project=project_remote,
        )
        if not success:
            overall_success = False

    # create or update the users
    if project_definition["project"].get("users"):
        print("Create users...")
        logger.info("Create users...")
        success = _create_users(
            con=con,
            users_section=project_definition["project"]["users"],
            current_project_groups=current_project_groups,
            current_project=project_remote,
            verbose=verbose,
        )
        if not success:
            overall_success = False

    # create the ontologies
    success = _create_ontologies(
        con=con,
        context=context,
        knora_api_prefix=knora_api_prefix,
        names_and_iris_of_list_nodes=names_and_iris_of_list_nodes,
        ontology_definitions=project_definition["project"]["ontologies"],
        project_remote=project_remote,
        verbose=verbose,
    )
    if not success:
        overall_success = False

    # final steps
    if overall_success:
        msg = (
            f"Successfully created project '{proj_shortname}' ({proj_shortcode}) with all its ontologies. "
            f"There were no problems during the creation process."
        )
        print(f"========================================================\n{msg}")
        logger.info(msg)
    else:
        msg = (
            f"The project '{proj_shortname}' ({proj_shortcode}) with its ontologies could be created, "
            f"but during the creation process, some problems occurred. Please carefully check the console output."
        )
        print(f"========================================================\nWARNING: {msg}")
        logger.warning(msg)

    return overall_success
