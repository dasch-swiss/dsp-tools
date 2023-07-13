import json
import unittest

import pytest

from dsp_tools.utils.update_text_props import update_text_properties


class TestUpdateTextProp(unittest.TestCase):
    base_file = "testdata/update-text-prop/update-text-prop.json"
    expected_file = "testdata/update-text-prop/update-text-prop-expected.json"
    output_file = "testdata/update-text-prop/update-text-prop_updated.json"

    def test_update_text_prop(self) -> None:
        success = update_text_properties(self.base_file)
        self.assertTrue(success)

        with open(self.output_file, encoding="utf-8") as json_file:
            updated = json.load(json_file)
        with open(self.expected_file, encoding="utf-8") as json_file:
            expected = json.load(json_file)
        self.assertDictEqual(updated, expected)


if __name__ == "__main__":
    pytest.main([__file__])
