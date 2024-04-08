import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json.new_lists import _fill_ids
from dsp_tools.commands.excel2json.new_lists import _make_single_node


def test_make_single_node() -> None:
    test_series = pd.Series(
        {
            "ID (optional)": "id",
            "en_1": "en_1_lbl",
            "de_1": "de_1_lbl",
            "en_2": "en_2_lbl",
            "de_2": "de_2_lbl",
        }
    )
    res = _make_single_node(test_series, 1)
    assert res._id == "id"
    assert res.labels == {"en": "en_1_lbl", "de": "de_1_lbl"}


def test_fill_ids() -> None:
    test_df = pd.DataFrame(
        {
            "ID (optional)": ["id1", pd.NA, "id3"],
            "en": ["en1", "en2", "en3"],
        }
    )
    expected = pd.DataFrame(
        {
            "ID (optional)": ["id1", "en2", "id3"],
            "en": ["en1", "en2", "en3"],
        }
    )
    res = _fill_ids(test_df)
    assert_frame_equal(res, expected)


if __name__ == "__main__":
    pytest.main([__file__])
