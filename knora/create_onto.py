import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
import sys
import re

from models.helpers import Actions, BaseError, Context, Cardinality
from models.langstring import Languages, LangStringParam, LangString
from models.connection import Connection, Error
from models.project import Project
from models.listnode import ListNode
from models.group import Group
from models.user import User
from models.ontology import Ontology
from models.propertyclass import PropertyClass
from models.resourceclass import ResourceClass


def validate_list(input_file: str) -> None:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # let's read the schema for the data model definition
    with open(os.path.join(current_dir, 'knora-schema-lists.json')) as s:
        schema = json.load(s)
    # read the data model definition
    with open(input_file) as f:
        datamodel = json.load(f)

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)
    print("Data model is syntactically correct and passed validation!")


def validate_ontology(input_file: str) -> None:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(current_dir, 'knora-schema.json')) as s:
        schema = json.load(s)
    # read the data model definition
    with open(input_file) as f:
        datamodel = json.load(f)

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)
    print("Data model is syntactically correct and passed validation!")

def create_lists (input_file: str, output_file: str, server: str, user: str, password: str, verbose: bool) -> bool:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # let's read the schema for the data model definition
    with open(os.path.join(current_dir, 'knora-schema-lists.json')) as s:
        schema = json.load(s)
    # read the data model definition
    with open(input_file) as f:
        datamodel = json.load(f)

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)
    if verbose:
        print("Data model is syntactically correct and passed validation!")

    #
    # Connect to the DaSCH Service Platform API
    #
    con = Connection(server)
    con.login(user, password)

    # --------------------------------------------------------------------------
    # let's read the prefixes of external ontologies that may be used
    #
    context = Context(datamodel["prefixes"])

    # --------------------------------------------------------------------------
    # Let's get the project which must exist
    #
    project = Project(
        con=con,
        shortcode=datamodel["project"]["shortcode"],
    ).read()
    assert project is not None

    # --------------------------------------------------------------------------
    # now let's create the lists
    #
    if verbose:
        print("Creating lists...")
    lists = datamodel["project"].get('lists')
    listrootnodes = {}
    if lists is not None:
        for rootnode in lists:
            if verbose is not None:
                print("  Creating list:" + rootnode['name'])
            root_list_node = ListNode(
                con=con,
                project=project,
                label=rootnode['labels'],
                comment=rootnode.get('comments'),
                name=rootnode['name']
            ).create()
            listnodes = list_creator(con, project, root_list_node, rootnode['nodes'])
            listrootnodes[rootnode['name']] = {
                "id": root_list_node.id,
                "nodes": listnodes
            }

    with open(output_file, 'w', encoding="utf-8") as fp:
        json.dump(listrootnodes, fp, indent=3, sort_keys=True)
        print("The definitions of the node-id's can be found in \"{}}\"!".format(output_file))
    return True


