import json
from pathlib import Path
from typing import Any
from typing import cast

from loguru import logger

from dsp_tools.error.exceptions import JSONFileParsingError
from dsp_tools.error.exceptions import UserFilepathNotFoundError


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
