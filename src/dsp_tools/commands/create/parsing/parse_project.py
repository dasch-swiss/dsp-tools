import os
from typing import Any
from typing import cast

from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import InputProblem
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_project import DefaultPermissions
from dsp_tools.commands.create.models.parsed_project import GlobalLimitedViewPermission
from dsp_tools.commands.create.models.parsed_project import LimitedViewPermissionsSelection
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
from dsp_tools.commands.create.parsing.parsing_utils import resolve_all_to_absolute_iri
from dsp_tools.setup.dotenv import read_dotenv_if_exists

read_dotenv_if_exists()


def parse_project(complete_json: dict[str, Any], api_url: str) -> ParsedProject | list[CollectedProblems]:
    prefix_lookup = create_prefix_lookup(complete_json, api_url)
    project_json = complete_json["project"]
    ontologies, failures = _parse_all_ontologies(project_json, prefix_lookup)
    permissions, permissions_failures = _parse_permissions(project_json, prefix_lookup)
    if permissions_failures:
        failures.append(permissions_failures)
    parsed_lists = parse_lists(project_json)
    users, memberships, user_problems = _parse_users(project_json)
    if user_problems:
        failures.append(user_problems)
    if failures:
        return failures
    return ParsedProject(
        prefixes=prefix_lookup,
        project_metadata=parse_metadata(project_json),
        permissions=cast(ParsedPermissions, permissions),
        groups=_parse_groups(project_json),
        users=users,
        user_memberships=memberships,
        lists=parsed_lists,
        ontologies=ontologies,
    )


def parse_metadata(project_json: dict[str, Any]) -> ParsedProjectMetadata:
    return ParsedProjectMetadata(
        shortcode=project_json["shortcode"],
        shortname=project_json["shortname"],
        longname=project_json["longname"],
        descriptions=project_json["descriptions"],
        keywords=project_json["keywords"],
        enabled_licenses=project_json.get("enabled_licenses", []),
    )


def _parse_permissions(
    project_json: dict[str, Any], prefix_lookup: dict[str, str]
) -> tuple[ParsedPermissions | None, CollectedProblems | None]:
    problems: list[CreateProblem] = []
    default_found = project_json["default_permissions"]
    default_perm = None
    match default_found:
        case "private":
            default_perm = DefaultPermissions.PRIVATE
        case "public":
            default_perm = DefaultPermissions.PUBLIC
        case _:
            problems.append(InputProblem(str(default_found), InputProblemType.DEFAULT_PERMISSIONS_NOT_CORRECT))

    found_overrule = project_json.get("default_permissions_overrule", {})
    if private := found_overrule.get("private"):
        resolved_private, resolving_problems = resolve_all_to_absolute_iri(private, None, prefix_lookup)
        if resolving_problems:
            problems.extend(resolving_problems)
    else:
        resolved_private = None
    limited_view = found_overrule.get("limited_view")
    limited_resolved, limited_problems = _get_limited_view(limited_view, prefix_lookup)
    problems.extend(limited_problems)
    if problems:
        return None, CollectedProblems(
            "During the parsing of the permissions the following problems were found:", problems
        )
    return ParsedPermissions(
        default_permissions=cast(DefaultPermissions, default_perm),
        overrule_private=resolved_private,
        overrule_limited_view=cast(LimitedViewPermissionsSelection | GlobalLimitedViewPermission, limited_resolved),
    ), None


def _get_limited_view(
    original_input: str | list[str] | None, prefixes: dict[str, str]
) -> tuple[LimitedViewPermissionsSelection | GlobalLimitedViewPermission | None, list[CreateProblem]]:
    match original_input:
        case "all":
            return GlobalLimitedViewPermission.ALL, []
        case list():
            return _handle_limited_view_list(original_input, prefixes)
        case None:
            return GlobalLimitedViewPermission.NONE, []
        case _:
            return None, [InputProblem(original_input, InputProblemType.LIMITED_VIEW_PERMISSIONS_NOT_CORRECT)]


def _handle_limited_view_list(
    limited_view_list: list[str], prefixes: dict[str, str]
) -> tuple[LimitedViewPermissionsSelection | None, list[CreateProblem]]:
    all_resolved, resolving_problems = resolve_all_to_absolute_iri(limited_view_list, None, prefixes)
    if resolving_problems:
        return None, resolving_problems
    return LimitedViewPermissionsSelection(all_resolved), []


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


def parse_lists(project_json: dict[str, Any]) -> list[ParsedList]:
    if not (found := project_json.get("lists")):
        return []
    return parse_list_section(found)


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
