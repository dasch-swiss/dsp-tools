import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
from knora import KnoraError, Knora
import sys


def program(args):
    # parse the arguments of the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("ontofile", help="path to ontology file")
    parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
    parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
    parser.add_argument("-p", "--password", default="test", help="The password for login")
    parser.add_argument("-V", "--validate", action='store_true', help="Do only validation of JSON, no upload of the ontology")
    parser.add_argument("-l", "--lists", action='store_true', help="Only create the lists")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose feedback")
    args = parser.parse_args(args)

    current_dir = os.path.dirname(os.path.realpath(__file__))

    # let's read the schema for the ontology definition
    if args.lists:
        with open(os.path.join(current_dir, 'knora-schema-lists.json')) as s:
            schema = json.load(s)
    else:
        with open(os.path.join(current_dir, 'knora-schema.json')) as s:
            schema = json.load(s)

    # read the ontology definition
    with open(args.ontofile) as f:
        ontology = json.load(f)

    # validate the ontology definition in order to be sure that it is correct
    validate(ontology, schema)
    print("Ontology is syntactically correct and passed validation!")

    if args.validate:
        exit(0)

    # create the knora connection object
    con = Knora(args.server, ontology.get("prefixes"))
    con.login(args.user, args.password)

    # bulk_templ = con.create_schema(ontology["project"]["shortcode"], ontology["project"]["ontology"]["name"])

    if not args.lists:
        # create or update the project
        try:
            project = con.get_project(ontology["project"]["shortcode"])
        except KnoraError as err:
            proj_iri = con.create_project(
                shortcode=ontology["project"]["shortcode"],
                shortname=ontology["project"]["shortname"],
                longname=ontology["project"]["longname"],
                descriptions=ontology["project"].get("descriptions"),
                keywords=ontology["project"].get("keywords")
            )
        else:
            if args.verbose is not None:
                print("Updating existing project!")
            pprint(ontology["project"].get("keywords"))
            proj_iri = con.update_project(
                shortcode=ontology["project"]["shortcode"],
                shortname=ontology["project"]["shortname"],
                longname=ontology["project"]["longname"],
                descriptions=ontology["project"].get("descriptions"),
                keywords=ontology["project"].get("keywords")
            )
        project = con.get_project(ontology["project"]["shortcode"])
        if args.verbose is not None:
            print("Project-IRI: " + proj_iri)
    else:
        project = con.get_project(ontology["project"]["shortcode"])
        proj_iri = project["id"]

    #--------------------------------------------------------------------------
    # now let's create the lists
    #
    if args.verbose is not None:
        print("Creating lists...")
    lists = ontology["project"].get('lists')
    listrootnodes = {}
    if lists is not None:
        for rootnode in lists:
            if args.verbose is not None:
                print("  Creating list:" + rootnode['name'])
            rootnode_iri = con.create_list_node(
                project_iri=proj_iri,
                name=rootnode['name'],
                labels=rootnode['labels'],
                comments=rootnode.get('comments')
            )
            listnodes = list_creator(con, proj_iri, rootnode_iri, rootnode_iri, rootnode['nodes'])
            listrootnodes[rootnode['name']] = {
                "id": rootnode_iri,
                "nodes": listnodes
            }

    with open('lists.json', 'w', encoding="utf-8") as fp:
        json.dump(listrootnodes, fp, indent=3, sort_keys=True)

    if args.lists:
        print("The definitions of the node-id's can be found in \"lists.json\"!")
        exit(0)

    #--------------------------------------------------------------------------
    # now we add the groups if existing
    #
    if args.verbose is not None:
        print("Adding groups...")

    group_iris = []
    groups = ontology["project"].get('groups')
    if groups is not None:
        for group in groups:
            try:
                group_iri = con.create_group(project_iri=proj_iri,
                                             name=group["name"],
                                             description=group["description"],
                                             selfjoin=group["selfjoin"] if group.get("selfjoin") is not None else False,
                                             status=group["status"] if group.get("status") is not None else True)
            except KnoraError as err:
                print("Creating group failed: " + err.message)
            if args.verbose is not None:
                print("  Group added: " + group['name'] + ' (' + group_iri + ')')

    #--------------------------------------------------------------------------
    # now we add the users if existing
    #
    if args.verbose is not None:
        print("Adding users...")

    users = ontology["project"].get('users')
    if users is not None:
        for user in users:
            try:
                user_iri = con.create_user(username=user["username"],
                                           email=user["email"],
                                           given_name=user["givenName"],
                                           family_name=user["familyName"],
                                           password=user["password"],
                                           lang=user["lang"] if user.get("lang") is not None else "en")
            except KnoraError as err:
                print("Creating user failed: " + err.message)
            userinfo = con.get_user_by_email(email=user["email"])
            user_iri = userinfo['id']

            try:
                con.add_user_to_project(user_iri, proj_iri)
            except KnoraError as err:
                print('Adding user to project failed: ' + err.message);

            if args.verbose is not None:
                print("  User added: " + user['username'] + ' (' + user_iri + ')')

            if args.verbose is not None:
                print("  Adding " + user['username'] + " to groups...")
                groupnames = user["groups"]
                for groupname in groupnames:
                    tmp = groupname.split(':')
                    try:
                        if len(tmp) > 1:
                            if tmp[0]: # we have 'proj_shortname:groupname'
                                group_iri = con.get_group_by_pshortname_and_gname(tmp[0], tmp[1])
                            else: # we have ':groupname' and add to currnt project
                                group_iri = con.get_group_by_piri_and_gname(proj_iri, tmp[1])
                            con.add_user_to_group(user_iri, group_iri)
                            print("    " + user['username'] + " added to group " + groupname)
                        else:
                            if tmp[0] == "ProjectAdmin":
                                con.add_user_to_project_admin(user_iri, proj_iri)
                                print("    " + user['username'] + " added to group " + groupname)
                            elif tmp[0] == "SystemAdmin":
                                con.add_user_to_sysadmin(user_iri)
                                print("    " + user['username'] + " added to group " + groupname)
                            else:
                                print("    Unknown System group: " + tmp[0])
                    except KnoraError as err:
                        print('    Added user to group failed: ' + err.message);


    #--------------------------------------------------------------------------
    # now we start creating the ontology
    #
    # first we assemble the ontology IRI
    onto_iri = args.server + "/ontology/" + ontology["project"]["shortcode"]\
               + "/" + ontology["project"]["ontology"]["name"] + "/v2"

    if args.verbose is not None:
        print("Creating the ontology...")
    # test, if the ontolgy already exists. if so, let's delete it!
    ontos = con.get_project_ontologies(ontology["project"]["shortcode"])
    if ontos is not None:
        for onto in ontos:
            if onto['iri'] == onto_iri:
                try:
                    con.delete_ontology(onto_iri, onto['moddate'])
                except KnoraError as err:
                    print("Deleting ontolopgy failed: " + err.message);
    onto_data = con.create_ontology(
        onto_name=ontology["project"]["ontology"]["name"],
        project_iri=proj_iri,
        label=ontology["project"]["ontology"]["label"]
    )

    onto_iri = onto_data['onto_iri']
    last_onto_date = onto_data['last_onto_date']

    # let's create the resources
    resource_ids = {}

    if args.verbose is not None:
        print("Creating the resclasses...")
    for resource in ontology["project"]["ontology"]["resources"]:
        result = con.create_res_class(
            onto_iri=onto_iri,
            onto_name=ontology["project"]["ontology"]["name"],
            last_onto_date=last_onto_date,
            class_name=resource["name"],
            super_class=resource["super"] if ':' in resource["super"] else "knora-api:" + resource["super"],
            labels=resource["labels"]
        )
        last_onto_date = result["last_onto_date"]
        resource_ids[resource["name"]] = result["class_iri"]
        if args.verbose is not None:
            print("Created resclass: " + resource["name"])

    #
    #  find properties that have been used for multiple resources
    #
    property_names = []
    duplicate_properties = []
    for resource in ontology["project"]["ontology"]["resources"]:
        for prop in resource["properties"]:
            if prop['name'] not in property_names:
                property_names.append(prop['name'])
            else:
                duplicate_properties.append(prop['name'])

    if args.verbose is not None:
        print("Creating the properties...")
    # let's create the properties
    property_ids = {}
    property_names = []
    for resource in ontology["project"]["ontology"]["resources"]:
        for prop in resource["properties"]:
            if property_ids.get(prop['name']) is None:
                guiattrs = prop.get("gui_attributes")
                if guiattrs is not None:
                    new_guiattrs = []
                    for guiattr in guiattrs:
                        parts = guiattr.split("=")
                        if parts[0] == "hlist":
                            new_guiattrs.append("hlist=<" + listrootnodes[parts[1]]["id"] + ">")
                        else:
                            new_guiattrs.append(guiattr)
                    guiattrs = new_guiattrs

                if prop.get("super") is not None:
                    super_props = list(map(lambda a: a if ':' in a else "knora-api:" + a, prop["super"]))
                else:
                    super_props = ["knora-api:hasValue"]

                if prop.get("object") is not None:
                    tmp = prop["object"].split(':')
                    if len(tmp) > 1:
                        if tmp[0]:
                            object = prop["object"]
                        else:
                            object = ontology["project"]["ontology"]["name"] + ':' + tmp[1]
                    else:
                        object = "knora-api:" + prop["object"]
                else:
                    object = None

                if prop.get("subject") is not None:
                    psubject = prop["subject"]
                else:
                    psubject = ontology["project"]["ontology"]["name"] + ':' + resource["name"]

                result = con.create_property(
                    onto_iri=onto_iri,
                    onto_name=ontology["project"]["ontology"]["name"],
                    last_onto_date=last_onto_date,
                    prop_name=prop["name"],
                    super_props=super_props,
                    labels=prop["labels"],
                    gui_element="salsah-gui:" + prop["gui_element"],
                    gui_attributes=guiattrs,
                    subject=psubject if prop['name'] not in duplicate_properties else None,
                    object=object,
                    comments=prop.get("comments")
                )
                last_onto_date = result["last_onto_date"]
                property_ids[prop["name"]] = result['prop_iri']
                if args.verbose is not None:
                    print("Property created: {} ({})".format(prop["name"], result['prop_iri']))
            else:
                print('Property \"{}\" reused!'.format(prop["name"]))

    if args.verbose is not None:
        print("Adding cardinalities...")
    # add the cardinalities
    for resource in ontology["project"]["ontology"]["resources"]:
        for prop in resource["properties"]:
            result = con.create_cardinality(
                onto_iri=onto_iri,
                onto_name=ontology["project"]["ontology"]["name"],
                last_onto_date=last_onto_date,
                class_iri=ontology["project"]["ontology"]["name"] + ':' + resource["name"],
                prop_iri=ontology["project"]["ontology"]["name"] + ':' + prop["name"],
                occurrence=prop["cardinality"]
            )
            last_onto_date = result["last_onto_date"]
            if args.verbose is not None:
                print("Cardinality for {} added: {}".format(prop["name"], prop["cardinality"]))

    con = None  # force logout by deleting the connection object.


def list_creator(con: Knora, proj_iri: str, list_iri: str, parent_iri: str, nodes: List[dict]):
    nodelist = []
    for node in nodes:
        node_id = con.create_list_node(
            name=node["name"],
            project_iri=proj_iri,
            labels=node["labels"],
            comments=node.get("comments"),
            parent_iri=parent_iri
        )
        if node.get('nodes') is not None:
            subnodelist = list_creator(con, proj_iri, list_iri, node_id, node['nodes'])
            nodelist.append({node["name"]: {"id": node_id, 'nodes': subnodelist}})
        else:
            nodelist.append({node["name"]: {"id": node_id}})
    return nodelist


def main():
    program(sys.argv[1:])


if __name__ == '__main__':
    # print(sys.argv)
    # print(sys.argv[1:])
    program(sys.argv[1:])
