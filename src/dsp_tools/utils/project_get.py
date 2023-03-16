import json
import re
from typing import Optional

from dsp_tools.models.connection import Connection
from dsp_tools.models.group import Group
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.listnode import ListNode
from dsp_tools.models.ontology import Ontology
from dsp_tools.models.project import Project
from dsp_tools.models.user import User


def get_project(project_identifier: str, outfile_path: str, server: str, user: str, password: str, verbose: bool) -> bool:
    """
    This function writes a project from a DSP server into a JSON file.

    Args:
        project_identifier : the project identifier, either shortcode, shortname or IRI of the project
        outfile_path : the output file the JSON content should be written to
        server : the DSP server where the data should be read from
        user : the user (e-mail) who sends the request
        password : the password of the user who sends the request
        verbose : verbose option for the command, if used more output is given to the user

    Raises:
        BaseError if something went wrong
    
    Returns:
        True if the process finishes without errors
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
        raise BaseError(f"ERROR Invalid project identifier '{project_identifier}'. Use the project's shortcode, shortname or IRI.")

    project = project.read()

    project_obj = project.createDefinitionFileObj()

    # get groups
    if verbose:
        print("Getting groups...")
    groups_obj = []
    groups: Optional[list[Group]] = Group.getAllGroupsForProject(con=con, proj_iri=project.id)
    if groups:
        for group in groups:
            groups_obj.append(group.createDefinitionFileObj())
            if verbose:
                print(f"\tGot group '{group.name}'")
    project_obj["groups"] = groups_obj

    # get users
    if verbose:
        print("Getting users...")
    users_obj = []
    users = User.getAllUsersForProject(con=con, proj_shortcode=project.shortcode)
    if users:
        for usr in users:
            users_obj.append(usr.createDefinitionFileObj(
                con=con, proj_shortname=project.shortname, proj_shortcode=project.shortcode
            ))
            if verbose:
                print(f"\tGot user '{usr.username}'")
        project_obj["users"] = users_obj

    # get the lists
    if verbose:
        print("Getting lists...")
    list_obj = []
    list_roots: Optional[list[ListNode]] = ListNode.getAllLists(con=con, project_iri=project.id)
    if list_roots:
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
    prefixes: dict[str, str] = dict()
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

    outfile_content = {
        "prefixes": prefixes,
        "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json",
        "project": project_obj
    }

    with open(outfile_path, 'w', encoding='utf8') as f:
        json.dump(outfile_content, f, indent=4, ensure_ascii=False)

    return True
