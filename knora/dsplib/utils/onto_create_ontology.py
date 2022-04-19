"""This module handles the ontology creation, update and upload to a DSP server. This includes the creation and update
of the project, the creation of groups, users, lists, resource classes, properties and cardinalities."""
import json
import re
from typing import Union, Optional, Any

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.group import Group
from knora.dsplib.models.helpers import BaseError, Cardinality, Context
from knora.dsplib.models.langstring import LangString
from knora.dsplib.models.ontology import Ontology
from knora.dsplib.models.project import Project
from knora.dsplib.models.propertyclass import PropertyClass
from knora.dsplib.models.resourceclass import ResourceClass
from knora.dsplib.models.user import User
from knora.dsplib.utils.expand_all_lists import expand_lists_from_excel
from knora.dsplib.utils.onto_create_lists import create_lists
from knora.dsplib.utils.onto_validate import validate_ontology


def login(server: str, user: str, password: str) -> Connection:
    """
    Logs in and returns the active connection

    Args:
        server: URL of the DSP server to connect to
        user: Username (e-mail)
        password: Password of the user

    Return:
        Connection instance
    """
    con = Connection(server)
    con.login(user, password)
    return con


def create_project(con: Connection, data_model: dict[str, Any], verbose: bool) -> Project:
    """
    Creates a project on a DSP server with information provided in the data_model

    Args:
        con: connection instance to connect to the DSP server
        data_model: The data model as JSON
        verbose: Prints out more information if set to True

    Returns:
        created project
    """
    project_shortcode = data_model["project"]["shortcode"]
    project_shortname = data_model["project"]["shortname"]

    try:
        project = Project(con=con,
                          shortcode=data_model["project"]["shortcode"],
                          shortname=data_model["project"]["shortname"],
                          longname=data_model["project"]["longname"],
                          description=LangString(data_model["project"].get("descriptions")),
                          keywords=set(data_model["project"].get("keywords")),
                          selfjoin=False,
                          status=True).create()
        if verbose:
            print(f"Created project '{project_shortname}' ({project_shortcode}).")
        return project
    except BaseError as err:
        print(
            f"ERROR while trying to create project '{project_shortname}' ({project_shortcode}). The error message was: {err.message}")
        exit(1)
    except Exception as exception:
        print(
            f"ERROR while trying to create project '{project_shortname}' ({project_shortcode}). The error message was: {exception}")
        exit(1)


def update_project(project: Project, data_model: dict[str, Any], verbose: bool) -> Project:
    """
    Updates a project on a DSP server with information provided in the data_model

    Args:
        project: The project to be updated
        data_model: The data model as JSON
        verbose: Prints out more information if set to True

    Returns:
        updated project
    """
    project_shortcode = data_model["project"]["shortcode"]
    project_shortname = data_model["project"]["shortname"]
    project.longname = data_model["project"]["longname"]
    project.description = data_model["project"].get("descriptions")
    project.keywords = data_model["project"].get("keywords")
    try:
        updated_project = project.update()
        if verbose:
            print(f"Updated project '{project_shortname}' ({project_shortcode}).")
        return updated_project
    except BaseError as err:
        print(
            f"ERROR while trying to update project '{project_shortname}' ({project_shortcode}). The error message was: {err.message}")
        exit(1)
    except Exception as exception:
        print(
            f"ERROR while trying to update project '{project_shortname}' ({project_shortcode}). The error message was: {exception}")
        exit(1)


def create_groups(con: Connection, groups: list[dict[str, str]], project: Project, verbose: bool) -> dict[str, Group]:
    """
    Creates group(s) on a DSP server from a list of group definitions

    Args:
        con: connection instance to connect to the DSP server
        groups: List of definitions of the groups (JSON) to be created
        project: Project the group(s) should be added to
        verbose: Prints out more information if set to True

    Returns:
        Dict with group names and groups
    """
    new_groups: dict[str, Group] = {}
    for group in groups:
        group_name = group["name"]

        # check if the group already exists, skip if so
        all_groups: Optional[list[Group]] = Group.getAllGroups(con)

        group_exists: bool = False
        if all_groups:
            group_exists = any(group_item.name == group_name for group_item in all_groups)

        if group_exists:
            print(f"WARN Group name '{group_name}' already in use. Skipping...")
            continue

        # check if status is defined, set default value if not
        group_status: Optional[str] = group.get("status")
        group_status_bool = True
        if isinstance(group_status, str):
            group_status_bool = json.loads(group_status.lower())  # lower() converts string to boolean

        # check if selfjoin is defined, set default value if not
        group_selfjoin: Optional[str] = group.get("selfjoin")
        group_selfjoin_bool = False
        if isinstance(group_selfjoin, str):
            group_selfjoin_bool = json.loads(group_selfjoin.lower())  # lower() converts string to boolean

        # create the group
        try:
            new_group: Group = Group(con=con,
                                     name=group_name,
                                     descriptions=LangString(group["descriptions"]),
                                     project=project,
                                     status=group_status_bool,
                                     selfjoin=group_selfjoin_bool).create()
            if verbose:
                print(f"Created group '{group_name}'.")
            if new_group.name:
                new_groups[new_group.name] = new_group

        except BaseError as err:
            print(f"ERROR while trying to create group '{group_name}'. The error message was: {err.message}")
            exit(1)
        except Exception as exception:
            print(f"ERROR while trying to create group '{group_name}'. The error message was: {exception}")
            exit(1)
    return new_groups


