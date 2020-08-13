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

from onto_validate import validate_list, validate_ontology
from onto_create_lists import create_lists
from onto_create_ontology import create_ontology


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

