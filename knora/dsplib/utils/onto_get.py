import json
import re
from typing import Dict

from ..models.connection import Connection
from ..models.listnode import ListNode
from ..models.ontology import Ontology
from ..models.project import Project


def get_ontology(projident: str, outfile: str, server: str, user: str, password: str, verbose: bool) -> bool:
    con = Connection(server)
    # con.login(user, password)
    if re.match("^[0-9aAbBcCdDeEfF]{4}$", projident):
        project = Project(con=con, shortcode=projident)
    elif re.match("^[\\w-]+$", projident):
        project = Project(con=con, shortname=projident)
    elif re.match("^(http)s?://([\\w\\.\\-~]+:?\\d{,4})(/[\\w\\-~]+)+$", projident):
        project = Project(con=con, shortname=projident)
    else:
        print("Invalid project identification!")
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
    prefixes: Dict[str, str] = {}
    ontologies = Ontology.getProjectOntologies(con, project.id)
    ontology_ids = [x.id for x in ontologies]
    for ontology in ontology_ids:
        oparts = ontology.split("/")
        name = oparts[len(oparts) - 2]
        shortcode = oparts[len(oparts) - 3]
        ontology = Ontology.getOntologyFromServer(con=con, shortcode=shortcode, name=name)
        projectobj["ontologies"].append(ontology.createDefinitionFileObj())
        prefixes.update(ontology.context.get_externals_used())

    umbrella = {"prefixes": prefixes, "project": projectobj}

    with open(outfile, 'w', encoding='utf8') as outfile:
        json.dump(umbrella, outfile, indent=3, ensure_ascii=False)
