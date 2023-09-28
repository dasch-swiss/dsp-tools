import json
import unittest
from pathlib import Path

import pytest

from dsp_tools.utils.update_text_props import update_text_properties


class TestUpdateTextProp(unittest.TestCase):
    """
    Tests for the update script that migrates old JSON project definition files to the new format,
    where text properties are represented by "UnformattedTextValue" and "FormattedTextValue".
    """

    base_file = Path("testdata/update-text-prop/update-text-prop.json")
    expected_file = Path("testdata/update-text-prop/update-text-prop-expected.json")
    output_file = Path("testdata/update-text-prop/update-text-prop_updated.json")

    def test_update_text_prop(self) -> None:
        """
        test if the update script's output file matches the expected output file
        """
        success = update_text_properties(self.base_file)
        self.assertTrue(success)

        with open(self.output_file, encoding="utf-8") as json_file:
            updated = json.load(json_file)
        with open(self.expected_file, encoding="utf-8") as json_file:
            expected = json.load(json_file)
        self.assertDictEqual(updated, expected)

        if self.output_file.exists():
            self.output_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
