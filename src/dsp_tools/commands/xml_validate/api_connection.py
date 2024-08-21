import json
from dataclasses import dataclass
from typing import Any


@dataclass
class ProjectClient:
    """Client handling ontology-related requests to the DSP-API."""

    def get_project_ontology(self) -> Any:
        with open("testdata/xml-validate/from_api/onto.jsonld", "r", encoding="utf-8") as file:
            return json.load(file)

    def get_one_list(self) -> dict[str, Any]:
        with open("testdata/xml-validate/from_api/onlyList.json", "r", encoding="utf-8") as file:
            data: dict[str, Any] = json.load(file)
        return data
