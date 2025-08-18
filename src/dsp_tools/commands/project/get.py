import json
import warnings
from typing import Any

import regex

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.commands.project.legacy_models.group import Group
from dsp_tools.commands.project.legacy_models.listnode import ListNode
from dsp_tools.commands.project.legacy_models.ontology import Ontology
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.commands.project.legacy_models.user import User
from dsp_tools.commands.project.models.permissions_client import PermissionsClient
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import UnknownDOAPException


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

    prefixes, ontos = _get_ontologies(con, str(project.iri), verbose)

    default_permissions, default_permissions_override = _get_default_permissions(auth, str(project.iri), prefixes)
    project_obj["default_permissions"] = default_permissions
    if default_permissions_override:
        project_obj["default_permissions_override"] = default_permissions_override

    project_obj["groups"] = _get_groups(con, str(project.iri), verbose)

    project_obj["users"] = _get_users(con, project, verbose)

    project_obj["lists"] = _get_lists(con, project, verbose)

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


def _get_default_permissions(
    auth: AuthenticationClientLive, project_iri: str, prefixes: dict[str, str]
) -> tuple[str, dict[str, list[str]] | None]:
    perm_client = PermissionsClient(auth, project_iri)
    project_doaps = perm_client.get_project_doaps()
    fallback_text = (
        "We cannot determine if this project is public or private. "
        "The DSP-TOOLS devs can assist you in analysing the existing DOAPs, "
        "and help you deciding if the original intent was rather public or rather private."
    )
    try:
        default_permissions = _parse_default_permissions(project_doaps)
        default_permissions_override = _parse_default_permissions_override(project_doaps, prefixes)
    except UnknownDOAPException:
        default_permissions = fallback_text
        default_permissions_override = None
    return default_permissions, default_permissions_override


def _parse_default_permissions(project_doaps: list[dict[str, Any]]) -> str:
    """If the DOAPs exactly match our definition of public/private, return public/private. Otherwise, return unknown."""
    unsupported_groups = ("SystemAdmin", "ProjectAdmin", "Creator", "KnownUser", "UnknownUser")
    if [x for x in project_doaps if x.get("forGroup", "").endswith(unsupported_groups)]:
        raise UnknownDOAPException()
    proj_member_doaps = [x for x in project_doaps if x.get("forGroup", "").endswith("ProjectMember")]
    if len(proj_member_doaps) != 1:
        raise UnknownDOAPException()
    perms = proj_member_doaps[0]["hasPermissions"]
    if len(perms) not in [2, 4]:
        raise UnknownDOAPException()
    proj_adm_perms = [x for x in perms if x["additionalInformation"].endswith("ProjectAdmin")]
    proj_mem_perms = [x for x in perms if x["additionalInformation"].endswith("ProjectMember")]
    knwn_usr_perms = [x for x in perms if x["additionalInformation"].endswith("KnownUser")]
    unkn_usr_perms = [x for x in perms if x["additionalInformation"].endswith("UnknownUser")]
    if not (len(proj_adm_perms) == len(proj_mem_perms) == 1):
        raise UnknownDOAPException()
    if proj_adm_perms[0]["name"] != "CR" or proj_mem_perms[0]["name"] != "D":
        raise UnknownDOAPException()
    if len(knwn_usr_perms) == len(unkn_usr_perms) == 0:
        return "private"
    if not (len(knwn_usr_perms) == len(unkn_usr_perms) == 1):
        raise UnknownDOAPException()
    if knwn_usr_perms[0]["name"] != "V" or unkn_usr_perms[0]["name"] != "V":
        raise UnknownDOAPException()
    return "public"


