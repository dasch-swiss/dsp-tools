from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from dsp_tools.commands.excel2json.exceptions import InvalidFileFormatError
from dsp_tools.commands.mapping.models import ParsedClassMapping
from dsp_tools.commands.mapping.models import ParsedPropertyMapping
from dsp_tools.commands.mapping.parse_excel import _parse_mapping_sheet
from dsp_tools.commands.mapping.parse_excel import _parse_prefix_sheet
from dsp_tools.commands.mapping.parse_excel import _validate_columns
from dsp_tools.commands.mapping.parse_excel import _validate_sheets

DUMMY_PATH = Path("dummy.xlsx")


class TestValidateSheets:
    def test_all_sheets_present(self):
        sheets = {"prefix": pd.DataFrame(), "classes": pd.DataFrame(), "properties": pd.DataFrame()}
        _validate_sheets(sheets, DUMMY_PATH)

    def test_missing_one_sheet_raises(self):
        sheets = {"classes": pd.DataFrame(), "properties": pd.DataFrame()}
        with pytest.raises(InvalidFileFormatError):
            _validate_sheets(sheets, DUMMY_PATH)

    def test_missing_multiple_sheets_raises(self):
        sheets = {"prefix": pd.DataFrame()}
        with pytest.raises(InvalidFileFormatError):
            _validate_sheets(sheets, DUMMY_PATH)


class TestValidateColumns:
    def _valid_sheets(self) -> dict[str, pd.DataFrame]:
        return {
            "prefix": pd.DataFrame({"prefix": [], "link": []}),
            "classes": pd.DataFrame({"class": [], "mapping": []}),
            "properties": pd.DataFrame({"property": [], "mapping": []}),
        }

    def test_all_columns_present(self):
        _validate_columns(self._valid_sheets(), DUMMY_PATH)

    def test_missing_column_in_prefix_sheet_raises(self):
        sheets = self._valid_sheets()
        sheets["prefix"] = pd.DataFrame({"prefix": []})
        with pytest.raises(InvalidFileFormatError):
            _validate_columns(sheets, DUMMY_PATH)

    def test_missing_column_in_classes_sheet_raises(self):
        sheets = self._valid_sheets()
        sheets["classes"] = pd.DataFrame({"class": []})
        with pytest.raises(InvalidFileFormatError):
            _validate_columns(sheets, DUMMY_PATH)

    def test_missing_column_in_properties_sheet_raises(self):
        sheets = self._valid_sheets()
        sheets["properties"] = pd.DataFrame({"mapping": []})
        with pytest.raises(InvalidFileFormatError):
            _validate_columns(sheets, DUMMY_PATH)


class TestParsePrefixSheet:
    def test_returns_mapping_dict(self):
        df = pd.DataFrame(
            {"prefix": ["schema", "owl"], "link": ["http://schema.org/", "http://www.w3.org/2002/07/owl#"]}
        )
        result = _parse_prefix_sheet(df)
        assert result == {"schema": "http://schema.org/", "owl": "http://www.w3.org/2002/07/owl#"}

    def test_drops_nan_rows(self):
        df = pd.DataFrame({"prefix": ["schema", np.nan], "link": ["http://schema.org/", np.nan]})
        result = _parse_prefix_sheet(df)
        assert result == {"schema": "http://schema.org/"}


class TestParseMappingSheet:
    def test_single_mapping_per_row_class(self):
        df = pd.DataFrame({"class": ["Book"], "mapping": ["schema:Book"]})
        result = _parse_mapping_sheet(df, "class", ParsedClassMapping)
        assert len(result) == 1
        assert isinstance(result[0], ParsedClassMapping)
        assert result[0].name == "Book"
        assert result[0].prefixed_mapping_iris == ["schema:Book"]

    def test_single_mapping_per_row_property(self):
        df = pd.DataFrame({"property": ["hasTitle"], "mapping": ["schema:name"]})
        result = _parse_mapping_sheet(df, "property", ParsedPropertyMapping)
        assert len(result) == 1
        assert isinstance(result[0], ParsedPropertyMapping)
        assert result[0].name == "hasTitle"
        assert result[0].prefixed_mapping_iris == ["schema:name"]

    def test_multiple_mappings_split_by_semicolon(self):
        df = pd.DataFrame({"class": ["Book"], "mapping": ["schema:Book ; owl:Class"]})
        result = _parse_mapping_sheet(df, "class", ParsedClassMapping)
        assert result[0].prefixed_mapping_iris == ["schema:Book", "owl:Class"]

    def test_drops_nan_rows(self):
        df = pd.DataFrame({"class": ["Book", np.nan], "mapping": ["schema:Book", np.nan]})
        result = _parse_mapping_sheet(df, "class", ParsedClassMapping)
        assert len(result) == 1