def create_users(con: Connection, users: list[dict[str, str]], groups: dict[str, Group], project: Project,
                 verbose: bool) -> None:
    """
    Creates user(s) on a DSP server from a list of user definitions

    Args:
        con: connection instance to connect to the DSP server
        users: List of definitions of the users (JSON) to be created
        groups: Dict with group definitions defined inside the actual ontology
        project: Project the user(s) should be added to
        verbose: Prints more information if set to True

    Returns:
        None
    """
    for user in users:
        username = user["username"]

        # check if the user already exists, skip if so
        maybe_user: Optional[User] = None
        try:
            maybe_user = User(con, email=user["email"]).read()
        except BaseError:
            pass
        if maybe_user:
            print(f"WARN User '{username}' already exists. Skipping...")
            continue

        sysadmin = False
        group_ids: set[str] = set()
        project_info: dict[str, bool] = {}

        # if "groups" is provided add user to the group(s)
        user_groups = user.get("groups")
        if user_groups:
            all_groups: Optional[list[Group]] = Group.getAllGroups(con)
            for full_group_name in user_groups:
                if verbose:
                    print(f"Add user '{username}' to group '{full_group_name}'.")
                # full_group_name has the form '[project_shortname]:group_name' or 'SystemAdmin'
                # if project_shortname is omitted, the group belongs to the current project
                tmp_group_name: Union[list[str], str] = full_group_name.split(
                    ":") if ":" in full_group_name else full_group_name

                if len(tmp_group_name) == 2:
                    project_shortname = tmp_group_name[0]
                    group_name = tmp_group_name[1]

                    group: Optional[Group] = None
                    if project_shortname:  # full_group_name refers to an already existing group on DSP
                        # check that group exists
                        if all_groups:
                            for g in all_groups:
                                if g.project == project.id and g.name == group_name:
                                    group = g
                        else:
                            print(f"WARN '{group_name}' is referring to a group on DSP but no groups found.")

                    else:  # full_group_name refers to a group inside the same ontology
                        group = groups.get(group_name)
                    if group is None:
                        print(f"WARN Group '{group_name}' not found in actual ontology.")
                    else:
                        if isinstance(group.id, str):
                            group_ids.add(group.id)
                elif tmp_group_name == "SystemAdmin":
                    sysadmin = True
                else:
                    print(f"WARN Provided group '{full_group_name}' for user '{username}' is not valid. Skipping...")

        # if "projects" is provided, add user to the projects(s)
        user_projects = user.get("projects")
        if user_projects:
            all_projects: list[Project] = project.getAllProjects(con)
            for full_project_name in user_projects:
                if verbose:
                    print(f"Add user '{username}' to project '{full_project_name}'.")
                # full_project_name has the form '[project_name]:member' or '[project_name]:admin'
                # if project_name is omitted, the user is added to the current project
                tmp_group_name = full_project_name.split(":")

                if not len(tmp_group_name) == 2:
                    print(
                        f"WARN Provided project '{full_project_name}' for user '{username}' is not valid. Skipping...")
                    continue

                project_name = tmp_group_name[0]
                project_role = tmp_group_name[1]

                in_project: Optional[Project] = None

                if project_name:  # project_name is provided
                    # check that project exists
                    for p in all_projects:
                        if p.shortname == project_name:
                            in_project = p

                else:  # no project_name provided
                    in_project = project

                if in_project and isinstance(in_project.id, str):
                    if project_role == "admin":
                        project_info[in_project.id] = True
                    else:
                        project_info[in_project.id] = False

        # create the user
        user_status: Optional[str] = user.get("status")
        user_status_bool = True
        if isinstance(user_status, str):
            user_status_bool = json.loads(user_status.lower())  # lower() converts string to boolean
        try:
            User(con=con,
                 username=user["username"],
                 email=user["email"],
                 givenName=user["givenName"],
                 familyName=user["familyName"],
                 password=user["password"],
                 status=user_status_bool,
                 lang=user["lang"] if user.get("lang") else "en",
                 sysadmin=sysadmin,
                 in_projects=project_info,
                 in_groups=group_ids).create()
            if verbose:
                print(f"Created user {username}.")
        except BaseError as err:
            print(f"ERROR while trying to create user '{username}'. The error message was: {err.message}")
            exit(1)
        except Exception as exception:
            print(f"ERROR while trying to create user '{username}'. The error message was: {exception}")
            exit(1)


