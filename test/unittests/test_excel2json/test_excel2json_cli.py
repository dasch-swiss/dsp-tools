import json
import unittest
from pathlib import Path


class TestExcel2JsonCli(unittest.TestCase):
    testdata_tmp = Path("testdata/tmp")

    def test_excel_to_json_list(self) -> None:
        """The unit tests test only if the deepest nested nodes are correct, and if the length of the list is correct"""
        excel_folder = Path("testdata/excel2json/lists-multilingual")
        out_file = self.testdata_tmp / "_lists-out.json"
        self._make_cli_call(f"dsp-tools excel2lists {excel_folder.absolute()} {out_file.absolute()}")
        with open(out_file, encoding="utf-8") as f:
            output_actual = json.load(f)
        with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertListEqual(output_actual, output_expected)
        out_file.unlink()
