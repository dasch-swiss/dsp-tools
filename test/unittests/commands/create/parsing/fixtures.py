# mypy: disable-error-code="no-untyped-def"

from pathlib import Path
from typing import Any

import pytest

from dsp_tools.commands.create.constants import KNORA_API_STR
from dsp_tools.commands.create.models.server_project_info import ListNameToIriLookup
from dsp_tools.utils.json_parsing import parse_json_file

ONTO_PREFIX = "http://0.0.0.0:3333/ontology/0003/onto/v2#"
LIST_IRI = "http://rdfh.ch/lists/9999/node_name"


@pytest.fixture
def prefixes() -> dict[str, str]:
    return {
        "dcterms": "http://purl.org/dc/terms/",
        "externalOnto": "http://otherOntology.com/onto/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "in-built": "http://0.0.0.0:3333/ontology/0003/in-built/v2#",
        "knora-api": KNORA_API_STR,
        "onto": ONTO_PREFIX,
        "second-onto": "http://0.0.0.0:3333/ontology/0003/second-onto/v2#",
    }


@pytest.fixture
def list_name_to_iri() -> ListNameToIriLookup:
    return ListNameToIriLookup({"node_name": LIST_IRI})


@pytest.fixture
def project_json_systematic() -> dict[str, Any]:
    return parse_json_file(Path("testdata/json-project/systematic-project-4123.json"))


@pytest.fixture
def project_json_create() -> dict[str, Any]:
    return parse_json_file(Path("testdata/json-project/create-project-0003.json"))


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
                    "name": "onto",
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
                "name": "onto",
                "label": "Minimal Ontology",
                "properties": [],
                "resources": [],
            }
        ],
    }


@pytest.fixture
def onto_json(project_json_create):
    return project_json_create["project"]["ontologies"][0]
