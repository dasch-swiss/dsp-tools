import json
import warnings
from typing import Any

import regex

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.models.group import Group
from dsp_tools.commands.project.models.listnode import ListNode
from dsp_tools.commands.project.models.ontology import Ontology
from dsp_tools.commands.project.models.project import Project
from dsp_tools.commands.project.models.user import User
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive


def get_project(
    project_identifier: str,
    outfile_path: str,
    creds: ServerCredentials,
    verbose: bool = False,
) -> bool:
    """
    This function writes a project from a DSP server into a JSON file.

    Args:
        project_identifier: the project identifier, either shortcode, shortname or IRI of the project
        outfile_path: the output file the JSON content should be written to
        creds: the credentials to access the DSP server
        verbose: verbose option for the command, if used more output is given to the user

    Raises:
        BaseError: if something went wrong

    Returns:
        True if the process finishes without errors
    """
    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)
    try:
        auth.get_token()
        con = ConnectionLive(creds.server, auth)
    except BaseError:
        warnings.warn("WARNING: Missing or wrong credentials. You won't get data about the users of this project.")
        con = ConnectionLive(creds.server)

    project = _create_project(con, project_identifier)

    project = project.read()
    project_obj = project.createDefinitionFileObj()

    project_obj["groups"] = _get_groups(con, str(project.iri), verbose)

    project_obj["users"] = _get_users(con, project, verbose)

    project_obj["lists"] = _get_lists(con, project, verbose)

    prefixes, ontos = _get_ontologies(con, str(project.iri), verbose)
    project_obj["ontologies"] = ontos

    schema = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json"
    outfile_content = {
        "prefixes": prefixes,
        "$schema": schema,
        "project": project_obj,
    }

    with open(outfile_path, "w", encoding="utf-8") as f:
        json.dump(outfile_content, f, indent=4, ensure_ascii=False)

    return True


def _create_project(con: Connection, project_identifier: str) -> Project:
    if regex.match("[0-9A-F]{4}", project_identifier):  # shortcode
        return Project(con=con, shortcode=project_identifier)
    elif regex.match("^[\\w-]+$", project_identifier):  # shortname
        return Project(con=con, shortname=project_identifier.lower())
    elif regex.match("^(http)s?://([\\w\\.\\-~]+:?\\d{,4})(/[\\w\\-~]+)+$", project_identifier):  # iri
        return Project(con=con, shortname=project_identifier)
    else:
        raise BaseError(
            f"ERROR Invalid project identifier '{project_identifier}'. Use the project's shortcode, shortname or IRI."
        )


def _get_groups(con: Connection, project_iri: str, verbose: bool) -> list[dict[str, Any]]:
    if verbose:
        print("Getting groups...")
    groups_obj: list[dict[str, Any]] = []
    if groups := Group.getAllGroupsForProject(con=con, proj_iri=project_iri):
        for group in groups:
            groups_obj.append(group.createDefinitionFileObj())
            if verbose:
                print(f"    Got group '{group.name}'")
    return groups_obj


def _get_users(con: Connection, project: Project, verbose: bool) -> list[dict[str, Any]] | None:
    if verbose:
        print("Getting users...")
    try:
        users = User.getAllUsersForProject(con=con, proj_shortcode=str(project.shortcode))
    except BaseError:
        return None
    if users is None:
        return None

    users_obj: list[dict[str, Any]] = []
    for usr in users:
        users_obj.append(
            usr.createDefinitionFileObj(
                con=con,
                proj_shortname=str(project.shortname),
                proj_iri=str(project.iri),
            )
        )
        if verbose:
            print(f"    Got user '{usr.username}'")
    return users_obj


def _get_lists(con: Connection, project: Project, verbose: bool) -> list[dict[str, Any]]:
    if verbose:
        print("Getting lists...")
    list_obj: list[dict[str, Any]] = []
    if list_roots := ListNode.getAllLists(con=con, project_iri=project.iri):
        for list_root in list_roots:
            complete_list = list_root.getAllNodes()
            list_obj.append(complete_list.createDefinitionFileObj())
            if verbose:
                print(f"    Got list '{list_root.name}'")
    return list_obj


def _get_ontologies(con: Connection, project_iri: str, verbose: bool) -> tuple[dict[str, str], list[dict[str, Any]]]:
    if verbose:
        print("Getting ontologies...")
    ontos = []
    prefixes: dict[str, str] = {}
    ontologies = Ontology.getProjectOntologies(con, project_iri)
    ontology_ids = [onto.iri for onto in ontologies]
    for ontology_id in ontology_ids:
        onto_url_parts = ontology_id.split("/")  # an id has the form http://0.0.0.0:3333/ontology/4123/testonto/v2
        name = onto_url_parts[len(onto_url_parts) - 2]
        shortcode = onto_url_parts[len(onto_url_parts) - 3]
        ontology = Ontology.getOntologyFromServer(con=con, shortcode=shortcode, name=name)
        ontos.append(ontology.createDefinitionFileObj())
        prefixes.update(ontology.context.get_externals_used())
        if verbose:
            print(f"    Got ontology '{name}'")
    return prefixes, ontos
