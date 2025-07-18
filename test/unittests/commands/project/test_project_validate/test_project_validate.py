from typing import Any

import pytest

from dsp_tools.commands.project.create.project_validate import _find_duplicate_listnodes


@pytest.fixture
def two_flat_lists_ok() -> list[dict[str, Any]]:
    return [
        {"name": "list1", "nodes": [{"name": "node1-1"}, {"name": "node1-2"}]},
        {"name": "list2", "nodes": [{"name": "node2-1"}, {"name": "node2-2"}]},
    ]


@pytest.fixture
def two_nested_lists_ok() -> list[dict[str, Any]]:
    return [
        {"name": "list1", "nodes": [{"name": "node1-1"}, {"name": "node1-2", "nodes": [{"name": "node1-2-1"}]}]},
        {"name": "list2", "nodes": [{"name": "node2-1"}, {"name": "node2-2", "nodes": [{"name": "node2-2-1"}]}]},
    ]


@pytest.fixture
def two_flat_lists_one_duplicate() -> list[dict[str, Any]]:
    return [
        {"name": "list1", "nodes": [{"name": "node1-1"}, {"name": "node1-2"}]},
        {"name": "list2", "nodes": [{"name": "node2-1"}, {"name": "node1-1"}]},
    ]


@pytest.fixture
def two_nested_lists_two_duplicates() -> list[dict[str, Any]]:
    return [
        {"name": "list1", "nodes": [{"name": "node1-1"}, {"name": "node1-2", "nodes": [{"name": "node1-2-1"}]}]},
        {"name": "list2", "nodes": [{"name": "node2-1"}, {"name": "node1-2-1", "nodes": [{"name": "node1-2"}]}]},
    ]


def test_find_duplicate_listnodes_ok_flat(two_flat_lists_ok: list[dict[str, Any]]) -> None:
    assert not _find_duplicate_listnodes(two_flat_lists_ok)


def test_find_duplicate_listnodes_ok_nested(two_nested_lists_ok: list[dict[str, Any]]) -> None:
    assert not _find_duplicate_listnodes(two_nested_lists_ok)


def test_find_duplicate_listnodes_flat_one_duplicate(two_flat_lists_one_duplicate: list[dict[str, Any]]) -> None:
    expected: set[str] = {"node1-1"}
    assert _find_duplicate_listnodes(two_flat_lists_one_duplicate) == expected


def test_find_duplicate_listnodes_nested_two_duplicates(two_nested_lists_two_duplicates: list[dict[str, Any]]) -> None:
    expected: set[str] = {"node1-2", "node1-2-1"}
    assert _find_duplicate_listnodes(two_nested_lists_two_duplicates) == expected
