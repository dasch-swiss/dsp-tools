

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
def list_one_child() -> dict[str, Any]:
    return {
        "name": "secondList",
        "labels": {"en": "List 2"},
        "comments": {"en": "This is the second list"},
        "nodes": [{"name": "l2_n1", "labels": {"en": "Node 1"}}],
    }


@pytest.fixture
def node_no_comments() -> dict[str, Any]:
    return {
        "name": "node_no_comments",
        "labels": {"en": "List 2", "de": "Liste 2"},
    }


def test_parse_list_section(list_many_children, list_one_child):
    result = parse_list_section([list_one_child, list_many_children])
    assert isinstance(result, list)
    assert len(result) == 2
    list_names = {x.list_info.name for x in result}
    assert list_names == {"firstList", "secondList"}


def test_parse_node_info(list_many_children):
    result = _parse_node_info(list_many_children)
    assert result.name == "firstList"
    assert result.labels == list_many_children["labels"]
    assert result.comments == list_many_children["comments"]


def test_parse_node_info_no_comments(node_no_comments):
    result = _parse_node_info(node_no_comments)
    assert result.name == "node_no_comments"
    assert result.labels == node_no_comments["labels"]
    assert not result.comments


def test_parse_one_list_many_children(list_many_children):
    result = _parse_one_list(list_many_children)
    assert result.list_info.name == "firstList"
    assert result.list_info.labels == {"en": "List 1"}
    assert result.list_info.comments == {"en": "This is the first list"}

    assert len(result.children) == 2
    l1_n1, l1_n2 = result.children
    assert l1_n1.node_info.name == "l1_n1"
    assert l1_n1.node_info.labels == {"en": "Node 1"}
    assert l1_n2.node_info.name == "l1_n2"
    assert l1_n2.node_info.labels == {"en": "Node 2"}

    assert len(l1_n1.children) == 1
    l1_n1_1 = l1_n1.children[0]
    assert l1_n1_1.node_info.name == "l1_n1_1"
    assert l1_n1_1.node_info.labels == {"en": "Node 1.1"}

    assert len(l1_n1_1.children) == 1
    l1_n1_1_1 = l1_n1_1.children[0]
    assert l1_n1_1_1.node_info.name == "l1_n1_1_1"
    assert l1_n1_1_1.node_info.labels == {"en": "Node 1.1.1"}

    assert len(l1_n1_1_1.children) == 0
    assert len(l1_n2.children) == 0
