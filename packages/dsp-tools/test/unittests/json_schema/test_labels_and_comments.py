import importlib.resources
import json
from typing import Any

import jsonschema
import pytest


def _load_schema(file_name: str) -> dict[str, Any]:
    with (
        importlib.resources.files("dsp_tools")
        .joinpath(f"resources/schema/{file_name}")
        .open(encoding="utf-8") as schema_file
    ):
        schema: dict[str, Any] = json.load(schema_file)
    return schema


def _validator_for_definition(file_name: str, definition: str) -> jsonschema.Draft7Validator:
    schema = _load_schema(file_name)
    return jsonschema.Draft7Validator({"definitions": schema["definitions"], "$ref": f"#/definitions/{definition}"})


def _resource(labels: dict[str, str] | None, comments: dict[str, str] | None) -> dict[str, Any]:
    resource: dict[str, Any] = {"name": "Book", "super": "Resource"}
    if labels is not None:
        resource["labels"] = labels
    if comments is not None:
        resource["comments"] = comments
    return resource


def _property(labels: dict[str, str] | None, comments: dict[str, str] | None) -> dict[str, Any]:
    prop: dict[str, Any] = {
        "name": "hasTitle",
        "super": ["hasValue"],
        "object": "TextValue",
        "gui_element": "SimpleText",
    }
    if labels is not None:
        prop["labels"] = labels
    if comments is not None:
        prop["comments"] = comments
    return prop


RESOURCE_VALIDATORS = [
    pytest.param(("project.json", "resource"), id="project-resource"),
    pytest.param(("resources-only.json", "resource"), id="resources-only"),
]
PROPERTY_VALIDATORS = [
    pytest.param(("project.json", "property"), id="project-property"),
    pytest.param(("properties-only.json", "property"), id="properties-only"),
]

VALID_LANGUAGES = [
    pytest.param({"en": "label"}, {"en": "comment"}, id="en-only"),
    pytest.param({"en": "l", "de": "l", "fr": "l"}, {"en": "c", "de": "c", "fr": "c"}, id="en-de-fr"),
    pytest.param(
        {"en": "l", "de": "l", "fr": "l", "it": "l", "rm": "l"},
        {"en": "c", "de": "c", "fr": "c", "it": "c", "rm": "c"},
        id="all-languages",
    ),
]

INVALID_LANGUAGES = [
    pytest.param({"de": "label"}, {"en": "c", "de": "c"}, id="label-without-en"),
    pytest.param({"en": "l", "de": "l"}, {"de": "comment"}, id="comment-without-en"),
    pytest.param(None, {"en": "comment"}, id="no-labels"),
    pytest.param({"en": "label"}, None, id="no-comments"),
    pytest.param({"en": "l", "de": "l"}, {"en": "comment"}, id="de-label-without-de-comment"),
    pytest.param({"en": "label"}, {"en": "c", "de": "c"}, id="de-comment-without-de-label"),
    pytest.param({"en": "l", "fr": "l"}, {"en": "comment"}, id="fr-label-without-fr-comment"),
    pytest.param({"en": "label"}, {"en": "c", "it": "c"}, id="it-comment-without-it-label"),
    pytest.param({"en": "l", "rm": "l"}, {"en": "c", "de": "c"}, id="rm-label-and-de-comment"),
]


@pytest.mark.parametrize("schema_and_definition", RESOURCE_VALIDATORS)
@pytest.mark.parametrize(("labels", "comments"), VALID_LANGUAGES)
def test_resource_valid(
    schema_and_definition: tuple[str, str], labels: dict[str, str], comments: dict[str, str]
) -> None:
    validator = _validator_for_definition(*schema_and_definition)
    assert not list(validator.iter_errors(_resource(labels, comments)))


@pytest.mark.parametrize("schema_and_definition", RESOURCE_VALIDATORS)
@pytest.mark.parametrize(("labels", "comments"), INVALID_LANGUAGES)
def test_resource_invalid(
    schema_and_definition: tuple[str, str], labels: dict[str, str] | None, comments: dict[str, str] | None
) -> None:
    validator = _validator_for_definition(*schema_and_definition)
    assert list(validator.iter_errors(_resource(labels, comments)))


@pytest.mark.parametrize("schema_and_definition", PROPERTY_VALIDATORS)
@pytest.mark.parametrize(("labels", "comments"), VALID_LANGUAGES)
def test_property_valid(
    schema_and_definition: tuple[str, str], labels: dict[str, str], comments: dict[str, str]
) -> None:
    validator = _validator_for_definition(*schema_and_definition)
    assert not list(validator.iter_errors(_property(labels, comments)))


@pytest.mark.parametrize("schema_and_definition", PROPERTY_VALIDATORS)
@pytest.mark.parametrize(("labels", "comments"), INVALID_LANGUAGES)
def test_property_invalid(
    schema_and_definition: tuple[str, str], labels: dict[str, str] | None, comments: dict[str, str] | None
) -> None:
    validator = _validator_for_definition(*schema_and_definition)
    assert list(validator.iter_errors(_property(labels, comments)))


@pytest.mark.parametrize(
    "node",
    [
        pytest.param({"name": "n", "labels": {"de": "Knoten"}}, id="node-without-en-and-comments"),
        pytest.param({"name": "n", "labels": {"de": "Knoten"}, "comments": {"fr": "c"}}, id="node-mixed-languages"),
    ],
)
def test_list_node_keeps_rules(node: dict[str, Any]) -> None:
    validator = _validator_for_definition("project.json", "node")
    assert not list(validator.iter_errors(node))
