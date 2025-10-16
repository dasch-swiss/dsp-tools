# mypy: disable-error-code="no-untyped-def"

from pathlib import Path
from typing import Any

import pytest

from dsp_tools.utils.json_parsing import parse_json_file

ONTO_PREFIX = "http://0.0.0.0:3333/ontology/8888/onto/v2#"
KNORA_API = "http://api.knora.org/ontology/knora-api/v2#"


@pytest.fixture
def prefixes() -> dict[str, str]:
    return {
        "foaf": "http://xmlns.com/foaf/0.1/",
        "externalOnto": "http://otherOntology.com/onto/",
        "dcterms": "http://purl.org/dc/terms/",
        "knora-api": KNORA_API,
        "onto": ONTO_PREFIX,
        "second-onto": "http://0.0.0.0:3333/ontology/8888/second-onto/v2#",
    }


@pytest.fixture
def project() -> dict[str, Any]:
    return parse_json_file(Path("testdata/json-project/create-project.json"))


@pytest.fixture
def onto_json(project):
    return project["project"]["ontologies"][0]
