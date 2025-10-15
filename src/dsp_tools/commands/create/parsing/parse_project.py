from pathlib import Path
from typing import Any

from loguru import logger

from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.utils.json_parsing import parse_json_input


def parse_project(project_file_as_path_or_parsed: str | Path | dict[str, Any]) -> ParsedProject:
    project_json = _parse_and_validate(project_file_as_path_or_parsed)


def _parse_and_validate(project_file_as_path_or_parsed: str | Path | dict[str, Any]) -> dict[str, Any]:
    project_json = parse_json_input(project_file_as_path_or_parsed=project_file_as_path_or_parsed)
    validate_project(project_json)
    print("    JSON project file is syntactically correct and passed validation.")
    logger.info("JSON project file is syntactically correct and passed validation.")
    return project_json


def _parse_metadata(project_json: dict[str, Any]) -> ParsedProjectMetadata:
    pass