def create_ontology(input_file: str, lists_file: str, server: str, user: str, password: str, verbose: bool) -> bool:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # let's read the schema for the data model definition
    with open(os.path.join(current_dir, 'knora-schema.json')) as s:
        schema = json.load(s)

    # read the data model definition
    with open(input_file) as f:
        datamodel = json.load(f)

    # validate the data model definition in order to be sure that it is correct
    validate(datamodel, schema)
    if verbose:
        print("Data model is syntactically correct and passed validation!")

    #
    # Connect to the DaSCH Service Platform API
    #
    con = Connection(server)
    con.login(user, password)

    # --------------------------------------------------------------------------
    # let's read the prefixes of external ontologies that may be used
    #
    context = Context(datamodel["prefixes"])

    # --------------------------------------------------------------------------
    # Let's create the project...
    #
    project = None
    try:
        # we try to read the project to see if it's existing....
        project = Project(
            con=con,
            shortcode=datamodel["project"]["shortcode"],
        ).read()
        #
        # we got it, update the project data if necessary...
        #
        if project.shortname != datamodel["project"]["shortname"]:
            project.shortname = datamodel["project"]["shortname"]
        if project.longname != datamodel["project"]["longname"]:
            project.longname == datamodel["project"]["longname"]
        project.description = datamodel["project"].get("descriptions")
        project.keywords = set(datamodel["project"].get("keywords"))
        nproject = project.update()
        if nproject is not None:
            project = nproject
        if verbose:
            print("Modified project:")
            project.print()
    except:
        #
        # The project doesn't exist yet – let's create it
        #
        try:
            project = Project(
                con=con,
                shortcode=datamodel["project"]["shortcode"],
                shortname=datamodel["project"]["shortname"],
                longname=datamodel["project"]["longname"],
                description=LangString(datamodel["project"].get("descriptions")),
                keywords=set(datamodel["project"].get("keywords")),
                selfjoin=False,
                status=True
            ).create()
        except BaseError as err:
            print("Creating project failed: " + err.message)
            return False
        if verbose:
            print("Created project:")
            project.print()
    assert project is not None

    # --------------------------------------------------------------------------
    # now let's create the lists
    #
    if verbose:
        print("Creating lists...")
    lists = datamodel["project"].get('lists')
    listrootnodes = {}
    if lists is not None:
        for rootnode in lists:
            if verbose is not None:
                print("  Creating list:" + rootnode['name'])
            root_list_node = ListNode(
                con=con,
                project=project,
                label=rootnode['labels'],
                comment=rootnode.get('comments'),
                name=rootnode['name']
            ).create()
            listnodes = list_creator(con, project, root_list_node, rootnode['nodes'])
            listrootnodes[rootnode['name']] = {
                "id": root_list_node.id,
                "nodes": listnodes
            }

    with open('lists.json', 'w', encoding="utf-8") as fp:
        json.dump(listrootnodes, fp, indent=3, sort_keys=True)
        print("The definitions of the node-id's can be found in \"{}\"!".format('lists.json'))

    # --------------------------------------------------------------------------
    # now let's add the groups (if there are groups defined...)
    #
    if verbose:
        print("Adding groups...")

    new_groups = {}
    groups = datamodel["project"].get('groups')
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
                print("Creating group failed: " + err.message)
                return False
            new_groups[new_group.name] = new_group
            if verbose:
                print("Groups:")
                new_group.print()

    # --------------------------------------------------------------------------
    # now let's add the users (if there are users defined...)
    #
    if verbose:
        print("Adding users...")
    all_groups: List[Group] = []
    all_projects: List[Project] = []
    users = datamodel["project"].get('users')
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
                #
                # now we determine the project memberships of the user
                # projectname has the form [projectname]:"member"|"admin" (projectname omitted = current project)
                #
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
            user_existing = False;
            tmp_user = None
            try:
                tmp_user = User(con, username=user["username"]).read()
            except Error as err:
                pass
            if tmp_user is None:
                try:
                    tmp_user = User(con, email=user["email"]).read()
                except Error as err:
                    pass
            if tmp_user:
                #
                # The user is already in the database – let's update its settings
                #
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
                except Error as err:
                    tmp_user.print()
                    print("Updating user failed: " + err.message)
                    return False
                #
                # now we update group and project membership
                # Note: we do NOT remove any mambership here, we just add!
                #
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
                #
                # The user does not exist yet, let's create a new one
                #
                try:
                    new_user = User(
                        con=con,
                        username=user["username"],
                        email=user["email"],
                        givenName=user["givenName"],
                        familyName=user["familyName"],
                        password=user["password"],
                        status=user["status"] if user.get("status") is not None else True,
                        lang=user["lang"] if user.get("lang") is not None else "en",
                        sysadmin=sysadmin,
                        in_projects=project_infos,
                        in_groups=group_ids
                    ).create()
                except Error as err:
                    print("Creating user failed: " + err.message)
                    return False
            if verbose:
                print("New user:")
                new_user.print()

    # --------------------------------------------------------------------------
    # now let's create the ontologies
    #
    ontologies = datamodel["project"]["ontologies"]
    for ontology in ontologies:
        last_modification_date, newontology = Ontology(
            con=con,
            project=project,
            label=ontology["label"],
            name=ontology["name"]
        ).create()
        if verbose:
            print("Created empty ontology:")
            newontology.print()

        #
        # First we create the empty resource classes
        #
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
                last_modification_date, newresclass = ResourceClass(
                    con=con,
                    context=newontology.context,
                    ontology_id=newontology.id,
                    name=resname,
                    superclasses=super_classes,
                    label=reslabel,
                    comment=rescomment
                ).create(last_modification_date)
            except Error as err:
                print("Creating resource class failed: " + err.message)
                exit(105)
            newresclasses[newresclass.id] = newresclass
            if verbose is not None:
                print("New resource class:")
                newresclass.print()

        #
        # Then we create the property classes
        #
        propclasses = ontology["properties"]
        newpropclasses: Dict[str, ResourceClass] = {}
        for propclass in propclasses:
            propname = propclass.get("name")
            proplabel = LangString(propclass.get("labels"))
            #
            # get the super-property/ies if defined. Valid forms are:
            #   - "prefix:superproperty" : fully qualified name of property in another ontology. The prefix has to
            #     be defined in the prefixes part.
            #   - "superproperty" : Use of super-property defined in the knora-api ontology
            #  if omitted, automatically "knora-api:hasValue" is assumed
            #
            if propclass.get("super") is not None:
                super_props = list(map(lambda a: a if ':' in a else "knora-api:" + a, propclass["super"]))
            else:
                super_props = ["knora-api:hasValue"]
            #
            # now we get the "object" if defined. Valid forms are:
            #  - "prefix:object_name" : fully qualified object. The prefix has to be defined in the prefixes part.
            #  - ":object_name" : The object is defined in the current ontology.
            #  - "object_name" : The object is defined in "knora-api"
            #
            if propclass.get("object") is not None:
                tmp = propclass["object"].split(':')
                pprint(tmp)
                if len(tmp) > 1:
                    if tmp[0]:
                        object = propclass["object"] # fully qualified name
                    else:
                        pprint(newontology)
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
                gui_attributes['hlist'] = "<" + listrootnodes[gui_attributes['hlist']]["id"] + ">"
            propcomment = propclass.get("comment")
            if propcomment is not None:
                propcomment = LangString(propcomment)
            else:
                propcomment = "no comment given"
            try:
                last_modification_date, newpropclass = PropertyClass(
                    con=con,
                    context=newontology.context,
                    label=proplabel,
                    name=propname,
                    ontology_id=newontology.id,
                    superproperties=super_props,
                    object=object,
                    subject=subject,
                    gui_element="salsah-gui:" + gui_element,
                    gui_attributes=gui_attributes,
                    comment=propcomment
                ).create(last_modification_date)
            except Error as err:
                print("Creating property class failed: " + err.message)
                return False
            newpropclasses[newpropclass.id] = newpropclass
            if verbose:
                print("New property class:")
                newpropclass.print()

        #
        # Add cardinalities
        #
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
                        propid = cardinfo["propname"] # fully qualified name
                    else:
                        propid = newontology.name + ':' + tmp[1]
                else:
                    propid = "knora-api:" + cardinfo["propname"]
                last_modification_date = rc.addProperty(propid, cardinality, last_modification_date)
    return True


