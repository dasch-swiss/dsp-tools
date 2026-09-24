import dataclasses
import warnings

import numpy as np
import pandas as pd
import pytest

from dsp_tools.xmllib.internal.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.models.provenance import SourceProvenance


class TestSourceProvenance:
    def test_only_source_file_required(self) -> None:
        prov = SourceProvenance(source_file="data.xlsx")
        assert prov.source_file == "data.xlsx"
        assert prov.sheet is None
        assert prov.row is None
        assert prov.cell is None

    def test_all_fields(self) -> None:
        prov = SourceProvenance(source_file="data.xlsx", sheet="Sheet1", row=5, cell="C")
        assert prov.source_file == "data.xlsx"
        assert prov.sheet == "Sheet1"
        assert prov.row == 5
        assert prov.cell == "C"

    def test_is_frozen(self) -> None:
        prov = SourceProvenance(source_file="data.xlsx")
        with pytest.raises(dataclasses.FrozenInstanceError):
            prov.row = 6  # type: ignore[misc]


class TestSourceFileNormalisation:
    def test_non_string_is_converted(self) -> None:
        prov = SourceProvenance(source_file=123)  # type: ignore[arg-type]
        assert prov.source_file == "123"

    @pytest.mark.parametrize("value", [pd.NA, np.nan, None, "", "  "])
    def test_empty_warns_and_becomes_empty_string(self, value) -> None:
        with pytest.warns(XmllibInputWarning, match="source_file"):
            prov = SourceProvenance(source_file=value)
        assert prov.source_file == ""


class TestSheetAndCellNormalisation:
    @pytest.mark.parametrize("value", [pd.NA, np.nan, None, ""])
    def test_empty_becomes_none_without_warning(self, value) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            prov = SourceProvenance(source_file="data.xlsx", sheet=value, cell=value)
        assert prov.sheet is None
        assert prov.cell is None

    def test_non_string_is_converted(self) -> None:
        prov = SourceProvenance(source_file="data.xlsx", sheet=3, cell=0)  # type: ignore[arg-type]
        assert prov.sheet == "3"
        assert prov.cell == "0"


class TestRowNormalisation:
    @pytest.mark.parametrize("value", [5, np.int64(5), 5.0, "5", " 5 "])
    def test_integer_like_is_converted(self, value) -> None:
        prov = SourceProvenance(source_file="data.xlsx", row=value)
        assert prov.row == 5
        assert type(prov.row) is int

    @pytest.mark.parametrize("value", [pd.NA, np.nan, None, ""])
    def test_empty_becomes_none_without_warning(self, value) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            prov = SourceProvenance(source_file="data.xlsx", row=value)
        assert prov.row is None

    @pytest.mark.parametrize("value", ["abc", 5.5, True, [5]])
    def test_invalid_warns_and_becomes_none(self, value) -> None:
        with pytest.warns(XmllibInputWarning, match="row"):
            prov = SourceProvenance(source_file="data.xlsx", row=value)
        assert prov.row is None
