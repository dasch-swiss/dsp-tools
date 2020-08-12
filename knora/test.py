import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
import sys

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

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Context):
            return obj.toJsonObj()
        return json.JSONEncoder.default(self, obj)

def program(args):
    #
    # parse the arguments of the command line
    #
    parser = argparse.ArgumentParser()
    #parser.add_argument("datamodelfile", help="path to data model file")
    parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
    parser.add_argument("-u", "--user", type=str, default="root@example.com", help="Username for Knora")
    parser.add_argument("-p", "--password", type=str, default="test", help="The password for login")
    parser.add_argument("-c", "--shortcode", type=str, help="Shortcode of the project")
    parser.add_argument("-n", "--shortname", type=str, help="Shortname of the project")
    parser.add_argument("-i", "--iri", type=str, help="Project iri")
    args = parser.parse_args(args)

    current_dir = os.path.dirname(os.path.realpath(__file__))

    #
    # Connect to the DaSCH Service Platform API
    #
    con = Connection(args.server)
    #con.login(args.user, args.password)

    #
    # First we get the project information...
    #
    if args.shortcode:
        project = Project(con=con, shortcode=args.shortcode)
    elif args.shortname:
        project = Project(con=con, shortname=args.shortname)
    elif args.iri:
        project = Project(con=con, shortname=args.iri)
    else:
        print("ERROR")
        exit(-1)
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

    with open('data.json', 'w', encoding='utf8') as outfile:
        json.dump(umbrella, outfile, indent=3, ensure_ascii=False)

    print(ontology.context)

def main():
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])
