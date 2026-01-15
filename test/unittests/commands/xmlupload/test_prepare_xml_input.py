# mypy: disable-error-code="no-untyped-def"
import pytest

from dsp_tools.clients.list_client import ListInfo
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import _reformat_all_lists
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import _reformat_one_list


@pytest.fixture
def nested_list() -> ListInfo:
    return ListInfo(
        {
            "id": "http://www.example.org/lists#a",
            "name": "list-a",
        },
        [
            {
                "id": "http://www.example.org/lists#a1",
                "name": "node-a1",
                "children": [
                    {
                        "id": "http://www.example.org/lists#a1.1",
                        "name": "node-a1.1",
                    },
                    {
                        "id": "http://www.example.org/lists#a1.2",
                        "name": "node-a1.2",
                        "children": [
                            {
                                "id": "http://www.example.org/lists#a1.2.1",
                                "name": "node-a1.2.1",
                            }
                        ],
                    },
                ],
            },
            {
                "id": "http://www.example.org/lists#a2",
                "name": "node-a2",
            },
        ],
    )


@pytest.fixture
def reformatted_nested_list() -> dict[tuple[str, str], str]:
    return {
        ("list-a", "list-a"): "http://www.example.org/lists#a",
        ("list-a", "node-a1"): "http://www.example.org/lists#a1",
        ("list-a", "node-a1.1"): "http://www.example.org/lists#a1.1",
        ("list-a", "node-a1.2"): "http://www.example.org/lists#a1.2",
        ("list-a", "node-a1.2.1"): "http://www.example.org/lists#a1.2.1",
        ("list-a", "node-a2"): "http://www.example.org/lists#a2",
        ("", "http://www.example.org/lists#a"): "http://www.example.org/lists#a",
        ("", "http://www.example.org/lists#a1"): "http://www.example.org/lists#a1",
        ("", "http://www.example.org/lists#a1.1"): "http://www.example.org/lists#a1.1",
        ("", "http://www.example.org/lists#a1.2"): "http://www.example.org/lists#a1.2",
        ("", "http://www.example.org/lists#a1.2.1"): "http://www.example.org/lists#a1.2.1",
        ("", "http://www.example.org/lists#a2"): "http://www.example.org/lists#a2",
    }


@pytest.fixture
def flat_list() -> ListInfo:
    return ListInfo(
        {
            "id": "http://www.example.org/lists#b",
            "name": "list-b",
        },
        [
            {"id": "http://www.example.org/lists#b1", "name": "node-b1"},
            {"id": "http://www.example.org/lists#b2", "name": "node-b2"},
        ],
    )


@pytest.fixture
def reformatted_flat_list() -> dict[tuple[str, str], str]:
    return {
        ("list-b", "list-b"): "http://www.example.org/lists#b",
        ("list-b", "node-b1"): "http://www.example.org/lists#b1",
        ("list-b", "node-b2"): "http://www.example.org/lists#b2",
        ("", "http://www.example.org/lists#b"): "http://www.example.org/lists#b",
        ("", "http://www.example.org/lists#b1"): "http://www.example.org/lists#b1",
        ("", "http://www.example.org/lists#b2"): "http://www.example.org/lists#b2",
    }


def test_reformat_all_lists(flat_list, nested_list, reformatted_flat_list, reformatted_nested_list):
    result = _reformat_all_lists([flat_list, nested_list])
    combined = {**reformatted_flat_list, **reformatted_nested_list}
    assert result == combined


def test_reformat_flat_list(flat_list, reformatted_flat_list):
    result = _reformat_one_list(flat_list)
    assert result == reformatted_flat_list


def test_reformat_nested_list(nested_list, reformatted_nested_list):
    result = _reformat_one_list(nested_list)
    assert result == reformatted_nested_list


def test_reformat_list_no_children():
    list_input = ListInfo(
        {
            "id": "http://www.example.org/lists#c",
            "name": "list-c",
        },
        [],
    )
    result = _reformat_one_list(list_input)
    expected = {
        ("list-c", "list-c"): "http://www.example.org/lists#c",
        ("", "http://www.example.org/lists#c"): "http://www.example.org/lists#c",
    }
    assert result == expected
