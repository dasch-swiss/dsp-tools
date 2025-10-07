import json
from pathlib import Path
from typing import Any
from typing import Union
from typing import cast

from loguru import logger

from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import JSONFileParsingError
from dsp_tools.error.exceptions import UserFilepathNotFoundError


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
    if isinstance(project_file_as_path_or_parsed, dict):
        return project_file_as_path_or_parsed
    if isinstance(project_file_as_path_or_parsed, str | Path):
        return parse_json_file(Path(project_file_as_path_or_parsed))
    raise BaseError("Invalid input: The input must be a path to a JSON file or a parsed JSON object.")


def parse_json_file(filepath: Path) -> dict[str, Any]:
    if not filepath.exists():
        raise UserFilepathNotFoundError(filepath)
    with open(filepath, encoding="utf-8") as f:
        try:
            loaded = json.load(f)
            return cast(dict[str, Any], loaded)
        except json.JSONDecodeError as e:
            logger.error(e)
            msg = f"The input file '{filepath}' cannot be parsed to a JSON object."
            raise JSONFileParsingError(msg) from None
