# mypy: disable-error-code="no-untyped-def"

from pathlib import Path
from typing import Any

import pytest

from dsp_tools.commands.create.constants import KNORA_API
from dsp_tools.utils.json_parsing import parse_json_file

ONTO_PREFIX = "http://0.0.0.0:3333/ontology/8888/onto/v2#"


@pytest.fixture
def project_json_systematic() -> dict[str, Any]:
    return parse_json_file(Path("testdata/json-project/test-project-systematic.json"))


@pytest.fixture
def project_json_create() -> dict[str, Any]:
    return parse_json_file(Path("testdata/json-project/create-project.json"))


@pytest.fixture
def minimal_failing_project() -> dict[str, Any]:
    return {
        "prefixes": {},
        "project": {
            "shortcode": "9999",
            "shortname": "fail-test",
            "longname": "Failure Test Project",
            "descriptions": {"en": "Test project for failures"},
            "keywords": ["test"],
            "enabled_licenses": ["http://rdfh.ch/licenses/cc-by-4.0"],
            "default_permissions": "public",
            "ontologies": [
                {
                    "name": "test-onto",
                    "label": "Test Ontology",
                    "properties": [
                        {
                            "name": "testProp",
                            "super": ["hasValue"],
                            "object": "TextValue",
                            "labels": {"en": "Test Property"},
                            "gui_element": "SimpleText",
                        }
                    ],
                    "resources": [
                        {
                            "name": "TestResource",
                            "super": "Resource",
                            "labels": {"en": "Test Resource"},
                            "cardinalities": [{"propname": "invalid:nonExistentProp", "cardinality": "1"}],
                        }
                    ],
                }
            ],
        },
    }


@pytest.fixture
def minimal_project_json() -> dict[str, Any]:
    return {
        "shortcode": "9999",
        "shortname": "minimal",
        "longname": "Minimal Test Project",
        "descriptions": {"en": "A minimal project"},
        "keywords": ["test"],
        "enabled_licenses": ["http://rdfh.ch/licenses/cc-by-4.0"],
        "default_permissions": "public",
        "ontologies": [
            {
                "name": "minimal-onto",
                "label": "Minimal Ontology",
                "properties": [],
                "resources": [],
            }
        ],
    }


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
def onto_json(project_json_create):
    return project_json_create["project"]["ontologies"][0]
