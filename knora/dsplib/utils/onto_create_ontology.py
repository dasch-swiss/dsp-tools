"""This module handles the ontology creation, update and upload to a DSP server. This includes the creation and update
of the project, the creation of groups, users, lists, resource classes, properties and cardinalities."""
import json
import re
from typing import Any, cast, Tuple

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.group import Group
from knora.dsplib.models.helpers import BaseError, Cardinality, Context
from knora.dsplib.models.langstring import LangString
from knora.dsplib.models.ontology import Ontology
from knora.dsplib.models.project import Project
from knora.dsplib.models.propertyclass import PropertyClass
from knora.dsplib.models.resourceclass import ResourceClass
from knora.dsplib.models.user import User
from knora.dsplib.utils.excel_to_json_lists import expand_lists_from_excel
from knora.dsplib.utils.onto_create_lists import create_lists
from knora.dsplib.utils.onto_validate import validate_project
from knora.dsplib.utils.shared_methods import login, try_network_action


def _create_project(con: Connection, project_definition: dict[str, Any]) -> Project:
    """
    Creates a project on a DSP server from a parsed JSON project file. Raises a BaseError if it is not
    possible to create the project.

    Args:
        con: connection instance to connect to the DSP server
        project_definition: a parsed JSON project file

    Returns:
        created project
    """
    project_local = Project(
        con=con,
        shortcode=project_definition["project"]["shortcode"],
        shortname=project_definition["project"]["shortname"],
        longname=project_definition["project"]["longname"],
        description=LangString(project_definition["project"].get("descriptions")),
        keywords=set(project_definition["project"].get("keywords")),
        selfjoin=False,
        status=True
    )
    project_remote: Project = try_network_action(
        action=lambda: project_local.create(),
        failure_msg=f"ERROR: Cannot create project '{project_definition['project']['shortname']}' "
                    f"({project_definition['project']['shortcode']}) on DSP server."
    )
    return project_remote


def _update_project(project: Project, project_definition: dict[str, Any], verbose: bool) -> Project:
    """
    Updates a project on a DSP server from a JSON project file. Only the longname, description and keywords will be
    updated. Raises a BaseError if the project cannot be updated.

    Args:
        project: the project to be updated (must exist on the DSP server)
        project_definition: a parsed JSON project file with the same shortname and shortcode than the existing project

    Returns:
        updated project
    """
    project.longname = project_definition["project"]["longname"]
    project.description = project_definition["project"].get("descriptions")
    project.keywords = project_definition["project"].get("keywords")
    project_remote: Project = try_network_action(
        action=lambda: project.update(),
        failure_msg=f"WARNING: Could not update project '{project_definition['project']['shortname']}' "
                    f"({project_definition['project']['shortcode']})."
    )
    if verbose:
        print(f"\tUpdated project '{project_definition['project']['shortname']}' ({project_definition['project']['shortcode']}).")
    return project_remote