def _parse_default_permissions_override(  # noqa: PLR0912, PLR0915
    project_doaps: list[dict[str, Any]], prefixes: dict[str, str]
) -> dict[str, list[str]] | None:
    # these cases exist:
    # private for prop
    # private for class
    # limited view for http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue
    # limited view for http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue and a certain class

    # convert knora-api form of prefixes into knora-base form (used by DOAPs)
    prefixes_knora_base_inverted = {}
    for onto_shorthand, knora_api_iri in prefixes.items():
        if match := regex.search(r"/ontology/([0-9A-Fa-f]{4})/([^/]+)/v2", knora_api_iri):
            shortcode, onto_name = match.groups()
            prefixes_knora_base_inverted[f"http://www.knora.org/ontology/{shortcode}/{onto_name}"] = onto_shorthand

    class_doaps = []
    prop_doaps = []
    has_img_all_classes_doaps = []
    has_img_specific_class_doaps = []
    other_doaps = []
    for doap in project_doaps:
        match (doap.get("forResourceClass"), doap.get("forProperty")):
            case (for_class, None) if for_class is not None:
                class_doaps.append(doap)
            case (None, for_prop) if for_prop is not None and "hasStillImageFileValue" not in for_prop:
                prop_doaps.append(doap)
            case (None, for_prop) if "hasStillImageFileValue" in str(for_prop):
                has_img_all_classes_doaps.append(doap)
            case (for_class, for_prop) if for_class is not None and "hasStillImageFileValue" in str(for_prop):
                has_img_specific_class_doaps.append(doap)
            case _:
                other_doaps.append(doap)
    if other_doaps:
        raise UnknownDOAPException()

    for expected_private_doap in class_doaps + prop_doaps:
        perm = sorted(expected_private_doap["hasPermissions"], key=lambda x: x["name"])
        if len(perm) != 2:
            raise UnknownDOAPException()
        CR, D = perm
        if CR["name"] != "CR" or not CR["additionalInformation"].endswith("ProjectAdmin"):
            raise UnknownDOAPException()
        if D["name"] != "D" or not D["additionalInformation"].endswith("ProjectMember"):
            raise UnknownDOAPException()

    for expected_limited_view in has_img_all_classes_doaps + has_img_specific_class_doaps:
        perm = sorted(expected_limited_view["hasPermissions"], key=lambda x: x["name"])
        if len(perm) != 4:
            raise UnknownDOAPException()
        CR, D, RV1, RV2 = perm
        if CR["name"] != "CR" or not CR["additionalInformation"].endswith("ProjectAdmin"):
            raise UnknownDOAPException()
        if D["name"] != "D" or not D["additionalInformation"].endswith("ProjectMember"):
            raise UnknownDOAPException()
        if RV1["name"] != "RV" or not RV2["additionalInformation"].endswith("nownUser"):
            raise UnknownDOAPException()
        if RV2["name"] != "RV" or not RV2["additionalInformation"].endswith("nownUser"):
            raise UnknownDOAPException()

    privates: list[str] = []
    for class_doap in class_doaps:
        privates.append(_shorten_iri(class_doap["forResourceClass"], prefixes_knora_base_inverted))
    for prop_doap in prop_doaps:
        privates.append(_shorten_iri(prop_doap["forProperty"], prefixes_knora_base_inverted))

    limited_views: list[str] = []
    if len(has_img_all_classes_doaps) > 1:
        raise UnknownDOAPException()
    if len(has_img_all_classes_doaps) == 1 and len(has_img_specific_class_doaps) > 0:
        raise UnknownDOAPException()
    if len(has_img_all_classes_doaps) == 1:
        limited_views.append("all")
    for img_doap in has_img_specific_class_doaps:
        limited_views.append(_shorten_iri(img_doap["forResourceClass"], prefixes_knora_base_inverted))

    result: dict[str, list[str]] = {}
    if privates:
        result["private"] = privates
    if limited_views:
        result["limited_view"] = limited_views
    return result


def _shorten_iri(full_iri: str, prefixes_inverted: dict[str, str]) -> str:
    before_hashtag, after_hashtag = full_iri.rsplit("#", maxsplit=1)
    prefix = prefixes_inverted[before_hashtag]
    return f"{prefix}:{after_hashtag}"


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
