import json
from pathlib import Path
from typing import Any
from typing import cast

import pytest
import regex

from dsp_tools.commands.excel2json.new_lists.make_new_lists import new_excel2lists
from dsp_tools.models.exceptions import InputError


@pytest.fixture()
def result_lists_correct() -> list[dict[str, Any]]:
    all_lists, _ = new_excel2lists(Path("testdata/excel2json/new_excel2json_files/lists"))
    all_lists = sorted(all_lists, key=lambda x: x["name"])
    return all_lists


@pytest.fixture()
def expected_lists() -> list[dict[str, Any]]:
    with open("testdata/excel2json/new-lists-output-expected.json", encoding="utf-8") as f:
        expected = json.load(f)
        return cast(list[dict[str, Any]], expected)


def test_number_of_lists(result_lists_correct: list[dict[str, Any]]) -> None:
    assert len(result_lists_correct) == 3


def test_first_list(expected_lists: list[dict[str, Any]], result_lists_correct: list[dict[str, Any]]) -> None:
    assert result_lists_correct[0] == expected_lists[0]


def test_second_list(expected_lists: list[dict[str, Any]], result_lists_correct: list[dict[str, Any]]) -> None:
    assert result_lists_correct[1] == expected_lists[1]


def test_third_list(expected_lists: list[dict[str, Any]], result_lists_correct: list[dict[str, Any]]) -> None:
    assert result_lists_correct[2] == expected_lists[2]


def test_duplicate_problems() -> None:
    expected = regex.escape(
        "\nThe excel file(s) used to create the list section have the following problem(s):"
        "\n\n---------------------------------------\n\n"
        "No duplicates are allowed in the 'ID (optional)' column. "
        "At the following locations, IDs are duplicated:"
        "\n----------------------------\n"
        "ID: 'duplicateID'\n"
        "    - Excel 'testdata/invalid-testdata/excel2json/new_lists_duplicate_ids/list_duplicate_1.xlsx' "
        "| Sheet 'duplicate_list_id1' | Row 2\n"
        "    - Excel 'testdata/invalid-testdata/excel2json/new_lists_duplicate_ids/list_duplicate_2.xlsx' "
        "| Sheet 'duplicate_list_id2' | Row 2"
        "\n----------------------------\n"
        "ID: 'duplicate_node_id'\n"
        "    - Excel 'testdata/invalid-testdata/excel2json/new_lists_duplicate_ids/list_duplicate_2.xlsx' "
        "| Sheet 'duplicate_node_id1' | Row 3\n"
        "    - Excel 'testdata/invalid-testdata/excel2json/new_lists_duplicate_ids/list_duplicate_2.xlsx' "
        "| Sheet 'duplicate_node_id2' | Row 3"
    )
    with pytest.raises(InputError, match=expected):
        new_excel2lists(Path("testdata/invalid-testdata/excel2json/new_lists_duplicate_ids"))


def test_invalid_shape() -> None:
    expected = "asdf"
    with pytest.raises(InputError, match=expected):
        new_excel2lists(Path("testdata/invalid-testdata/excel2json/new_lists_duplicate_listname"))


def test_invalid_shape() -> None:
    expected = "asdf"
    with pytest.raises(InputError, match=expected):
        new_excel2lists(Path("testdata/invalid-testdata/excel2json/new_lists_invalid_shape"))


def test_missing_translation() -> None:
    expected = "asdf"
    with pytest.raises(InputError, match=expected):
        new_excel2lists(Path("testdata/invalid-testdata/excel2json/new_lists_missing_translations"))


if __name__ == "__main__":
    pytest.main([__file__])
