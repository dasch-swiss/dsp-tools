import json
from pathlib import Path
from typing import Any
from typing import cast

import pytest

from dsp_tools.commands.excel2json.new_lists import new_excel2lists


@pytest.fixture()
def result_lists_correct() -> list[dict[str, Any]]:
    list_dict, _ = new_excel2lists(Path("testdata/excel2json/new_excel2json_files/lists"))
    return list_dict


@pytest.fixture()
def expected_lists() -> list[dict[str, Any]]:
    with open("testdata/excel2json/new-lists-output-expected.json", encoding="utf-8") as f:
        expected = json.load(f)
        return cast(list[dict[str, Any]], expected)


def test_number_of_lists(expected_lists: list[dict[str, Any]], result_lists_correct: list[dict[str, Any]]) -> None:
    assert len(result_lists_correct) == len(expected_lists)


def test_identical_lists(expected_lists: list[dict[str, Any]], result_lists_correct: list[dict[str, Any]]) -> None:
    assert result_lists_correct == expected_lists


def test_first_list(expected_lists: list[dict[str, Any]], result_lists_correct: list[dict[str, Any]]) -> None:
    assert result_lists_correct[0] == expected_lists[0]


def test_second_list(expected_lists: list[dict[str, Any]], result_lists_correct: list[dict[str, Any]]) -> None:
    assert result_lists_correct[1] == expected_lists[1]


def test_thrid_list(expected_lists: list[dict[str, Any]], result_lists_correct: list[dict[str, Any]]) -> None:
    assert result_lists_correct[2] == expected_lists[2]


if __name__ == "__main__":
    pytest.main([__file__])
