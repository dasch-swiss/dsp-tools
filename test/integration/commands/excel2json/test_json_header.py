import json
from pathlib import Path

import pytest

from dsp_tools.commands.excel2json.json_header import get_json_header
from dsp_tools.commands.excel2json.models.json_header import EmptyJsonHeader
from dsp_tools.commands.excel2json.models.json_header import FilledJsonHeader
from dsp_tools.commands.excel2json.models.json_header import JsonHeader


def test_get_json_header_no_file() -> None:
    test_path = Path("testdata/excel2json/excel2json_files")
    result = get_json_header(test_path)
    assert isinstance(result, EmptyJsonHeader)


@pytest.fixture()
def filled_json_header() -> JsonHeader:
    test_path = Path("testdata/excel2json/new_excel2json_files/json_header.xlsx")
    return get_json_header(test_path)


def test_is_filled_header(filled_json_header: JsonHeader) -> None:
    assert isinstance(filled_json_header, FilledJsonHeader)


def test_serialised_header(filled_json_header: JsonHeader) -> None:
    serialised_header = filled_json_header.serialise()
    with open("testdata/excel2json/new_excel2json_files/expected_json_header.json", encoding="utf-8") as f:
        expected = json.load(f)
    assert expected == serialised_header


if __name__ == "__main__":
    pytest.main([__file__])
