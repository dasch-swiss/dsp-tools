from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.create import create
from dsp_tools.commands.create.lists_only import create_lists_only


@pytest.fixture(scope="module")
def _create_project_0003(creds: ServerCredentials):
    assert create(Path("testdata/json-project/create-project-no-lists-0003.json"), creds, False)


@pytest.fixture(scope="module")
def _create_lists_only(_create_project_0003: None, creds: ServerCredentials):
    assert create_lists_only(Path("testdata/json-project/create-project-0003.json"), creds)


@pytest.fixture(scope="module")
def created_lists(_create_lists_only: None, creds: ServerCredentials):
    url = f"{creds.server}/admin/lists?projectShortcode=0003"
    response = requests.get(url, timeout=10)
    assert response.status_code == 200, f"Failed to get lists: {response.status_code} {response.text}"
    data = response.json()
    assert "lists" in data, f"Response missing 'lists' key: {data}"
    return data["lists"]


@pytest.mark.usefixtures("_create_lists_only")
def test_do_not_crash_if_lists_exist(creds: ServerCredentials):
    assert create_lists_only(Path("testdata/json-project/create-project-0003.json"), creds)


def test_all_lists_created(created_lists):
    assert len(created_lists) == 2, f"Expected 2 lists but got {len(created_lists)}: {created_lists}"


def test_list_one(created_lists, creds):
    lists = sorted(created_lists, key=lambda x: x["name"])
    first_list = lists[0]
    assert first_list["name"] == "firstList"
    assert "id" in first_list
    first_list_iri = first_list["id"]

    # request all the nodes of the list
    encoded_first_list_iri = quote_plus(first_list_iri)
    first_list_detail_response = requests.get(f"{creds.server}/admin/lists/{encoded_first_list_iri}", timeout=30)
    assert first_list_detail_response.status_code == 200
    first_list_detail = first_list_detail_response.json()
    assert "list" in first_list_detail

    first_list_info = first_list_detail["list"]["listinfo"]
    assert first_list_info["name"] == "firstList"
    assert "id" in first_list_info

    first_list_children = first_list_detail["list"]["children"]
    first_list_all_nodes = _collect_all_nodes(first_list_children)
    assert len(first_list_all_nodes) == 4

    first_list_node_names = {node["name"] for node in first_list_all_nodes}
    expected_names = {"l1_n1", "l1_n1_1", "l1_n1_1_1", "l1_n2"}
    assert first_list_node_names == expected_names
    for node in first_list_all_nodes:
        assert node["id"]


def test_list_two(created_lists, creds):
    lists = sorted(created_lists, key=lambda x: x["name"])
    second_list = lists[1]
    assert second_list["name"] == "secondList"
    assert "id" in second_list
    second_list_iri = second_list["id"]

    # request all the nodes of the list
    encoded_second_list_iri = quote_plus(second_list_iri)
    second_list_detail_response = requests.get(f"{creds.server}/admin/lists/{encoded_second_list_iri}", timeout=30)
    assert second_list_detail_response.status_code == 200
    second_list_detail = second_list_detail_response.json()
    assert "list" in second_list_detail

    second_list_info = second_list_detail["list"]["listinfo"]
    assert second_list_info["name"] == "secondList"
    assert "id" in second_list_info

    second_list_children = second_list_detail["list"]["children"]
    second_list_all_nodes = _collect_all_nodes(second_list_children)
    assert len(second_list_all_nodes) == 1

    assert second_list_all_nodes[0]["name"] == "l2n1"
    assert "id" in second_list_all_nodes[0]


def _collect_all_nodes(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Recursively collect all nodes from a list's children."""
    all_nodes = []
    for child in children:
        all_nodes.append(child)
        if "children" in child:
            all_nodes.extend(_collect_all_nodes(child["children"]))
    return all_nodes
