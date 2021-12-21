import json
import re
from typing import Dict

from ..models.connection import Connection
from ..models.listnode import ListNode
from ..models.ontology import Ontology
from ..models.project import Project


def get_ontology(project_identifier: str, outfile: str, server: str, user: str, password: str, verbose: bool) -> None:
    """
    This function returns the JSON ontology from a DSP server.

    Args:
        project_identifier : the project identifier, either shortcode, shortname or IRI of the project
        outfile : the output file the JSON content should be written to
        server : the DSP server where the data should be read from
        user : the user (e-mail) who sends the request
        password : the password of the user who sends the request
        verbose : verbose option for the command, if used more output is given to the user

    Returns:
        None
    """
    con = Connection(server)
    if user and password:
        con.login(user, password)

    project = None
    if re.match("[0-9A-F]{4}", project_identifier):  # shortcode
        project = Project(con=con, shortcode=project_identifier)
    elif re.match("^[\\w-]+$", project_identifier):  # shortname
        project = Project(con=con, shortname=project_identifier)
    elif re.match("^(http)s?://([\\w\\.\\-~]+:?\\d{,4})(/[\\w\\-~]+)+$", project_identifier):  # iri
        project = Project(con=con, shortname=project_identifier)
    else:
        print(f"ERROR Invalid project identifier '{project_identifier}'. Use the project's shortcode, shortname or IRI.")
        exit(1)

    project = project.read()

    project_obj = project.createDefinitionFileObj()

    # get the lists
    if verbose:
        print("Getting lists...")
    list_roots = ListNode.getAllLists(con=con, project_iri=project.id)
    list_obj = []
    for list_root in list_roots:
        complete_list = list_root.getAllNodes()
        list_obj.append(complete_list.createDefinitionFileObj())
        if verbose:
            print(f"\tGot list '{list_root.name}'")
    project_obj["lists"] = list_obj

    # get the ontologies
    if verbose:
        print(f"Getting ontologies...")
    project_obj["ontologies"] = []
    prefixes: Dict[str, str] = {}
    ontologies = Ontology.getProjectOntologies(con, project.id)
    ontology_ids = [onto.id for onto in ontologies]
    for ontology_id in ontology_ids:
        onto_url_parts = ontology_id.split("/")  # an id has the form http://0.0.0.0:3333/ontology/4123/testonto/v2
        name = onto_url_parts[len(onto_url_parts) - 2]
        shortcode = onto_url_parts[len(onto_url_parts) - 3]
        ontology = Ontology.getOntologyFromServer(con=con, shortcode=shortcode, name=name)
        project_obj["ontologies"].append(ontology.createDefinitionFileObj())
        prefixes.update(ontology.context.get_externals_used())
        if verbose:
            print(f"\tGot ontology '{name}'")

    ontology_json = {
        "prefixes": prefixes,
        "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json",
        "project": project_obj
    }

    with open(outfile, 'w', encoding='utf8') as outfile:
        json.dump(ontology_json, outfile, indent=3, ensure_ascii=False)