def sort_resources(unsorted_resources: list[dict[str, Any]], onto_name: str) -> list[dict[str, Any]]:
    """
    This method sorts the resource classes in an ontology according their inheritance order
    (parent classes first).

    Args:
        unsorted_resources: list of resources from a JSON ontology definition
        onto_name: name of the onto

    Returns:
        sorted list of resource classes
    """
    
    # do not modify the original unsorted_resources, which points to the original onto file
    resources_to_sort = unsorted_resources.copy()
    sorted_resources: list[dict[str, Any]] = list()
    ok_resource_names: list[str] = list()
    while len(resources_to_sort) > 0:
        # inside the for loop, resources_to_sort is modified, so a copy must be made
        # to iterate over
        for res in resources_to_sort.copy():
            res_name = f'{onto_name}:{res["name"]}'
            parent_classes = res['super']
            if isinstance(parent_classes, str):
                parent_classes = [parent_classes]
            parent_classes = [re.sub(r'^:([^:]+)$', f'{onto_name}:\\1', elem) for elem in parent_classes]
            parent_classes_ok = [not parent.startswith(onto_name) or parent in ok_resource_names for parent in parent_classes]
            if all(parent_classes_ok):
                sorted_resources.append(res)
                ok_resource_names.append(res_name)
                resources_to_sort.remove(res)
    return sorted_resources


def sort_prop_classes(unsorted_prop_classes: list[dict[str, Any]], onto_name: str) -> list[dict[str, Any]]:
    """
        In case of inheritance, parent properties must be uploaded before their children. This method sorts the
        properties.

        Args:
            unsorted_prop_classes: list of properties from a JSON ontology definition
            onto_name: name of the onto

        Returns:
            sorted list of properties
        """

    # do not modify the original unsorted_prop_classes, which points to the original onto file
    prop_classes_to_sort = unsorted_prop_classes.copy()
    sorted_prop_classes: list[dict[str, Any]] = list()
    ok_propclass_names: list[str] = list()
    while len(prop_classes_to_sort) > 0:
        # inside the for loop, resources_to_sort is modified, so a copy must be made
        # to iterate over
        for prop in prop_classes_to_sort.copy():
            prop_name = f'{onto_name}:{prop["name"]}'
            parent_classes = prop.get('super', 'hasValue')
            if isinstance(parent_classes, str):
                parent_classes = [parent_classes]
            parent_classes = [re.sub(r'^:([^:]+)$', f'{onto_name}:\\1', elem) for elem in parent_classes]
            parent_classes_ok = [not parent.startswith(onto_name) or parent in ok_propclass_names for parent in parent_classes]
            if all(parent_classes_ok):
                sorted_prop_classes.append(prop)
                ok_propclass_names.append(prop_name)
                prop_classes_to_sort.remove(prop)
    return sorted_prop_classes


