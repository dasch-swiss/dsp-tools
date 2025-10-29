from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.lists_only import create_lists_only
from dsp_tools.commands.project.create.project_create_all import create_project
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers


@pytest.fixture(scope="module")
def container_ports() -> Iterator[ExternalContainerPorts]:
    with get_containers() as metadata:
        yield metadata.ports


@pytest.fixture(scope="module")
def creds(container_ports: ExternalContainerPorts) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_ports.api}",
        f"http://0.0.0.0:{container_ports.ingest}",
    )


@pytest.fixture(scope="module")
def _create_project_0003(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/json-project/create-project-no-lists-0003.json"), creds)


@pytest.fixture(scope="module")
def _create_lists_only(_create_project_0003: None, creds: ServerCredentials) -> None:
    assert create_lists_only(Path("testdata/json-project/create-project-0003.json"), creds)


@pytest.fixture(scope="module")
def _get_created_lists(_create_lists_only, creds: ServerCredentials) -> dict[str, Any]:
    url = f"{creds.server}/admin/lists?projectShortcode=0003"
    response = requests.get(url, timeout=10)
    assert response.status_code == 200, f"Failed to get lists: {response.status_code} {response.text}"
    return response.json()


def test_all_lists_created(_get_created_lists):
    assert "lists" in _get_created_lists, f"Response missing 'lists' key: {_get_created_lists}"
    lists = _get_created_lists["lists"]
    assert len(lists) == 2, f"Expected 2 lists but got {len(lists)}: {lists}"


def test_list_one(_get_created_lists, creds):
    lists = sorted(_get_created_lists, key=lambda x: x["name"])
    first_list = lists[0]
    assert first_list["name"] == "firstList", f"Expected 'firstList' but got '{first_list['name']}'"
    assert "id" in first_list, f"List missing 'id': {first_list}"
    first_list_iri = first_list["id"]

    # request all the nodes of the list
    encoded_first_list_iri = quote_plus(first_list_iri)
    first_list_detail_response = requests.get(f"{creds.server}/admin/lists/{encoded_first_list_iri}", timeout=30)
    assert first_list_detail_response.status_code == 200, (
        f"Failed to get first list details: {first_list_detail_response.status_code} {first_list_detail_response.text}"
    )
    first_list_detail = first_list_detail_response.json()
    assert "list" in first_list_detail, f"Response missing 'list' key: {first_list_detail}"

    first_list_info = first_list_detail["list"]["listinfo"]
    assert first_list_info["name"] == "firstList"
    assert "id" in first_list_info

    first_list_children = first_list_detail["list"]["children"]
    first_list_all_nodes = _collect_all_nodes(first_list_children)
    assert len(first_list_all_nodes) == 4, (
        f"Expected 4 nodes in firstList but got {len(first_list_all_nodes)}: {first_list_all_nodes}"
    )

    first_list_node_names = {node["name"] for node in first_list_all_nodes}
    expected_names = {"l1_n1", "l1_n1_1", "l1_n1_1_1", "l1_n2"}
    assert first_list_node_names == expected_names, (
        f"Node names don't match. Expected: {expected_names} but got: {first_list_node_names}"
    )

    for node in first_list_all_nodes:
        assert "id" in node, f"Node missing 'id': {node}"
        assert node["id"], f"Node has empty 'id': {node}"


def test_list_two(_get_created_lists, creds) -> None:
    second_list = _get_created_lists[1]
    assert second_list["name"] == "secondList", f"Expected 'secondList' but got '{second_list['name']}'"
    assert "id" in second_list, f"List missing 'id': {second_list}"
    second_list_iri = second_list["id"]

    # request all the nodes of the list
    encoded_second_list_iri = quote_plus(second_list_iri)
    second_list_detail_response = requests.get(f"{creds.server}/admin/lists/{encoded_second_list_iri}", timeout=30)
    assert second_list_detail_response.status_code == 200, (
        f"Failed to get second list details: "
        f"{second_list_detail_response.status_code} {second_list_detail_response.text}"
    )
    second_list_detail = second_list_detail_response.json()
    assert "list" in second_list_detail, f"Response missing 'list' key: {second_list_detail}"

    second_list_info = second_list_detail["list"]["listinfo"]
    assert second_list_info["name"] == "secondList"
    assert "id" in second_list_info

    second_list_children = second_list_detail["list"]["children"]
    second_list_all_nodes = _collect_all_nodes(second_list_children)
    assert len(second_list_all_nodes) == 1, (
        f"Expected 1 node in secondList but got {len(second_list_all_nodes)}: {second_list_all_nodes}"
    )

    assert second_list_all_nodes[0]["name"] == "l2n1", (
        f"Expected node name 'l2n1' but got '{second_list_all_nodes[0]['name']}'"
    )
    assert "id" in second_list_all_nodes[0], f"Node missing 'id': {second_list_all_nodes[0]}"


def _collect_all_nodes(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Recursively collect all nodes from a list's children."""
    all_nodes = []
    for child in children:
        all_nodes.append(child)
        if "children" in child:
            all_nodes.extend(_collect_all_nodes(child["children"]))
    return all_nodes
