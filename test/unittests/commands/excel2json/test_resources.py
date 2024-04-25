import warnings

import pandas as pd
import pytest
import regex
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json.resources import _check_complete_gui_order
from dsp_tools.commands.excel2json.resources import _create_all_cardinalities
from dsp_tools.commands.excel2json.resources import _make_one_property


class TestCheckCompleteGuiOrder:
    def test_column_does_not_exist(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3]})
        expected_df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, 3]})
        res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_na_in_row(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, pd.NA, pd.NA]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' are empty.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected_df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, 3]})
        with pytest.warns(Warning, match=expected_msg):
            res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_error(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, "a"]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' contain invalid characters "
            "that could not be converted to an integer.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected_df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, 3]})
        with pytest.warns(Warning, match=expected_msg):
            res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_good(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "gui_order": ["1", "2", "3"]})
        expected_df = pd.DataFrame({"property": [1, 2, 3], "gui_order": [1, 2, 3]})
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)


class TestCreateAllCardinalities:
    def test_na_in_row(self) -> None:
        df = pd.DataFrame({"property": ["1", "2", "3"], "cardinality": ["1-n", "1", "0-n"], "gui_order": [1, 2, pd.NA]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' are empty.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected = [
            {"propname": ":1", "gui_order": 1, "cardinality": "1-n"},
            {"propname": ":2", "gui_order": 2, "cardinality": "1"},
            {"propname": ":3", "gui_order": 3, "cardinality": "0-n"},
        ]
        with pytest.warns(Warning, match=expected_msg):
            res = _create_all_cardinalities("class_name", df)
            assert res == expected

    def test_error(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "cardinality": ["1-n", "1", "0-n"], "gui_order": [1, 2, "a"]})
        expected_msg = regex.escape(
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' contain invalid characters "
            "that could not be converted to an integer.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected = [
            {"propname": ":1", "gui_order": 1, "cardinality": "1-n"},
            {"propname": ":2", "gui_order": 2, "cardinality": "1"},
            {"propname": ":3", "gui_order": 3, "cardinality": "0-n"},
        ]
        with pytest.warns(Warning, match=expected_msg):
            res = _create_all_cardinalities("class_name", df)
            assert res == expected

    def test_good(self) -> None:
        df = pd.DataFrame({"property": [1, 2, 3], "cardinality": ["1-n", "1", "0-n"], "gui_order": ["1", "2", "3"]})
        expected = [
            {"propname": ":1", "gui_order": 1, "cardinality": "1-n"},
            {"propname": ":2", "gui_order": 2, "cardinality": "1"},
            {"propname": ":3", "gui_order": 3, "cardinality": "0-n"},
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            res = _create_all_cardinalities("class_name", df)
            assert res == expected


def test_make_one_property() -> None:
    s = pd.Series(
        {
            "property": "1",
            "gui_order": 1,
            "cardinality": "1-n",
        }
    )
    expected = {
        "propname": ":1",
        "gui_order": 1,
        "cardinality": "1-n",
    }
    res = _make_one_property(s)
    assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