def create_ontology(input_file: str,
                    lists_file: str,
                    server: str,
                    user_mail: str,
                    password: str,
                    verbose: bool,
                    dump: bool) -> None:
    """
    Creates the ontology and all its parts from a JSON input file on a DSP server

    Args:
        input_file: The input JSON file from which the ontology and its parts should be created
        lists_file: The file which the list output (list node ID) is written to
        server: The DSP server which the ontology should be created on
        user_mail: The user (e-mail) which the ontology should be created with (requesting user)
        password: The password for the user (requesting user)
        verbose: Prints more information if set to True
        dump: Dumps test files (JSON) for DSP API requests if set to True

    Returns:
        None
    """

    knora_api_prefix = "knora-api:"

    # read the ontology from the input file
    with open(input_file) as f:
        onto_json_str = f.read()

    data_model = json.loads(onto_json_str)

    # expand all lists referenced in the list section of the data model and add them to the ontology
    data_model["project"]["lists"] = expand_lists_from_excel(data_model)

    # validate the ontology
    if not validate_ontology(data_model):
        exit(1)

    # make the connection to the server
    con = login(server=server, user=user_mail, password=password)

    if dump:
        con.start_logging()

    # read the prefixes of external ontologies that may be used
    context = Context(data_model.get("prefixes") or {})

    # check if the project exists
    project = None
    try:
        project = Project(con=con, shortcode=data_model["project"]["shortcode"]).read()
    except BaseError:
        pass

    # if project exists, update it
    if project:
        print(f"Project '{data_model['project']['shortcode']}' already exists. Updating it...")
        updated_project: Project = update_project(project=project, data_model=data_model, verbose=verbose)
        if verbose:
            updated_project.print()

    # if project does not exist, create it
    else:
        if verbose:
            print("Create project...")
        project = create_project(con=con, data_model=data_model, verbose=verbose)

    # create the list(s), skip if it already exists
    list_root_nodes = {}
    if data_model["project"].get("lists"):
        if verbose:
            print("Create lists...")
        list_root_nodes = create_lists(input_file, lists_file, server, user_mail, password, verbose)

    # create the group(s), skip if it already exists
    new_groups = {}
    if data_model["project"].get("groups"):
        if verbose:
            print("Create groups...")
        new_groups = create_groups(con=con, groups=data_model["project"]["groups"], project=project, verbose=verbose)

    # create or update the user(s), skip if it already exists
    if data_model["project"].get("users"):
        if verbose:
            print("Create users...")
        create_users(con=con, users=data_model["project"]["users"], groups=new_groups, project=project,
                     verbose=verbose)

    # create the ontologies
    if verbose:
        print("Create ontologies...")
    for ontology in data_model.get("project").get("ontologies"):
        new_ontology = None
        last_modification_date = None
        ontology_name = ontology["name"]
        try:
            new_ontology = Ontology(con=con,
                                    project=project,
                                    label=ontology["label"],
                                    name=ontology_name).create()
            context.add_context(new_ontology.name, new_ontology.id + ('#' if not new_ontology.id.endswith('#') else ''))
            last_modification_date = new_ontology.lastModificationDate
            if verbose:
                print(f"Created ontology '{ontology_name}'.")
        except BaseError as err:
            print(
                f"ERROR while trying to create ontology '{ontology_name}'. The error message was: {err.message}")
            exit(1)
        except Exception as exception:
            print(f"ERROR while trying to create ontology '{ontology_name}'. The error message was: {exception}")
            exit(1)

        # add the prefixes defined in the json file
        for prefix, ontology_info in context:
            if prefix not in new_ontology.context and ontology_info:
                s = ontology_info.iri + ("#" if ontology_info.hashtag else "")
                new_ontology.context.add_context(prefix, s)

        # create the empty resource classes
        new_res_classes: dict[str, ResourceClass] = {}
        sorted_resources = sort_resources(ontology["resources"], ontology["name"])
        for res_class in sorted_resources:
            res_name = res_class.get("name")
            super_classes = res_class.get("super")
            if isinstance(super_classes, str):
                super_classes = [super_classes]
            res_label = LangString(res_class.get("labels"))
            res_comment = res_class.get("comments")
            if res_comment:
                res_comment = LangString(res_comment)
            # if no cardinalities are submitted, don't create the class
            if not res_class.get("cardinalities"):
                print(f"ERROR while trying to add cardinalities to class '{res_name}'. No cardinalities submitted. At"
                      f"least one direct cardinality is required to create a class with dsp-tools.")
                continue

            new_res_class: Optional[ResourceClass] = None
            try:
                last_modification_date, new_res_class = ResourceClass(con=con,
                                                                      context=new_ontology.context,
                                                                      ontology_id=new_ontology.id,
                                                                      name=res_name,
                                                                      superclasses=super_classes,
                                                                      label=res_label,
                                                                      comment=res_comment).create(
                    last_modification_date)
            except BaseError as err:
                print(
                    f"ERROR while trying to create resource class '{res_name}'. The error message was: {err.message}")
            except Exception as exception:
                print(
                    f"ERROR while trying to create resource class '{res_name}'. The error message was: {exception}")

            if new_res_class:
                if isinstance(new_res_class.id, str):
                    new_res_classes[new_res_class.id] = new_res_class
                new_ontology.lastModificationDate = last_modification_date

                if verbose:
                    print("Created resource class:")
                    new_res_class.print()

        # create the property classes
        sorted_prop_classes = sort_prop_classes(ontology["properties"], ontology["name"])
        for prop_class in sorted_prop_classes:
            prop_name = prop_class.get("name")
            prop_label = LangString(prop_class.get("labels"))

            # get the super-property/ies if defined, valid forms are:
            #   - "prefix:super-property" : fully qualified name of property in another ontology. The prefix has to be
            #     defined in the prefixes part.
            #   - "super-property" : super-property defined in the knora-api ontology
            #   - if omitted, "knora-api:hasValue" is assumed

            if prop_class.get("super"):
                super_props = []
                for super_class in prop_class.get("super"):
                    if ':' in super_class:
                        super_props.append(super_class)
                    else:
                        super_props.append(knora_api_prefix + super_class)
            else:
                super_props = ["knora-api:hasValue"]

            # get the "object" if defined, valid forms are:
            #   - "prefix:object_name" : fully qualified object. The prefix has to be defined in the prefixes part.
            #   - ":object_name" : The object is defined in the current ontology.
            #   - "object_name" : The object is defined in "knora-api"

            if prop_class.get("object"):
                tmp_group_name = prop_class.get("object").split(':')
                if len(tmp_group_name) > 1:
                    if tmp_group_name[0]:
                        prop_object = prop_class.get("object")  # fully qualified name
                    else:
                        prop_object = new_ontology.name + ':' + tmp_group_name[1]  # object refers to actual ontology
                else:
                    prop_object = knora_api_prefix + prop_class.get("object")  # object refers to knora-api
            else:
                prop_object = None
            prop_subject = prop_class.get("subject")
            gui_element = prop_class.get("gui_element")
            gui_attributes = prop_class.get("gui_attributes")
            if gui_attributes and gui_attributes.get("hlist"):
                gui_attributes["hlist"] = "<" + list_root_nodes[gui_attributes["hlist"]]["id"] + ">"
            prop_comment = prop_class.get("comments")
            if prop_comment:
                prop_comment = LangString(prop_comment)

            new_prop_class = None
            try:
                last_modification_date, new_prop_class = PropertyClass(con=con,
                                                                       context=new_ontology.context,
                                                                       label=prop_label,
                                                                       name=prop_name,
                                                                       ontology_id=new_ontology.id,
                                                                       superproperties=super_props,
                                                                       object=prop_object,
                                                                       subject=prop_subject,
                                                                       gui_element="salsah-gui:" + gui_element,
                                                                       gui_attributes=gui_attributes,
                                                                       comment=prop_comment).create(
                    last_modification_date)
            except BaseError as err:
                print(
                    f"ERROR while trying to create property class '{prop_name}'. The error message was: {err.message}"
                )
            except Exception as exception:
                print(
                    f"ERROR while trying to create property class '{prop_name}'. The error message was: {exception}")

            if new_prop_class:
                new_ontology.lastModificationDate = last_modification_date
                if verbose:
                    print("Created property:")
                    new_prop_class.print()

        # Add cardinalities to class
        switcher = {
            "1": Cardinality.C_1,
            "0-1": Cardinality.C_0_1,
            "0-n": Cardinality.C_0_n,
            "1-n": Cardinality.C_1_n
        }

        for res_class in ontology.get("resources"):
            if res_class.get("cardinalities"):
                for card_info in res_class.get("cardinalities"):
                    rc = new_res_classes.get(new_ontology.id + "#" + res_class.get("name"))
                    cardinality = switcher[card_info.get("cardinality")]
                    prop_name_for_card = card_info.get("propname")
                    tmp_group_name = prop_name_for_card.split(":")
                    if len(tmp_group_name) > 1:
                        if tmp_group_name[0]:
                            prop_id = prop_name_for_card  # fully qualified name
                        else:
                            prop_id = new_ontology.name + ":" + tmp_group_name[1]  # prop name refers to actual ontology
                    else:
                        prop_id = knora_api_prefix + prop_name_for_card  # prop name refers to knora-api

                    if rc:
                        try:
                            last_modification_date = rc.addProperty(
                                property_id=prop_id,
                                cardinality=cardinality,
                                gui_order=card_info.get("gui_order"),
                                last_modification_date=last_modification_date)
                            if verbose:
                                print(f"{res_class['name']}: Added property '{prop_name_for_card}'")

                        except BaseError as err:
                            print(
                                f"ERROR while trying to add cardinality '{prop_id}' to resource class {res_class.get('name')}."
                                f"The error message was: {err.message}")
                        except Exception as exception:
                            print(
                                f"ERROR while trying to add cardinality '{prop_id}' to resource class {res_class.get('name')}."
                                f"The error message was: {exception}")

                        new_ontology.lastModificationDate = last_modification_date
