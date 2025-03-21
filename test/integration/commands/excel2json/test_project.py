import json
from typing import Any
from typing import cast

import pytest

from dsp_tools.commands.excel2json.project import _old_create_project_json
from dsp_tools.commands.excel2json.project import _old_validate_folder_structure_and_get_filenames


@pytest.fixture
def expected_project() -> dict[str, Any]:
    with open("testdata/excel2json/excel2json-expected-output.json", encoding="utf-8") as f:
        proj = json.load(f)
        return cast(dict[str, Any], proj)


@pytest.fixture
def returned_project() -> dict[str, Any]:
    excel_folder = "testdata/excel2json/old_excel2json_files"
    listfolder, onto_folders = _old_validate_folder_structure_and_get_filenames(excel_folder)
    _, project = _old_create_project_json(excel_folder, listfolder, onto_folders)
    return project


def test_same_keys(returned_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    assert set(returned_project["project"]) == set(expected_project["project"])


def test_lists(returned_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    res_lists = sorted(returned_project["project"]["lists"], key=lambda x: x["name"])
    expected_lists = sorted(expected_project["project"]["lists"], key=lambda x: x["name"])
    for r, e in zip(res_lists, expected_lists):
        assert r == e, r["name"]


def test_ontology_number(returned_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    res_ontos = returned_project["project"]["ontologies"]
    expected_onto = expected_project["project"]["ontologies"]
    assert len(res_ontos) == 1
    assert len(expected_onto) == 1


def test_properties(returned_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    res_props = sorted(returned_project["project"]["ontologies"][0]["properties"], key=lambda x: x["name"])
    ex_props = sorted(expected_project["project"]["ontologies"][0]["properties"], key=lambda x: x["name"])
    for r, e in zip(res_props, ex_props):
        assert r == e, r["name"]


def test_resources(returned_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    res_resources = sorted(returned_project["project"]["ontologies"][0]["resources"], key=lambda x: x["name"])
    ex_resources = sorted(expected_project["project"]["ontologies"][0]["resources"], key=lambda x: x["name"])
    for r, e in zip(res_resources, ex_resources):
        assert r == e, r["name"]


def test_entire_project(returned_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    assert returned_project == expected_project


if __name__ == "__main__":
    pytest.main([__file__])
