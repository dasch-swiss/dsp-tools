from typing import Any

import pytest

from dsp_tools.commands.create.parsing.parse_lists import _parse_node_info
from dsp_tools.commands.create.parsing.parse_lists import _parse_one_list
from dsp_tools.commands.create.parsing.parse_lists import parse_list_section


@pytest.fixture
def list_many_children() -> dict[str, Any]:
    return {
        "name": "firstList",
        "labels": {"en": "List 1"},
        "comments": {"en": "This is the first list"},
        "nodes": [
            {
                "name": "l1_n1",
                "labels": {"en": "Node 1"},
                "nodes": [
                    {
                        "name": "l1_n1_1",
                        "labels": {"en": "Node 1.1"},
                        "nodes": [{"name": "l1_n1_1_1", "labels": {"en": "Node 1.1.1"}}],
                    }
                ],
            },
            {"name": "l1_n2", "labels": {"en": "Node 2"}},
        ],
    }


@pytest.fixture
def list_no_children() -> dict[str, Any]:
    return {
        "name": "ListNoNodes",
        "labels": {"en": "List 2", "de": "Liste 2"},
        "comments": {"en": "This a list", "de": "With two comments"},
    }


@pytest.fixture
def node_no_comments() -> dict[str, Any]:
    return {
        "name": "node_no_comments",
        "labels": {"en": "List 2", "de": "Liste 2"},
        "comments": {"en": "This a list", "de": "With two comments"},
    }


def test_parse_list_section(list_many_children, list_no_children):
    result = parse_list_section([list_no_children, list_many_children])
    assert len(result) == 2
    list_names = {x.list_info.name for x in result}
    assert list_names == {"firstList", "ListNoNodes"}


def test_parse_node_info(list_no_children):
    result = _parse_node_info(list_no_children)
    assert result.name == "ListNoNodes"
    assert result.labels == list_no_children["labels"]
    assert result.comments == list_no_children["comments"]


def test_parse_node_info_no_comments(node_no_comments):
    result = _parse_node_info(node_no_comments)
    assert result.name == "node_no_comments"
    assert result.labels == node_no_comments["labels"]
    assert not result.comments


def test_parse_one_list_many_children(list_many_children):
    result = _parse_one_list(list_many_children)
    # TODO: make assertions


def test_parse_one_list_no_children(list_no_children):
    result = _parse_one_list(list_no_children)
    # TODO: make assertions
