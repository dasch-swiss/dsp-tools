import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json.resources import _check_complete_gui_order


class TestCheckCompleteGuiOrder:
    def test_column_does_not_exist(self) -> None:
        df = pd.DataFrame({"prop": [1, 2, 3]})
        expected_msg = (
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "the column 'gui_order' does not exist.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected_df = pd.DataFrame({"prop": [1, 2, 3], "gui_order": [1, 2, 3]})
        with pytest.warns(Warning, match=expected_msg):
            res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_na_in_row(self) -> None:
        df = pd.DataFrame({"prop": [1, 2, 3], "gui_order": [1, 2, pd.NA]})
        expected_msg = (
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' are empty.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected_df = pd.DataFrame({"prop": [1, 2, 3], "gui_order": [1, 2, 3]})
        with pytest.warns(Warning, match=expected_msg):
            res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_error(self) -> None:
        df = pd.DataFrame({"prop": [1, 2, 3], "gui_order": [1, 2, "a"]})
        expected_msg = (
            "In the sheet 'class_name' of the file 'resources.xlsx', "
            "some rows in the column 'gui_order' contain invalid characters "
            "that could not be converted to an integer.\n"
            "Values have been filled in automatically, "
            "so that the gui-order reflects the order of the properties in the file."
        )
        expected_df = pd.DataFrame({"prop": [1, 2, 3], "gui_order": [1, 2, 3]})
        with pytest.warns(Warning, match=expected_msg):
            res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)

    def test_good(self) -> None:
        df = pd.DataFrame({"prop": [1, 2, 3], "gui_order": ["1", "2", "3"]})
        expected_df = pd.DataFrame({"prop": [1, 2, 3], "gui_order": [1, 2, 3]})
        res = _check_complete_gui_order("class_name", df)
        assert_frame_equal(res, expected_df)


if __name__ == "__main__":
    pytest.main([__file__])
