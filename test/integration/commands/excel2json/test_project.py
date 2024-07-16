import json
from typing import Any

import pytest

from dsp_tools.commands.excel2json.project import _create_project_json
from dsp_tools.commands.excel2json.project import _validate_folder_structure_get_filenames


@pytest.fixture()
def expected_project() -> dict[str, Any]:
    with open("testdata/excel2json/excel2json-expected-output.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture()
def result_project() -> dict[str, Any]:
    excel_folder = "testdata/excel2json/excel2json_files"
    listfolder, onto_folders = _validate_folder_structure_get_filenames(excel_folder)
    _, project = _create_project_json(excel_folder, listfolder, onto_folders)
    return project


def test_same_keys(result_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    assert set(result_project["project"]) == set(expected_project["project"])


def test_lists(result_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    res_lists = sorted(result_project["project"]["lists"], key=lambda x: x["name"])
    expected_lists = sorted(expected_project["project"]["lists"], key=lambda x: x["name"])
    for r, e in zip(res_lists, expected_lists):
        assert r == e, r["name"]


def test_ontology_number(result_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    res_ontos = result_project["project"]["ontologies"]
    expected_onto = expected_project["project"]["ontologies"]
    assert len(res_ontos) == len(expected_onto) == 1


def test_properties(result_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    res_props = sorted(result_project["project"]["ontologies"][0]["properties"], key=lambda x: x["name"])
    ex_props = sorted(expected_project["project"]["ontologies"][0]["properties"], key=lambda x: x["name"])
    for r, e in zip(res_props, ex_props):
        assert r == e, r["name"]


def test_resources(result_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    res_resources = sorted(result_project["project"]["ontologies"][0]["resources"], key=lambda x: x["name"])
    ex_resources = sorted(expected_project["project"]["ontologies"][0]["resources"], key=lambda x: x["name"])
    for r, e in zip(res_resources, ex_resources):
        assert r == e, r["name"]


def test_all(result_project: dict[str, Any], expected_project: dict[str, Any]) -> None:
    assert result_project == expected_project


if __name__ == "__main__":
    pytest.main([__file__])