def list_creator(con: Connection, project: Project, parent_node: ListNode, nodes: List[dict]):
    nodelist = []
    for node in nodes:
        newnode = ListNode(
            con=con,
            project=project,
            label=node["labels"],
            comment=node.get("comments"),
            name=node["name"],
            parent=parent_node
        ).create()
        if node.get('nodes') is not None:
            subnodelist = list_creator(con, project, newnode, node['nodes'])
            nodelist.append({newnode.name: {"id": newnode.id, 'nodes': subnodelist}})
        else:
            nodelist.append({newnode.name: {"id": newnode.id}})
    return nodelist


def get_ontology(ontoident: str, outfile: str, server: str, user: str, password: str, verbose: bool) -> bool:
    con = Connection(server)
    # con.login(user, password)
    if re.match("^[0-9aAbBcCdDeEfF]{4}$", ontoident):
        project = Project(con=con, shortcode=ontoident)
    elif re.match("^[\\w-]+$", ontoident):
        project = Project(con=con, shortname=ontoident)
    elif re.match("^(http)s?://([\\w\\.\\-~]+:?\\d{,4})(/[\\w\\-~]+)+$", ontoident):
        project = Project(con=con, shortname=ontoident)
    else:
        print("Invalid ontology identification!")
        return False

    project = project.read()

    projectobj = project.createDefinitionFileObj()

    #
    # now collect the lists
    #
    listroots = ListNode.getAllLists(con=con, project_iri=project.id)
    listobj = []
    for listroot in listroots:
        complete_list = listroot.getAllNodes()
        listobj.append(complete_list.createDefinitionFileObj())
    projectobj["lists"] = listobj

    projectobj["ontologies"] = []
    for ontology in project.ontologies:
        oparts = ontology.split("/")
        name = oparts[len(oparts) - 1]
        shortcode = oparts[len(oparts) - 2]
        lastmoddate, ontology = Ontology.getOntologyFromServer(con=con, shortcode=shortcode, name=name)
        projectobj["ontologies"].append(ontology.createDefinitionFileObj())

    umbrella = {
        "prefixes": ontology.context.get_externals_used(),
        "project": projectobj
    }

    with open(outfile, 'w', encoding='utf8') as outfile:
        json.dump(umbrella, outfile, indent=3, ensure_ascii=False)

    print(ontology.context)

def program(args):
    #
    # parse the arguments of the command line
    #
    parser = argparse.ArgumentParser(
        description="A program to create and manipulate ontologies based on the DaSCH Service Platform and Knora"
    )
    subparsers = parser.add_subparsers(title="Subcommands",
                                       description='Valid subcommands are',
                                       help='sub-command help')

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose feedback")
    parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
    parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
    parser.add_argument("-p", "--password", default="test", help="The password for login")

    parser_create = subparsers.add_parser('create', help='Create ontologies, lists etc.')
    parser_create.set_defaults(action="create")
    parser_create.add_argument("-V", "--validate", action='store_true', help="Do only validation of JSON, no upload of the ontology")
    parser_create.add_argument("datamodelfile", help="path to data model file")
    parser_create.add_argument("-L", "--listfile", type=str, default="lists.json", help="Name of list node informationfile")
    parser_create.add_argument("-l", "--lists", action='store_true', help="Only create the lists")

    parser_get = subparsers.add_parser('get', help='Get ontology information from server')
    parser_get.set_defaults(action="get")
    parser_get.add_argument("outfile", help="path to data model file", default="onto.json")
    parser_get.add_argument("-o", "--ontology", type=str, help="Shortcode, shortname or iri of ontology", required=True)

    args = parser.parse_args(args)

    if args.action == "create":
        if args.lists:
            if args.validate:
                validate_list(args.datamodelfile)
            else:
                create_lists(args.datamodelfile, args.listfile)
        else:
            if args.validate:
                validate_ontology(args.datamodelfile)
            else:
                create_ontology(args.datamodelfile, args.listfile, args.server, args.user, args.password, args.verbose)
    elif args.action == "get":
        get_ontology(args.ontology, args.outfile, args.server, args.user, args.password, args.verbose)


def main():
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])

