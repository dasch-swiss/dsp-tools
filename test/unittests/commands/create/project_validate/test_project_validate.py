
import pytest

from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedListNode
from dsp_tools.commands.create.models.parsed_project import ParsedNodeInfo
from dsp_tools.commands.create.project_validate import _check_for_duplicates_in_list_section
from dsp_tools.commands.create.project_validate import _flatten_all_lists


@pytest.fixture
def two_nested_lists_ok() -> list[ParsedList]:
    return [
        ParsedList(
            list_info=ParsedNodeInfo(name="list1", labels={"en": "List 1"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node1", labels={"en": "Node 1"}, comments=None),
                    children=[
                        ParsedListNode(
                            node_info=ParsedNodeInfo(name="node1-1", labels={"en": "node1-1"}, comments=None),
                            children=[
                                ParsedListNode(
                                    node_info=ParsedNodeInfo(
                                        name="node1-1-1", labels={"en": "node1-1-1"}, comments=None
                                    ),
                                    children=[
                                        ParsedListNode(
                                            node_info=ParsedNodeInfo(
                                                name="node1-1-1-1", labels={"en": "node1-1-1-1"}, comments=None
                                            ),
                                            children=[],
                                        )
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
        ParsedList(
            list_info=ParsedNodeInfo(name="list2", labels={"en": "List 2"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node2-1", labels={"en": "Node 2-1"}, comments=None), children=[]
                ),
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node2-2", labels={"en": "Node 2-2"}, comments=None),
                    children=[
                        ParsedListNode(
                            node_info=ParsedNodeInfo(name="node2-2-1", labels={"en": "Node 2-2-1"}, comments=None),
                            children=[],
                        )
                    ],
                ),
            ],
        ),
    ]


@pytest.fixture
def two_flat_lists_one_duplicate() -> list[ParsedList]:
    return [
        ParsedList(
            list_info=ParsedNodeInfo(name="list1", labels={"en": "List 1"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node1-1", labels={"en": "Node 1-1"}, comments=None), children=[]
                ),
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node1-2", labels={"en": "Node 1-2"}, comments=None), children=[]
                ),
            ],
        ),
        ParsedList(
            list_info=ParsedNodeInfo(name="list2", labels={"en": "List 2"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node2-1", labels={"en": "Node 2-1"}, comments=None), children=[]
                ),
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node1-1", labels={"en": "Node 1-1"}, comments=None), children=[]
                ),
            ],
        ),
    ]


@pytest.fixture
def two_nested_lists_two_duplicates() -> list[ParsedList]:
    return [
        ParsedList(
            list_info=ParsedNodeInfo(name="list1", labels={"en": "List 1"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node1-1", labels={"en": "Node 1-1"}, comments=None), children=[]
                ),
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node1-2", labels={"en": "Node 1-2"}, comments=None),
                    children=[
                        ParsedListNode(
                            node_info=ParsedNodeInfo(name="node1-2-1", labels={"en": "Node 1-2-1"}, comments=None),
                            children=[],
                        )
                    ],
                ),
            ],
        ),
        ParsedList(
            list_info=ParsedNodeInfo(name="list2", labels={"en": "List 2"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node2-1", labels={"en": "Node 2-1"}, comments=None), children=[]
                ),
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node1-2-1", labels={"en": "Node 1-2-1"}, comments=None),
                    children=[
                        ParsedListNode(
                            node_info=ParsedNodeInfo(name="node1-2", labels={"en": "Node 1-2"}, comments=None),
                            children=[],
                        )
                    ],
                ),
            ],
        ),
    ]


@pytest.fixture
def two_lists_duplicate_list_names() -> list[ParsedList]:
    return [
        ParsedList(
            list_info=ParsedNodeInfo(name="duplicate_list", labels={"en": "Duplicate List"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node1-1", labels={"en": "Node 1-1"}, comments=None), children=[]
                )
            ],
        ),
        ParsedList(
            list_info=ParsedNodeInfo(name="duplicate_list", labels={"en": "Duplicate List"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="node2-1", labels={"en": "Node 2-1"}, comments=None), children=[]
                )
            ],
        ),
    ]


@pytest.fixture
def list_with_duplicate_list_name_and_node_name() -> list[ParsedList]:
    return [
        ParsedList(
            list_info=ParsedNodeInfo(name="duplicate_list", labels={"en": "Duplicate List"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="duplicate_node", labels={"en": "Duplicate Node"}, comments=None),
                    children=[],
                )
            ],
        ),
        ParsedList(
            list_info=ParsedNodeInfo(name="duplicate_list", labels={"en": "Duplicate List"}, comments=None),
            children=[
                ParsedListNode(
                    node_info=ParsedNodeInfo(name="duplicate_node", labels={"en": "Duplicate Node"}, comments=None),
                    children=[],
                )
            ],
        ),
    ]


def test_(two_nested_lists_ok):
    result = _flatten_all_lists(two_nested_lists_ok)
    expected = {"node1", "node1-1", "node1-1-1", "node1-1-1-1", "node2-1", "node2-2", "node2-2-1"}
    assert len(result) == len(expected)
    assert set(result) == expected


def test_check_for_duplicates_ok_nested(two_nested_lists_ok):
    result = _check_for_duplicates_in_list_section(two_nested_lists_ok)
    assert result is None


def test_check_for_duplicates_flat_one_duplicate(two_flat_lists_one_duplicate):
    result = _check_for_duplicates_in_list_section(two_flat_lists_one_duplicate)
    assert result is not None
    assert len(result.problems) == 1
    assert "node1-1" in result.problems[0].problematic_object


def test_check_for_duplicates_nested_two_duplicates(two_nested_lists_two_duplicates):
    result = _check_for_duplicates_in_list_section(two_nested_lists_two_duplicates)
    assert result is not None
    assert len(result.problems) == 2
    problematic_objects = {problem.problematic_object for problem in result.problems}
    assert any("node1-2" in obj for obj in problematic_objects)
    assert any("node1-2-1" in obj for obj in problematic_objects)


def test_check_for_duplicates_duplicate_list_names(two_lists_duplicate_list_names):
    result = _check_for_duplicates_in_list_section(two_lists_duplicate_list_names)
    assert result is not None
    assert len(result.problems) == 1
    assert "duplicate_list" in result.problems[0].problematic_object


def test_check_for_duplicates_both_list_and_node_duplicates(
    list_with_duplicate_list_name_and_node_name,
):
    result = _check_for_duplicates_in_list_section(list_with_duplicate_list_name_and_node_name)
    assert result is not None
    assert len(result.problems) == 2
    problematic_objects = {problem.problematic_object for problem in result.problems}
    assert any("duplicate_list" in obj for obj in problematic_objects)
    assert any("duplicate_node" in obj for obj in problematic_objects)
