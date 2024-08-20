import json
from typing import Any

import pytest


@pytest.fixture()
def list_from_api() -> dict[str, Any]:
    with open("testdata/xml-validate/from_api/onlyList.json", "r", encoding="utf-8") as file:
        data: dict[str, Any] = json.load(file)
    return data
