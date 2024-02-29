import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dsp_tools.utils.xml_validation_models import InconsistentTextValueEncodings
from dsp_tools.utils.xml_validation_models import TextValueData
from dsp_tools.utils.xml_validation_models import _make_msg_for_one_resource
from dsp_tools.utils.xml_validation_models import _make_msg_from_df


class TestInvalidTextValueEncodings:
    def test_get_problems_as_df(self) -> None:
        problems = InconsistentTextValueEncodings(
            [
                TextValueData("id1", ":simple", {"utf8", "xml"}),
                TextValueData("id1", ":rich", {"utf8", "xml"}),
                TextValueData("id2", ":rich", {"utf8", "xml"}),
            ]
        )
        expected_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1", "id2"],
                "Property Name": [":rich", ":simple", ":rich"],
            }
        )
        res_df = problems._get_problems_as_df()
        assert_frame_equal(res_df, expected_df)

    def test_make_msg_for_one_resource(self) -> None:
        test_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1"],
                "Property Name": [":rich", ":simple"],
            }
        )
        res = _make_msg_for_one_resource("id1", test_df)
        expected = "Resource ID: 'id1'\n" "    - Property Name: ':rich'\n" "    - Property Name: ':simple'"
        assert res == expected

    def test_make_msg_from_df(self) -> None:
        test_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1", "id2", "id3"],
                "Property Name": [":rich", ":simple", ":rich", ":mixed"],
            }
        )
        res = _make_msg_from_df(test_df)
        expected = (
            "Resource ID: 'id1'\n"
            "    - Property Name: ':rich'\n"
            "    - Property Name: ':simple'"
            "\n----------------------------\n"
            "Resource ID: 'id2'\n"
            "    - Property Name: ':rich'"
            "\n----------------------------\n"
            "Resource ID: 'id3'\n"
            "    - Property Name: ':mixed'"
        )
        assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
