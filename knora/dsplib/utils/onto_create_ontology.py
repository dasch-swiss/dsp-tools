"""This module handles the ontology creation and upload to a DSP server. This includes the creation and upload of lists."""
import json
from typing import Dict, List, Optional, Set

from .expand_all_lists import expand_lists_from_excel
from .onto_create_lists import create_lists
from .onto_validate import validate_ontology
from ..models.connection import Connection
from ..models.group import Group
from ..models.helpers import BaseError, Cardinality, Context
from ..models.langstring import LangString
from ..models.ontology import Ontology
from ..models.project import Project
from ..models.propertyclass import PropertyClass
from ..models.resourceclass import ResourceClass
from ..models.user import User


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


def create_ontology(input_file: str,
                    lists_file: Optional[str],
                    server: str,
                    user: str,
                    password: str,
                    verbose: bool,
                    dump: bool) -> bool:
    """
    Creates the ontology from a json input file on a DSP server

    Args:
        input_file: The input json file from which the ontology should be created
        lists_file: The file which the output (list node ID) is written to
        server: The DSP server which the ontology should be created on
        user: The user which the ontology should be created with
        password: The password for the user
        verbose: Prints some more information
        dump: Dumps test files (json) for DSP API requests if True

    Returns:
        True if successful
    """
    # read the ontology from the input file
    with open(input_file) as f:
        onto_json_str = f.read()

    data_model = json.loads(onto_json_str)

    # expand all lists referenced in the list section of the data model
    new_lists = expand_lists_from_excel(data_model)

    # add the newly created lists from Excel to the ontology
    data_model['project']['lists'] = new_lists

    # validate the ontology
    if validate_ontology(data_model):
        pass
    else:
        quit()

    # make the connection to the server
    con = login(server=server,
                user=user,
                password=password)

    if dump:
        con.start_logging()

    # read the prefixes of external ontologies that may be used
    context = Context(data_model["prefixes"])

    # create or update the project
    project = None
    try:
        # try to read the project to check if it exists
        project = Project(con=con, shortcode=data_model["project"]["shortcode"]).read()

        # update the project with data from data_model
        if project.shortname != data_model["project"]["shortname"]:
            project.shortname = data_model["project"]["shortname"]
        if project.longname != data_model["project"]["longname"]:
            project.longname == data_model["project"]["longname"]
        project.description = data_model["project"].get("descriptions")
        project.keywords = set(data_model["project"].get("keywords"))
        updated_project = project.update()
        if updated_project is not None:
            project = updated_project
        if verbose:
            print("Modified project:")
            project.print()
    except:
        # create the project if it does not exist
        try:
            project = Project(con=con,
                              shortcode=data_model["project"]["shortcode"],
                              shortname=data_model["project"]["shortname"],
                              longname=data_model["project"]["longname"],
                              description=LangString(data_model["project"].get("descriptions")),
                              keywords=set(data_model["project"].get("keywords")),
                              selfjoin=False,
                              status=True).create()
        except BaseError as err:
            print("Creating project failed: ", err.message)
            return False
        if verbose:
            print("Created project:")
            project.print()
    assert project is not None

    # create the lists
    list_root_nodes = create_lists(input_file, lists_file, server, user, password, verbose)

    # create the groups
    if verbose:
        print("Create groups...")

    new_groups = {}
    groups = data_model["project"].get('groups')
    if groups is not None:
        for group in groups:
            try:
                new_group = Group(con=con,
                                  name=group["name"],
                                  description=group["description"],
                                  project=project,
                                  status=group["status"] if group.get("status") is not None else True,
                                  selfjoin=group["selfjoin"] if group.get("selfjoin") is not None else False).create()
            except BaseError as err:
                print("Creating group has failed: ", err.message)
                return False
            new_groups[new_group.name] = new_group
            if verbose:
                print("Groups:")
                new_group.print()  # project.set_default_permissions(new_group.id)

    # create the users
    if verbose:
        print("Create users...")
    all_groups: List[Group] = []
    all_projects: List[Project] = []
    users = data_model["project"].get('users')
    if users is not None:
        for user in users:
            sysadmin = False
            group_ids: Set[str] = set()
            for groupname in user["groups"]:
                #
                # First we determine the groups the user is in because we can do this in one call
                # groupname has the form [proj_shortname]:groupname|"SystemAdmin"
                # (projectname omitted = current project)
                #
                tmp = groupname.split(':')
                if len(tmp) > 1:
                    group = None
                    if tmp[0] and tmp[0] != '':
                        # we have 'proj_shortname:groupname
                        if not all_groups:
                            all_groups = Group.getAllGroups(con)
                        tmp_group = list(filter(lambda g: g.project.shortname == tmp[0] and g.name == tmp[1], all_groups))
                        assert len(tmp_group) == 1
                        group = tmp_group[0]
                    else:
                        # we have ':groupname' and add to current project
                        group = new_groups.get(tmp[1])
                        assert group is not None
                    group_ids.add(group.id)
                else:
                    if tmp[0] == "SystemAdmin":
                        sysadmin = True

            project_infos: Dict[str, bool] = {}
            for projectname in user["projects"]:
                # determine the project memberships of the user
                # projectname has the form [projectname]:"member"|"admin" (projectname omitted = current project)
                tmp = projectname.split(':')
                assert len(tmp) == 2
                if tmp[0]:
                    # we have 'proj_shortname:"member"|"admin"'
                    if not all_projects:
                        all_projects = project.getAllProjects(con)
                    tmp_project = list(filter(lambda g: g.shortname == tmp[0], all_projects))
                    assert len(tmp_project) == 1
                    in_project = tmp_project[0]
                else:
                    # we have ':"member"|"admin"'
                    in_project = project
                if tmp[1] == "admin":
                    project_infos[in_project.id] = True
                else:
                    project_infos[in_project.id] = False
            user_existing = False
            tmp_user = None
            try:
                tmp_user = User(con,
                                username=user["username"]).read()
            except BaseError as err:
                pass
            if tmp_user is None:
                try:
                    tmp_user = User(con,
                                    email=user["email"]).read()
                except BaseError as err:
                    pass
            if tmp_user:
                # if the user exists already, update his settings
                if tmp_user.username != user["username"]:
                    tmp_user.username = user["username"]
                if tmp_user.email != user["email"]:
                    tmp_user.email = user["email"]
                if tmp_user.givenName != user["givenName"]:
                    tmp_user.givenName = user["givenName"]
                if tmp_user.familyName != user["familyName"]:
                    tmp_user.familyName = user["familyName"]
                if tmp_user.password != user["password"]:
                    tmp_user.password = user["password"]
                if user.get("status") and tmp_user.status != user["status"]:
                    tmp_user.status = user["status"]
                if user.get("lang") and tmp_user.lang != user["lang"]:
                    tmp_user.lang = user["lang"]
                if tmp_user.sysadmin != sysadmin:
                    tmp_user.sysadmin = sysadmin
                try:
                    tmp_user.update()
                except BaseError as err:
                    tmp_user.print()
                    print("Updating user failed:", err.message)
                    return False

                # update group and project membership
                # Note: memberships are NOT removed here, just added
                tmp_in_groups = tmp_user.in_groups
                add_groups = group_ids - tmp_in_groups
                for g in add_groups:
                    User.addToGroup(g)
                rm_groups = tmp_in_groups - group_ids
                # we do no remove a user from a group here!
                tmp_in_projects = tmp_user.in_projects
                for p in project_infos.items():
                    if tmp_in_projects.get(p[0]) and tmp_in_projects[p[0]] == p[1]:
                        continue
                    User.addToProject(p[0], p[1])
            else:
                # if the user does not exist yet, create him
                try:
                    new_user = User(con=con,
                                    username=user["username"],
                                    email=user["email"],
                                    givenName=user["givenName"],
                                    familyName=user["familyName"],
                                    password=user["password"],
                                    status=user["status"] if user.get("status") is not None else True,
                                    lang=user["lang"] if user.get("lang") is not None else "en",
                                    sysadmin=sysadmin,
                                    in_projects=project_infos,
                                    in_groups=group_ids).create()
                except BaseError as err:
                    print("Creating user failed:", err.message)
                    return False
            if verbose:
                print("New user:")
                new_user.print()

    # create the ontologies
    if verbose:
        print("Create ontologies...")
    ontologies = data_model["project"]["ontologies"]
    for ontology in ontologies:
        newontology = Ontology(con=con,
                               project=project,
                               label=ontology["label"],
                               name=ontology["name"]).create()
        last_modification_date = newontology.lastModificationDate
        if verbose:
            print("Created empty ontology:")
            newontology.print()

        # add the prefixes defined in the json file
        for prefix, iri in context:
            if not prefix in newontology.context:
                s = iri.iri + ("#" if iri.hashtag else "")
                newontology.context.add_context(prefix, s)

        # create the empty resource classes
        resclasses = ontology["resources"]
        newresclasses: Dict[str, ResourceClass] = {}
        for resclass in resclasses:
            resname = resclass.get("name")
            super_classes = resclass.get("super")
            if isinstance(super_classes, str):
                super_classes = [super_classes]
            reslabel = LangString(resclass.get("labels"))
            rescomment = resclass.get("comment")
            if rescomment is not None:
                rescomment = LangString(rescomment)
            try:
                last_modification_date, newresclass = ResourceClass(con=con,
                                                                    context=newontology.context,
                                                                    ontology_id=newontology.id,
                                                                    name=resname,
                                                                    superclasses=super_classes,
                                                                    label=reslabel,
                                                                    comment=rescomment).create(last_modification_date)
                newontology.lastModificationDate = last_modification_date
            except BaseError as err:
                print("Creating resource class failed:", err.message)
                exit(105)
            newresclasses[newresclass.id] = newresclass
            if verbose is not None:
                print("New resource class:")
                newresclass.print()

        # create the property classes
        propclasses = ontology["properties"]
        newpropclasses: Dict[str, ResourceClass] = {}
        for propclass in propclasses:
            propname = propclass.get("name")
            proplabel = LangString(propclass.get("labels"))
            # get the super-property/ies if defined. Valid forms are:
            #   - "prefix:superproperty" : fully qualified name of property in another ontology. The prefix has to
            #     be defined in the prefixes part.
            #   - "superproperty" : Use of super-property defined in the knora-api ontology
            #  if omitted, "knora-api:hasValue" is assumed
            if propclass.get("super") is not None:
                super_props = list(map(lambda a: a if ':' in a else "knora-api:" + a, propclass["super"]))
            else:
                super_props = ["knora-api:hasValue"]
            # get the "object" if defined. Valid forms are:
            #  - "prefix:object_name" : fully qualified object. The prefix has to be defined in the prefixes part.
            #  - ":object_name" : The object is defined in the current ontology.
            #  - "object_name" : The object is defined in "knora-api"
            if propclass.get("object") is not None:
                tmp = propclass["object"].split(':')
                if len(tmp) > 1:
                    if tmp[0]:
                        object = propclass["object"]  # fully qualified name
                    else:
                        newontology.print()
                        object = newontology.name + ':' + tmp[1]
                else:
                    object = "knora-api:" + propclass["object"]
            else:
                object = None

            if propclass.get("subject") is not None:
                subject = propclass["subject"]
            else:
                subject = None
            gui_element = propclass.get("gui_element")
            gui_attributes = propclass.get("gui_attributes")
            if gui_attributes is not None and gui_attributes.get("hlist") is not None:
                gui_attributes['hlist'] = "<" + list_root_nodes[gui_attributes['hlist']]["id"] + ">"
            propcomment = propclass.get("comment")
            if propcomment is not None:
                propcomment = LangString(propcomment)
            else:
                propcomment = "no comment given"
            try:
                last_modification_date, newpropclass = PropertyClass(con=con,
                                                                     context=newontology.context,
                                                                     label=proplabel,
                                                                     name=propname,
                                                                     ontology_id=newontology.id,
                                                                     superproperties=super_props,
                                                                     object=object,
                                                                     subject=subject,
                                                                     gui_element="salsah-gui:" + gui_element,
                                                                     gui_attributes=gui_attributes,
                                                                     comment=propcomment).create(last_modification_date)
                newontology.lastModificationDate = last_modification_date
            except BaseError as err:
                print("Creating property class failed:", err.message)
                return False
            newpropclasses[newpropclass.id] = newpropclass
            if verbose:
                print("New property class:")
                newpropclass.print()

        # Add cardinalities
        switcher = {
            "1": Cardinality.C_1,
            "0-1": Cardinality.C_0_1,
            "0-n": Cardinality.C_0_n,
            "1-n": Cardinality.C_1_n
        }
        for resclass in resclasses:
            for cardinfo in resclass["cardinalities"]:
                rc = newresclasses.get(newontology.id + '#' + resclass["name"])
                cardinality = switcher[cardinfo["cardinality"]]
                tmp = cardinfo["propname"].split(':')
                if len(tmp) > 1:
                    if tmp[0]:
                        propid = cardinfo["propname"]  # fully qualified name
                    else:
                        propid = newontology.name + ':' + tmp[1]
                else:
                    propid = "knora-api:" + cardinfo["propname"]
                gui_order = cardinfo.get('gui_order')
                last_modification_date = rc.addProperty(
                        property_id=propid,
                        cardinality=cardinality,
                        gui_order=gui_order,
                        last_modification_date=last_modification_date)
                newontology.lastModificationDate = last_modification_date
    return True
