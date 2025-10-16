from pathlib import Path
from typing import Any

from loguru import logger

from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.parsing.parse_ontology import parse_ontology
from dsp_tools.commands.create.parsing.parsing_utils import create_prefix_lookup
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.utils.json_parsing import parse_json_input


def parse_project(project_file_as_path_or_parsed: str | Path | dict[str, Any], server: str) -> ParsedProject:
    complete_json = _parse_and_validate(project_file_as_path_or_parsed)
    prefix_lookup = create_prefix_lookup(complete_json, server)
    project_json = complete_json["project"]
    return ParsedProject(
        prefixes=prefix_lookup,
        project_metadata=_parse_metadata(project_json),
        permissions=_parse_permissions(project_json),
        groups=_parse_groups(project_json),
        users=_parse_users(project_json),
        lists=_parse_lists(project_json),
        ontologies=_parse_all_ontologies(project_json, prefix_lookup),
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
        enabled_licenses=project_json["enabled_licenses"],
    )


def _parse_permissions(project_json: dict[str, Any]) -> ParsedPermissions:
    return ParsedPermissions(
        default_permissions=project_json["default_permissions"],
        default_permissions_overrule=project_json.get("default_permissions_overrule"),
    )


def _parse_groups(project_json: dict[str, Any]) -> list[ParsedGroup]:
    if not (found := project_json.get("groups")):
        return []
    return [ParsedGroup(x) for x in found]


def _parse_users(project_json: dict[str, Any]) -> list[ParsedUser]:
    if not (found := project_json.get("users")):
        return []
    return [ParsedUser(x) for x in found]


def _parse_lists(project_json: dict[str, Any]) -> list[ParsedList]:
    if not (found := project_json.get("lists")):
        return []
    return [ParsedList(x["name"], x) for x in found]


def _parse_all_ontologies(project_json: dict[str, Any], prefix_lookup: dict[str, str]) -> list[ParsedOntology]:
    return [parse_ontology(o, prefix_lookup) for o in project_json["ontologies"]]
