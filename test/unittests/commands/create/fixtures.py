from pathlib import Path
from typing import Any

import pytest

from dsp_tools.utils.json_parsing import parse_json_file


@pytest.fixture
def prefixes() -> dict[str, str]:
    return {"": ""}


@pytest.fixture
def project() -> dict[str, Any]:
    return parse_json_file(Path("testdata/json-project/create-project.json"))
