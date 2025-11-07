from pathlib import Path
from typing import Any

from loguru import logger

from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedGroupDescription
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.models.parsed_project import ParsedUserMemberShipInfo
from dsp_tools.commands.create.parsing.parse_lists import parse_list_section
from dsp_tools.commands.create.parsing.parse_ontology import parse_ontology
from dsp_tools.commands.create.parsing.parsing_utils import create_prefix_lookup
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.utils.json_parsing import parse_json_input


def parse_lists_only(
    project_file_as_path_or_parsed: str | Path | dict[str, Any],
) -> tuple[ParsedProjectMetadata, list[ParsedList]] | CollectedProblems:
    complete_json = _parse_and_validate(project_file_as_path_or_parsed)
    project_json = complete_json["project"]
    project_metadata = _parse_metadata(project_json)
    parsed_lists, problems = _parse_lists(project_json)
    if isinstance(problems, CollectedProblems):
        return problems
    return project_metadata, parsed_lists


def parse_project(
    project_file_as_path_or_parsed: str | Path | dict[str, Any], api_url: str
) -> ParsedProject | list[CollectedProblems]:
    complete_json = _parse_and_validate(project_file_as_path_or_parsed)
    return _parse_project(complete_json, api_url)


def _parse_project(complete_json: dict[str, Any], api_url: str) -> ParsedProject | list[CollectedProblems]:
    prefix_lookup = create_prefix_lookup(complete_json, api_url)
    project_json = complete_json["project"]
    ontologies, failures = _parse_all_ontologies(project_json, prefix_lookup)
    parsed_lists, problems = _parse_lists(project_json)
    users, memberships = _parse_users(project_json)
    if isinstance(problems, CollectedProblems):
        failures.append(problems)
    if failures:
        return failures
    return ParsedProject(
        prefixes=prefix_lookup,
        project_metadata=_parse_metadata(project_json),
        permissions=_parse_permissions(project_json),
        groups=_parse_groups(project_json),
        users=users,
        user_memberships=memberships,
        lists=parsed_lists,
        ontologies=ontologies,
    )


def _parse_and_validate(project_file_as_path_or_parsed: str | Path | dict[str, Any]) -> dict[str, Any]:
    project_json = parse_json_input(project_file_as_path_or_parsed=project_file_as_path_or_parsed)
    validate_project(project_json)
    print("    JSON project file is syntactically correct and passed validation.")
    logger.info("JSON project file is syntactically correct and passed validation.")
    return project_json


def _parse_metadata(project_json: dict[str, Any]) -> ParsedProjectMetadata:
    return ParsedProjectMetadata(
        shortcode=project_json["shortcode"],
        shortname=project_json["shortname"],
        longname=project_json["longname"],
        descriptions=project_json["descriptions"],
        keywords=project_json["keywords"],
        enabled_licenses=project_json.get("enabled_licenses", []),
    )


def _parse_permissions(project_json: dict[str, Any]) -> ParsedPermissions:
    return ParsedPermissions(
        default_permissions=project_json["default_permissions"],
        default_permissions_overrule=project_json.get("default_permissions_overrule"),
    )


def _parse_groups(project_json: dict[str, Any]) -> list[ParsedGroup]:
    if not (found := project_json.get("groups")):
        return []
    return [_parse_one_group(x) for x in found]


def _parse_one_group(group_dict: dict[str, Any]) -> ParsedGroup:
    descriptions = [ParsedGroupDescription(lang=lang, text=text) for lang, text in group_dict["descriptions"].items()]
    return ParsedGroup(name=group_dict["name"], descriptions=descriptions)


def _parse_users(project_json: dict[str, Any]) -> tuple[list[ParsedUser], list[ParsedUserMemberShipInfo]]:
    if not (found := project_json.get("users")):
        return [], []
    users, memberships = [], []
    for u in found:
        usr, mbmr = _parse_one_user(u)
        users.append(usr)
        memberships.append(mbmr)
    return users, memberships


def _parse_one_user(user_dict: dict[str, Any]) -> tuple[ParsedUser, ParsedUserMemberShipInfo]:
    projects = user_dict.get("projects", [])
    is_admin = ":admin" in projects
    groups = [g.removeprefix(":") for g in user_dict.get("groups", [])]
    usr = ParsedUser(
        username=user_dict["username"],
        email=user_dict["email"],
        given_name=user_dict["givenName"],
        family_name=user_dict["familyName"],
        password=user_dict["password"],
        lang=user_dict.get("lang", "en"),
    )
    memberships = ParsedUserMemberShipInfo(user_dict["username"], is_admin, groups)
    return usr, memberships


def _parse_lists(project_json: dict[str, Any]) -> tuple[list[ParsedList], CollectedProblems | None]:
    if not (found := project_json.get("lists")):
        return [], None
    result = parse_list_section(found)
    if isinstance(result, CollectedProblems):
        return [], result
    return result, None


def _parse_all_ontologies(
    project_json: dict[str, Any], prefix_lookup: dict[str, str]
) -> tuple[list[ParsedOntology], list[CollectedProblems]]:
    ontos = []
    failures = []
    for o in project_json["ontologies"]:
        result = parse_ontology(o, prefix_lookup)
        if isinstance(result, ParsedOntology):
            ontos.append(result)
        else:
            failures.append(result)
    return ontos, failures
