import json
from pathlib import Path
from typing import Any
from typing import Union

from dsp_tools.error.exceptions import BaseError


def parse_json_input(project_file_as_path_or_parsed: Union[str, Path, dict[str, Any]]) -> dict[str, Any]:
    """
    Check the input for a method that expects a JSON project definition, either as file path or as parsed JSON object:
    If it is parsed already, return it unchanged.
    If the input is a file path, parse it.

    Args:
        project_file_as_path_or_parsed: path to the JSON project definition, or parsed JSON object

    Raises:
        BaseError: if the input is invalid

    Returns:
        the parsed JSON object
    """
    project_definition: dict[str, Any] = {}
    if isinstance(project_file_as_path_or_parsed, dict):
        project_definition = project_file_as_path_or_parsed
    elif isinstance(project_file_as_path_or_parsed, str | Path) and Path(project_file_as_path_or_parsed).exists():
        with open(project_file_as_path_or_parsed, encoding="utf-8") as f:
            try:
                project_definition = json.load(f)
            except json.JSONDecodeError as e:
                msg = f"The input file '{project_file_as_path_or_parsed}' cannot be parsed to a JSON object."
                raise BaseError(msg) from e
    else:
        raise BaseError("Invalid input: The input must be a path to a JSON file or a parsed JSON object.")
    return project_definition
