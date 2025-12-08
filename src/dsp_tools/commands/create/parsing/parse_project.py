import os
from pathlib import Path
from typing import Any

from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import InputProblem
from dsp_tools.commands.create.models.create_problems import InputProblemType
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
from dsp_tools.commands.create.project_validate import parse_and_validate_project

# Load .env file only if it exists in the current working directory
# This allows CI to set environment variables directly without interference
dotenv_file = find_dotenv(usecwd=True)
if dotenv_file:
    load_dotenv(dotenv_path=dotenv_file, override=False)


def parse_project(complete_json: dict[str, Any], api_url: str) -> ParsedProject | list[CollectedProblems]:
    prefix_lookup = create_prefix_lookup(complete_json, api_url)
    project_json = complete_json["project"]
    ontologies, failures = _parse_all_ontologies(project_json, prefix_lookup)
    parsed_lists, list_problems = _parse_lists(project_json)
    if list_problems:
        failures.append(list_problems)
    users, memberships, user_problems = _parse_users(project_json)
    if user_problems:
        failures.append(user_problems)
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


def _parse_and_validate(json_file: Path) -> dict[str, Any]:
    _, project_json = parse_and_validate_project(json_file)
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


def _parse_users(
    project_json: dict[str, Any],
) -> tuple[list[ParsedUser], list[ParsedUserMemberShipInfo], CollectedProblems | None]:
    if not (found := project_json.get("users")):
        return [], [], None
    users, memberships = [], []
    input_problems: list[CreateProblem] = []
    for u in found:
        result = _parse_one_user(u)
        if isinstance(result, InputProblem):
            input_problems.append(result)
        else:
            usr, mbmr = result
            users.append(usr)
            memberships.append(mbmr)
    if input_problems:
        problem_collection = CollectedProblems(
            "When parsing the user section the following problems occurred:", input_problems
        )
    else:
        problem_collection = None
    return users, memberships, problem_collection


def _parse_one_user(user_dict: dict[str, Any]) -> tuple[ParsedUser, ParsedUserMemberShipInfo] | InputProblem:
    projects = user_dict.get("projects", [])
    is_admin = ":admin" in projects
    groups = [g.removeprefix(":") for g in user_dict.get("groups", [])]
    pw = user_dict["password"]
    if not pw:
        pw = os.getenv("DSP_USER_PASSWORD")
        if not pw:
            return InputProblem(user_dict["username"], InputProblemType.USER_PASSWORD_NOT_SET)
    usr = ParsedUser(
        username=user_dict["username"],
        email=user_dict["email"],
        given_name=user_dict["givenName"],
        family_name=user_dict["familyName"],
        password=pw,
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
