import json
from pathlib import Path

import pytest
import regex

from dsp_tools.commands.excel2json.json_header import get_json_header
from dsp_tools.commands.excel2json.models.json_header import EmptyJsonHeader
from dsp_tools.commands.excel2json.models.json_header import FilledJsonHeader
from dsp_tools.commands.excel2json.models.json_header import JsonHeader
from dsp_tools.error.exceptions import InputError


@pytest.fixture
def filled_json_header() -> JsonHeader:
    test_path = Path("testdata/excel2json/excel2json_files/json_header.xlsx")
    return get_json_header(test_path)


def test_get_json_header_no_file() -> None:
    test_path = Path("testdata/excel2json/old_excel2json_files")
    result = get_json_header(test_path)
    assert isinstance(result, EmptyJsonHeader)


def test_is_filled_header(filled_json_header: JsonHeader) -> None:
    assert isinstance(filled_json_header, FilledJsonHeader)


def test_serialised_header(filled_json_header: JsonHeader) -> None:
    serialised_header = filled_json_header.to_dict()
    with open("testdata/excel2json/expected_json_header.json", encoding="utf-8") as f:
        expected = json.load(f)
    assert expected == serialised_header


def test_to_dict_json_header_invalid_missing_sheet() -> None:
    test_path = Path("testdata/invalid-testdata/excel2json/json_header_missing_sheet.xlsx")
    expected = regex.escape(
        "The Excel file 'json_header.xlsx' contains the following problems:\n\n"
        "The following sheet(s) are mandatory and may not be empty:\n"
        "    - keywords"
    )
    with pytest.raises(InputError, match=expected):
        get_json_header(test_path)


def test_to_dict_json_header_invalid_empty_sheet() -> None:
    test_path = Path("testdata/invalid-testdata/excel2json/json_header_empty_sheet.xlsx")
    expected = regex.escape(
        "The Excel file 'json_header.xlsx' contains the following problems:\n\n"
        "The sheet 'description' has the following problems:\n\n"
        "At least one value is required in the columns: "
        "description_de, description_en, description_fr, description_it, description_rm\n"
        "Row 2 does not contain any values in those columns."
    )
    with pytest.raises(InputError, match=expected):
        get_json_header(test_path)


if __name__ == "__main__":
    pytest.main([__file__])