def _create_groups(con: Connection, groups: list[dict[str, str]], project: Project) -> Tuple[dict[str, Group], bool]:
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
        dict of the form ``{group name: group object}`` with the groups that have successfully been created (or already exist). Empty dict if no group was created.
        True if everything went smoothly, False if a warning or error occurred
    """
    overall_success = True
    current_project_groups: dict[str, Group] = {}
    try:
        remote_groups: list[Group] = try_network_action(
            action=lambda: Group.getAllGroupsForProject(con=con, proj_shortcode=project.shortcode),
            failure_msg="WARNING: Unable to check if group names are already existing on DSP server, because it is "
                        "not possible to retrieve the remote groups from DSP server."
        )
    except BaseError as err:
        print(err.message)
        remote_groups = []
        overall_success = False
        
    for group in groups:
        group_name = group["name"]

        # if the group already exists, add it to "current_project_groups" (for later usage), then skip it
        remotely_existing_group = [g for g in remote_groups if g.name == group_name]
        if remotely_existing_group:
            current_project_groups[group_name] = remotely_existing_group[0]
            print(f"\tWARNING: Group name '{group_name}' already exists on the DSP server. Skipping...")
            overall_success = False
            continue

        # create the group
        group_local = Group(
            con=con,
            name=group_name,
            descriptions=LangString(group["descriptions"]),
            project=project,
            status=group.get("status", True),
            selfjoin=group.get("selfjoin", False)
        )
        try:
            group_remote: Group = try_network_action(
                action=lambda: group_local.create(),
                failure_msg=f"\tWARNING: Unable to create group '{group_name}'."
            )
        except BaseError as err:
            print(err.message)
            overall_success = False
            continue

        current_project_groups[group_remote.name] = group_remote
        print(f"\tCreated group '{group_name}'.")

    return current_project_groups, overall_success


def _create_users(
    con: Connection,
    users: list[dict[str, str]],
    current_project_groups: dict[str, Group],
    current_project: Project,
    verbose: bool
) -> bool:
    """
    Creates users on a DSP server from the "users" section of a JSON project file. If a user cannot be created, a
    warning is printed and the user is skipped.

    Args:
        con: connection instance to connect to the DSP server
        users: "users" section of a parsed JSON project file
        current_project_groups: groups defined in the current project (dict of the form {group name - group object}). These groups must exist on the DSP server.
        current_project: "project" object of the current project (must exist on DSP server)
        verbose: Prints more information if set to True

    Returns:
        True if all users could be created without any problems. False if a warning/error occurred.
    """
    overall_success = True
    for user in users:
        username = user["username"]

        # skip the user if he already exists
        try:
            try_network_action(
                action=lambda: User(con, email=user["email"]).read(),
                failure_msg=""
            )
            print(f"\tWARNING: User '{username}' already exists on the DSP server. Skipping...")
            overall_success = False
            continue
        except BaseError:
            pass

        # if "groups" is provided, add user to the group(s)
        group_ids: set[str] = set()
        sysadmin = False
        remote_groups: list[Group] = []
        for full_group_name in user.get("groups", []):
            # full_group_name has the form '[project_shortname]:group_name' or 'SystemAdmin'
            if ":" not in full_group_name and full_group_name != "SystemAdmin":
                print(f"\tWARNING: User {username} cannot be added to group {full_group_name}, because such a "
                      f"group doesn't exist.")
                overall_success = False
                continue

            if full_group_name == "SystemAdmin":
                sysadmin = True
                if verbose:
                    print(f"\tAdded user '{username}' to group 'SystemAdmin'.")
                continue

            # all other cases (":" in full_group_name)
            project_shortname, group_name = full_group_name.split(":")
            if not project_shortname:
                # full_group_name refers to a group inside the same project
                if group_name not in current_project_groups:
                    print(f"\tWARNING: User {username} cannot be added to group {full_group_name}, because "
                          f"such a group doesn't exist.")
                    overall_success = False
                    continue
                group = current_project_groups[group_name]
            else:
                # full_group_name refers to an already existing group on DSP
                try:
                    # "remote_groups" might be available from a previous loop cycle
                    remote_groups = remote_groups or try_network_action(
                        action=lambda: Group.getAllGroups(con=con),
                        failure_msg=f"\tWARNING: User '{username}' is referring to the group {full_group_name} that "
                                    f"exists on the DSP server, but no groups could be retrieved from the DSP server."
                    )
                except BaseError as err:
                    print(err.message)
                    overall_success = False
                    continue
                existing_group = [g for g in remote_groups if g.project == current_project.id and g.name == group_name]
                if not existing_group:
                    print(f"\tWARNING: User {username} cannot be added to group {full_group_name}, because "
                          f"such a group doesn't exist.")
                    overall_success = False
                    continue
                group = existing_group[0]

            group_ids.add(group.id)
            if verbose:
                print(f"\tAdded user '{username}' to group '{full_group_name}'.")

        # if "projects" is provided, add user to the project(s)
        project_info: dict[str, bool] = {}
        remote_projects: list[Project] = []
        for full_project_name in user.get("projects", []):
            # full_project_name has the form '[project_name]:member' or '[project_name]:admin'
            if ":" not in full_project_name:
                print(f"\tWARNING: Provided project '{full_project_name}' for user '{username}' is not valid. "
                      f"Skipping...")
                overall_success = False
                continue

            project_name, project_role = full_project_name.split(":")
            if not project_name:
                # full_project_name refers to the current project
                in_project = current_project
            else:
                # full_project_name refers to an already existing project on DSP
                try:
                    # "remote_projects" might be available from a previous loop cycle
                    remote_projects = remote_projects or try_network_action(
                        action=lambda: current_project.getAllProjects(con=con),
                        failure_msg=f"\tWARNING: User '{username}' cannot be added to the projects {user['projects']} "
                                    f"because the projects cannot be retrieved from the DSP server."
                    )
                except BaseError as err:
                    print(err.message)
                    overall_success = False
                    continue
                in_project_list = [p for p in remote_projects if p.shortname == project_name]
                if not in_project_list:
                    print(f"\tWARNING: Provided project '{full_project_name}' for user '{username}' is not valid. "
                          f"Skipping...")
                    overall_success = False
                    continue
                in_project = in_project_list[0]

            project_info[in_project.id] = bool(project_role == "admin")
            if verbose:
                print(f"\tAdded user '{username}' as {project_role} to project '{in_project.shortname}'.")

        # create the user
        user_local = User(
            con=con,
            username=user["username"],
            email=user["email"],
            givenName=user["givenName"],
            familyName=user["familyName"],
            password=user["password"],
            status=user.get("status", True),
            lang=user.get("lang", "en"),
            sysadmin=sysadmin,
            in_projects=project_info,
            in_groups=group_ids
        )
        try:
            try_network_action(
                action=lambda: user_local.create(),
                failure_msg=f"\tWARNING: Unable to create user '{username}'."
            )
        except BaseError as err:
            print(err.message)
            overall_success = False
            continue
        print(f"\tCreated user '{username}'.")

    return overall_success


def _sort_resources(unsorted_resources: list[dict[str, Any]], onto_name: str) -> list[dict[str, Any]]:
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
    sorted_resources: list[dict[str, Any]] = list()
    ok_resource_names: list[str] = list()
    while len(resources_to_sort) > 0:
        # inside the for loop, resources_to_sort is modified, so a copy must be made to iterate over
        for res in resources_to_sort.copy():
            res_name = f'{onto_name}:{res["name"]}'
            parent_classes = res['super']
            if isinstance(parent_classes, str):
                parent_classes = [parent_classes]
            parent_classes = [re.sub(r'^:([^:]+)$', f'{onto_name}:\\1', elem) for elem in parent_classes]
            parent_classes_ok = [not p.startswith(onto_name) or p in ok_resource_names for p in parent_classes]
            if all(parent_classes_ok):
                sorted_resources.append(res)
                ok_resource_names.append(res_name)
                resources_to_sort.remove(res)
    return sorted_resources


def _sort_prop_classes(unsorted_prop_classes: list[dict[str, Any]], onto_name: str) -> list[dict[str, Any]]:
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
    sorted_prop_classes: list[dict[str, Any]] = list()
    ok_propclass_names: list[str] = list()
    while len(prop_classes_to_sort) > 0:
        # inside the for loop, resources_to_sort is modified, so a copy must be made to iterate over
        for prop in prop_classes_to_sort.copy():
            prop_name = f'{onto_name}:{prop["name"]}'
            parent_classes = prop.get('super', 'hasValue')
            if isinstance(parent_classes, str):
                parent_classes = [parent_classes]
            parent_classes = [re.sub(r'^:([^:]+)$', f'{onto_name}:\\1', elem) for elem in parent_classes]
            parent_classes_ok = [not p.startswith(onto_name) or p in ok_propclass_names for p in parent_classes]
            if all(parent_classes_ok):
                sorted_prop_classes.append(prop)
                ok_propclass_names.append(prop_name)
                prop_classes_to_sort.remove(prop)
    return sorted_prop_classes


def create_project(
    input_file: str,
    server: str,
    user_mail: str,
    password: str,
    verbose: bool,
    dump: bool
) -> bool:
    """
    Creates a project from a JSON project file on a DSP server. A project must contain at least one ontology, and it may
    contain lists, users, and groups.
    Returns True if everything went smoothly during the process, False if a warning or error occurred.

    Args:
        input_file: the path to the JSON file from which the project and its parts should be created
        server: the URL of the DSP server on which the project should be created
        user_mail: a username (e-mail) who has the permission to create a project
        password: the user's password
        verbose: prints more information if set to True
        dump: dumps test files (JSON) for DSP API requests if set to True

    Returns:
        True if everything went smoothly, False if a warning or error occurred
    """

    knora_api_prefix = "knora-api:"
    overall_success = True
    success = True

    # create project
    ################
    with open(input_file) as f:
        project_json_str = f.read()
    project_definition = json.loads(project_json_str)
    print(f"Create project '{project_definition['project']['shortname']}' "
          f"({project_definition['project']['shortcode']})...")

    # expand all lists referenced in the "lists" section of the project, and add them to the project
    new_lists, success = expand_lists_from_excel(project_definition["project"].get("lists", []))
    if new_lists:
        project_definition["project"]["lists"] = new_lists
    if not success:
        overall_success = False

    if validate_project(project_definition, expand_lists=False):
        print('\tJSON project file is syntactically correct and passed validation.')

    con = login(server=server, user=user_mail, password=password)
    if dump:
        con.start_logging()

    # read the prefixes of external ontologies that may be used
    context = Context(project_definition.get("prefixes") or {})

    # if project exists, update it, otherwise create it
    project_local = Project(con=con, shortcode=project_definition["project"]["shortcode"])
    try:
        project_remote: Project = try_network_action(
            action=lambda: project_local.read(),
            failure_msg=""
        )
        print(f"\tWARNING: Project '{project_remote.shortname}' ({project_remote.shortcode}) already exists on the DSP "
              f"server. Updating it...")
        overall_success = False
        try:
            project_remote = _update_project(project=project_remote, project_definition=project_definition, verbose=verbose)
        except BaseError as err:
            print(err.message)
    except BaseError:
        project_remote = _create_project(con=con, project_definition=project_definition)
        print(f"\tCreated project '{project_remote.shortname}' ({project_remote.shortcode}).")

    # create the lists
    ##################
    list_root_nodes: dict[str, Any] = {}
    if project_definition["project"].get("lists"):
        print("Create lists...")
        list_root_nodes, success = create_lists(server=server, user=user_mail, password=password, project_definition=project_definition)
        if not success:
            overall_success = False

    # create the groups
    ###################
    current_project_groups: dict[str, Group] = {}
    if project_definition["project"].get("groups"):
        print("Create groups...")
        current_project_groups, success = _create_groups(
            con=con, 
            groups=project_definition["project"]["groups"], 
            project=project_remote
        )
        if not success:
            overall_success = False

    # create or update the users
    ############################
    if project_definition["project"].get("users"):
        print("Create users...")
        success = _create_users(
            con=con, 
            users=project_definition["project"]["users"], 
            current_project_groups=current_project_groups, 
            current_project=project_remote, 
            verbose=verbose
        )
        if not success:
            overall_success = False

    # create the ontologies
    #######################
    print("Create ontologies...")
    all_ontologies: list[Ontology] = try_network_action(
        action=lambda: Ontology.getAllOntologies(con=con),
        failure_msg="WARNING: Unable to retrieve remote ontologies. Cannot check if your ontology already exists."
    )
    for ontology in project_definition.get("project").get("ontologies"):
        if ontology["name"] in [onto.name for onto in all_ontologies]:
            print(f"\tWARNING: Ontology '{ontology['name']}' already exists on the DSP server. Skipping...")
            overall_success = False
            continue

        print(f"Create ontology '{ontology['name']}'...")
        ontology_local = Ontology(
            con=con,
            project=project_remote,
            label=ontology["label"],
            name=ontology["name"]
        )
        ontology_remote: Ontology = try_network_action(
            action=lambda: ontology_local.create(),
            failure_msg=f"ERROR while trying to create ontology '{ontology['name']}'."
        )
        context.add_context(ontology_remote.name, ontology_remote.id + ('#' if not ontology_remote.id.endswith('#') else ''))
        last_modification_date = ontology_remote.lastModificationDate
        if verbose:
            print(f"\tCreated ontology '{ontology['name']}'.")

        # add the prefixes defined in the json file
        for onto_prefix, onto_info in context:
            if onto_info and onto_prefix not in ontology_remote.context:
                onto_iri = onto_info.iri + ("#" if onto_info.hashtag else "")
                ontology_remote.context.add_context(onto_prefix, onto_iri)

        # create the empty resource classes
        print("\tCreate resource classes...")
        new_res_classes: dict[str, ResourceClass] = {}
        sorted_resources = _sort_resources(ontology["resources"], ontology["name"])
        for res_class in sorted_resources:
            super_classes = res_class["super"]
            if isinstance(super_classes, str):
                super_classes = [super_classes]
            res_class_local = ResourceClass(
                con=con,
                context=ontology_remote.context,
                ontology_id=ontology_remote.id,
                name=res_class["name"],
                superclasses=super_classes,
                label=LangString(res_class.get("labels")),
                comment=LangString(res_class.get("comments")) if res_class.get("comments") else None
            )
            try:
                last_modification_date, res_class_remote = try_network_action(
                    action=lambda: res_class_local.create(last_modification_date=last_modification_date),
                    failure_msg=f"WARNING: Unable to create resource class '{res_class['name']}'."
                )
                res_class_remote = cast(ResourceClass, res_class_remote)
                new_res_classes[res_class_remote.id] = res_class_remote
                ontology_remote.lastModificationDate = last_modification_date
                if verbose:
                    print(f"\tCreated resource class '{res_class['name']}'")
            except BaseError as err:
                print(err.message)
                overall_success = False

        # create the property classes
        print("\tCreate property classes...")
        sorted_prop_classes = _sort_prop_classes(ontology["properties"], ontology["name"])
        new_prop_classes: dict[str, PropertyClass] = {}
        for prop_class in sorted_prop_classes:

            # get the super-property/ies, valid forms are:
            #   - "prefix:super-property" : fully qualified name of property in another ontology. The prefix has to be
            #     defined in the prefixes part.
            #   - ":super-property" : super-property defined in current ontology
            #   - "super-property" : super-property defined in the knora-api ontology
            #   - if omitted, "knora-api:hasValue" is assumed
            if prop_class.get("super"):
                super_props = []
                for super_class in prop_class.get("super"):
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
                prefix, _object = prop_class["object"].split(':')
                prop_object = f"{prefix}:{_object}" if prefix else f"{ontology_remote.name}:{_object}"
            else:
                prop_object = knora_api_prefix + prop_class["object"]

            gui_attributes = prop_class.get("gui_attributes")
            if gui_attributes and gui_attributes.get("hlist"):
                gui_attributes["hlist"] = "<" + list_root_nodes[gui_attributes["hlist"]]["id"] + ">"

            prop_class_local = PropertyClass(
                con=con,
                context=ontology_remote.context,
                label=LangString(prop_class.get("labels")),
                name=prop_class["name"],
                ontology_id=ontology_remote.id,
                superproperties=super_props,
                object=prop_object,
                subject=prop_class.get("subject"),
                gui_element="salsah-gui:" + prop_class["gui_element"],
                gui_attributes=gui_attributes,
                comment=LangString(prop_class["comments"]) if prop_class.get("comments") else None
            )
            try:
                last_modification_date, prop_class_remote = try_network_action(
                    action=lambda: prop_class_local.create(last_modification_date=last_modification_date),
                    failure_msg=f"WARNING: Unable to create property class '{prop_class['name']}'."
                )
                prop_class_remote = cast(PropertyClass, prop_class_remote)
                new_prop_classes[prop_class_remote.id] = prop_class_remote
                ontology_remote.lastModificationDate = last_modification_date
                if verbose:
                    print(f"\tCreated property class '{prop_class['name']}'")
            except BaseError as err:
                print(err.message)
                overall_success = False

        # Add cardinalities to class
        print("\tAdd cardinalities to resource classes...")
        switcher = {
            "1": Cardinality.C_1,
            "0-1": Cardinality.C_0_1,
            "0-n": Cardinality.C_0_n,
            "1-n": Cardinality.C_1_n
        }

        for res_class in ontology.get("resources"):
            res_class_remote = new_res_classes.get(ontology_remote.id + "#" + res_class["name"])
            if not res_class_remote:
                print(f"WARNING: Unable to add cardinalities to resource class '{res_class['name']}': This class "
                      f"doesn't exist on the DSP server.")
                overall_success = False
                continue
            for card_info in res_class.get("cardinalities"):
                if ":" in card_info["propname"]:
                    prefix, prop = card_info["propname"].split(":")
                    qualified_propname = card_info["propname"] if prefix else f"{ontology_remote.name}:{prop}"
                    if not new_prop_classes.get(ontology_remote.id + "#" + prop):
                        print(f"WARNING: Unable to add cardinality '{card_info['propname']}' to resource class "
                              f"'{res_class['name']}': This property class doesn't exist on the DSP server.")
                        overall_success = False
                        continue
                else:
                    qualified_propname = knora_api_prefix + card_info["propname"]

                try:
                    last_modification_date = try_network_action(
                        action=lambda: res_class_remote.addProperty(
                            property_id=qualified_propname,
                            cardinality=switcher[card_info["cardinality"]],
                            gui_order=card_info.get("gui_order"),
                            last_modification_date=last_modification_date
                        ),
                        failure_msg=f"WARNING: Unable to add cardinality '{qualified_propname}' to resource class "
                                    f"{res_class['name']}."
                    )
                    if verbose:
                        print(f"\tAdded cardinality '{card_info['propname']}' to resource class '{res_class['name']}'")
                except BaseError as err:
                    print(err.message)
                    overall_success = False

                ontology_remote.lastModificationDate = last_modification_date

    # final steps
    #############
    if overall_success:
        print("========================================================\n",
              f"Successfully created project '{project_definition['project']['shortname']}' "
              f"({project_definition['project']['shortcode']}) with all its ontologies. There were no problems during "
              f"the creation process.")
    else:
        print("========================================================\n",
              f"WARNING: The project '{project_definition['project']['shortname']}' ({project_definition['project']['shortcode']}) "
              f"with its ontologies could be created, but during the creation process, some problems occurred. "
              f"Please carefully check the console output.")
    return overall_success
