from pathlib import Path
from typing import Any

from loguru import logger

from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_project import ParsedGroups
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.utils.json_parsing import parse_json_input


def parse_project(project_file_as_path_or_parsed: str | Path | dict[str, Any], server: str) -> ParsedProject:
    project_json = _parse_and_validate(project_file_as_path_or_parsed)
    prefix_lookup = _create_prefix_lookup(project_json, server)
    ontos = _parse_all_ontologies(project_json, prefix_lookup)
    return ParsedProject(
        prefixes=prefix_lookup,
        project_metadata=_parse_metadata(project_json),
        permissions=_parse_permissions(project_json),
        groups=_parse_groups(project_json),
        users=_parse_users(project_json),
        lists=_parse_lists(project_json),
        ontologies=ontos,
    )


def _parse_and_validate(project_file_as_path_or_parsed: str | Path | dict[str, Any]) -> dict[str, Any]:
    project_json = parse_json_input(project_file_as_path_or_parsed=project_file_as_path_or_parsed)
    validate_project(project_json)
    print("    JSON project file is syntactically correct and passed validation.")
    logger.info("JSON project file is syntactically correct and passed validation.")
    return project_json


def _create_prefix_lookup(project_json: dict[str, Any], server: str) -> dict[str, str]:
    pass


def _parse_metadata(project_json: dict[str, Any]) -> ParsedProjectMetadata:
    pass


def _parse_permissions(project_json: dict[str, Any]) -> ParsedPermissions:
    pass


def _parse_groups(project_json: dict[str, Any]) -> list[ParsedGroups]:
    pass


def _parse_users(project_json: dict[str, Any]) -> list[ParsedUser]:
    pass


def _parse_lists(project_json: dict[str, Any]) -> list[ParsedList]:
    pass


def _parse_all_ontologies(project_json: dict[str, Any], prefix_lookup: dict[str, str]) -> list[ParsedOntology]:
    pass
